"""
Ingestion endpoints for triggering and monitoring data collection.
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime
from backend.app.core.database import get_db
from backend.db.models.ingest_run import IngestRun
from workers.tasks.scraper_tasks import run_ingestion_task

router = APIRouter()


class IngestRunRequest(BaseModel):
    """Request model for starting an ingestion run."""
    state: str
    county: str


class IngestRunResponse(BaseModel):
    """Response model for ingestion run."""
    id: str
    source: str
    status: str
    startedAt: str
    completedAt: Optional[str]
    parcelsProcessed: int
    parcelsTotal: Optional[int]
    errors: int
    
    class Config:
        from_attributes = True


class IngestStatusResponse(BaseModel):
    """Response model for ingestion status."""
    job_id: str
    status: str
    run_id: Optional[str]
    started_at: str
    completed_at: Optional[str]
    progress: Optional[dict] = None


@router.post("/ingest/run", response_model=IngestStatusResponse)
async def start_ingestion(
    request: IngestRunRequest,
    db: Session = Depends(get_db)
):
    """
    Start an ingestion run for a specific state and county.
    Creates an ingest_runs record and triggers a Celery task.
    """
    # Create ingest run record
    run_id = f"run-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}-{request.state.lower()}-{request.county.lower().replace(' ', '-')}"
    source = f"{request.county}, {request.state}"
    
    ingest_run = IngestRun(
        id=run_id,
        source=source,
        status="running",
        started_at=datetime.utcnow(),
        parcels_processed=0,
        errors=0
    )
    
    db.add(ingest_run)
    db.commit()
    db.refresh(ingest_run)
    
    # Trigger Celery task
    task = run_ingestion_task.delay(
        run_id=run_id,
        state=request.state,
        county=request.county
    )
    
    return IngestStatusResponse(
        job_id=task.id,
        status="running",
        run_id=run_id,
        started_at=ingest_run.started_at.isoformat(),
        completed_at=None
    )


@router.get("/ingest/status/{job_id}", response_model=IngestStatusResponse)
async def get_ingestion_status(
    job_id: str,
    db: Session = Depends(get_db)
):
    """
    Get the status of an ingestion job by Celery task ID.
    """
    from celery.result import AsyncResult
    from workers.celery_app import celery_app
    
    task_result = AsyncResult(job_id, app=celery_app)
    
    # Try to find the associated ingest run
    # The run_id might be stored in task metadata or we can search by recent runs
    ingest_run = None
    
    # Try to get run_id from task result
    if task_result.info and isinstance(task_result.info, dict):
        run_id = task_result.info.get('run_id')
        if run_id:
            ingest_run = db.query(IngestRun).filter(IngestRun.id == run_id).first()
    
    # If not found, try to find by matching time window (fallback)
    if not ingest_run:
        recent_runs = db.query(IngestRun).order_by(IngestRun.started_at.desc()).limit(10).all()
        for run in recent_runs:
            # Simple heuristic: if task started around the same time as run
            if task_result.date_done:
                from datetime import datetime, timezone
                time_diff = abs((task_result.date_done.replace(tzinfo=timezone.utc) - run.started_at.replace(tzinfo=timezone.utc)).total_seconds())
                if time_diff < 60:  # Within 60 seconds
                    ingest_run = run
                    break
    
    status = "unknown"
    if task_result.state == "PENDING":
        status = "pending"
    elif task_result.state == "STARTED":
        status = "running"
    elif task_result.state == "SUCCESS":
        status = "completed"
    elif task_result.state == "FAILURE":
        status = "failed"
    
    if ingest_run:
        return IngestStatusResponse(
            job_id=job_id,
            status=ingest_run.status,
            run_id=ingest_run.id,
            started_at=ingest_run.started_at.isoformat(),
            completed_at=ingest_run.completed_at.isoformat() if ingest_run.completed_at else None,
            progress={
                "parcels_processed": ingest_run.parcels_processed,
                "parcels_total": ingest_run.parcels_total,
                "errors": ingest_run.errors
            }
        )
    else:
        return IngestStatusResponse(
            job_id=job_id,
            status=status,
            run_id=None,
            started_at=datetime.utcnow().isoformat(),
            completed_at=None
        )


@router.get("/ingest/runs", response_model=List[IngestRunResponse])
async def get_ingestion_runs(
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    """
    Get list of ingestion runs with pagination.
    """
    runs = db.query(IngestRun).order_by(IngestRun.started_at.desc()).offset(offset).limit(limit).all()
    
    return [
        IngestRunResponse(
            id=run.id,
            source=run.source,
            status=run.status,
            startedAt=run.started_at.isoformat(),
            completedAt=run.completed_at.isoformat() if run.completed_at else None,
            parcelsProcessed=run.parcels_processed,
            parcelsTotal=run.parcels_total,
            errors=run.errors
        )
        for run in runs
    ]
