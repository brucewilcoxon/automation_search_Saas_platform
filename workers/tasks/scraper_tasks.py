"""
Celery tasks for scraping and data ingestion.
"""
from workers.celery_app import celery_app
from typing import Dict, Any
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import and_
from backend.app.core.database import SessionLocal
from backend.db.models.ingest_run import IngestRun
from backend.db.models.auction_event import AuctionEvent
from backend.db.models.auction_item import AuctionItem
from scrapers.adapters.factory import create_adapter


@celery_app.task(name="workers.tasks.scraper_tasks.run_ingestion_task")
def run_ingestion_task(run_id: str, state: str, county: str) -> Dict[str, Any]:
    """
    Main ingestion task that:
    1. Discovers auction events
    2. Lists auction items for each event
    3. Normalizes parcel IDs
    4. Upserts into database with idempotency
    
    Args:
        run_id: Ingest run identifier
        state: State code (e.g., 'FL')
        county: County name (e.g., 'Miami-Dade')
        
    Returns:
        Dictionary with task results
    """
    db: Session = SessionLocal()
    events_created = 0
    events_updated = 0
    items_created = 0
    items_updated = 0
    errors = 0
    
    try:
        # Update run status
        ingest_run = db.query(IngestRun).filter(IngestRun.id == run_id).first()
        if not ingest_run:
            return {"status": "error", "message": f"Ingest run {run_id} not found"}
        
        ingest_run.status = "running"
        db.commit()
        
        # Create adapter
        adapter = create_adapter(state, county)
        if not adapter:
            ingest_run.status = "failed"
            ingest_run.errors = 1
            ingest_run.completed_at = datetime.utcnow()
            db.commit()
            return {
                "status": "error",
                "message": f"No adapter found for {county}, {state}",
                "run_id": run_id
            }
        
        # Step 1: Discover auction events
        try:
            events_data = adapter.discover_auction_events()
        except Exception as e:
            errors += 1
            ingest_run.errors = errors
            db.commit()
            raise Exception(f"Failed to discover events: {str(e)}")
        
        total_items = 0
        
        # Step 2: Process each event
        for event_data in events_data:
            try:
                event_id = event_data.get('event_id')
                event_date_str = event_data.get('event_date')
                event_url = event_data.get('event_url')
                status = event_data.get('status', 'upcoming')
                raw_json = event_data.get('raw_json', {})
                
                if not event_id or not event_date_str:
                    continue
                
                # Parse event date
                from datetime import datetime as dt
                try:
                    event_date = dt.fromisoformat(event_date_str).date()
                except (ValueError, AttributeError):
                    event_date = dt.strptime(event_date_str, '%Y-%m-%d').date()
                
                # Check for existing event (idempotency: same county + date)
                existing_event = db.query(AuctionEvent).filter(
                    and_(
                        AuctionEvent.county.ilike(f"%{county}%"),
                        AuctionEvent.event_date == event_date,
                        AuctionEvent.state == state.upper()
                    )
                ).first()
                
                if existing_event:
                    # Update existing event
                    existing_event.source_url = event_url or existing_event.source_url
                    existing_event.status = status
                    existing_event.raw_json = raw_json
                    event = existing_event
                    events_updated += 1
                else:
                    # Create new event
                    event = AuctionEvent(
                        id=event_id,
                        state=state.upper(),
                        county=county,
                        event_date=event_date,
                        status=status,
                        source_url=event_url,
                        raw_json=raw_json,
                        item_count=0
                    )
                    db.add(event)
                    events_created += 1
                
                db.flush()  # Get event.id
                
                # Step 3: List auction items for this event
                if event_url:
                    try:
                        items_data = adapter.list_auction_items(event_url)
                        
                        for item_data in items_data:
                            try:
                                item_id = item_data.get('item_id')
                                parcel_id_raw = item_data.get('parcel_id_raw', '')
                                opening_bid = item_data.get('opening_bid')
                                item_status = item_data.get('status', 'available')
                                item_url = item_data.get('item_url')
                                item_raw_json = item_data.get('raw_json', {})
                                
                                if not item_id:
                                    continue
                                
                                # Normalize parcel ID
                                parcel_id_norm = adapter.normalize_parcel_id(parcel_id_raw) if parcel_id_raw else None
                                
                                # Check for existing item (idempotency: same event + normalized parcel ID)
                                existing_item = None
                                if parcel_id_norm:
                                    existing_item = db.query(AuctionItem).filter(
                                        and_(
                                            AuctionItem.event_id == event.id,
                                            AuctionItem.parcel_id_norm == parcel_id_norm
                                        )
                                    ).first()
                                
                                if existing_item:
                                    # Update existing item
                                    existing_item.parcel_id_raw = parcel_id_raw or existing_item.parcel_id_raw
                                    existing_item.opening_bid = opening_bid or existing_item.opening_bid
                                    existing_item.status = item_status
                                    existing_item.item_url = item_url or existing_item.item_url
                                    existing_item.raw_json = item_raw_json
                                    items_updated += 1
                                else:
                                    # Create new item
                                    item = AuctionItem(
                                        id=item_id,
                                        event_id=event.id,
                                        parcel_id_raw=parcel_id_raw,
                                        parcel_id_norm=parcel_id_norm,
                                        opening_bid=opening_bid,
                                        status=item_status,
                                        item_url=item_url,
                                        raw_json=item_raw_json
                                    )
                                    db.add(item)
                                    items_created += 1
                                
                                total_items += 1
                                
                            except Exception as e:
                                errors += 1
                                continue
                        
                    except Exception as e:
                        errors += 1
                        continue
                
            except Exception as e:
                errors += 1
                continue
        
        # Update event item counts
        for event_data in events_data:
            event_id = event_data.get('event_id')
            if event_id:
                event = db.query(AuctionEvent).filter(AuctionEvent.id == event_id).first()
                if event:
                    item_count = db.query(AuctionItem).filter(AuctionItem.event_id == event.id).count()
                    event.item_count = item_count
        
        # Update ingest run
        ingest_run.status = "completed"
        ingest_run.parcels_processed = total_items
        ingest_run.parcels_total = total_items
        ingest_run.errors = errors
        ingest_run.completed_at = datetime.utcnow()
        
        db.commit()
        
        return {
            "status": "success",
            "run_id": run_id,
            "events_created": events_created,
            "events_updated": events_updated,
            "items_created": items_created,
            "items_updated": items_updated,
            "total_items": total_items,
            "errors": errors
        }
        
    except Exception as e:
        # Update run status to failed
        if ingest_run:
            ingest_run.status = "failed"
            ingest_run.errors = errors + 1
            ingest_run.completed_at = datetime.utcnow()
            db.commit()
        
        return {
            "status": "error",
            "run_id": run_id,
            "message": str(e),
            "errors": errors + 1
        }
    finally:
        db.close()
