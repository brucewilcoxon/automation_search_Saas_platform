"""
Comparable sales similarity calculation logic.
Deterministic heuristic-based scoring.
"""
from typing import Optional
from decimal import Decimal


def calculate_similarity_score(
    target_acreage: Optional[float],
    target_zoning: Optional[str],
    target_lat: Optional[float],
    target_lng: Optional[float],
    comp_acreage: Optional[float],
    comp_zoning: Optional[str],
    comp_lat: Optional[float],
    comp_lng: Optional[float],
    distance_miles: Optional[float]
) -> float:
    """
    Calculate similarity score between target parcel and comparable sale.
    
    Scoring weights (as per frontend description):
    - Acreage proximity: 40%
    - Zoning match: 30%
    - Geographic distance: 30%
    
    Args:
        target_acreage: Target parcel acreage
        target_zoning: Target parcel zoning
        target_lat: Target parcel latitude
        target_lng: Target parcel longitude
        comp_acreage: Comparable sale acreage
        comp_zoning: Comparable sale zoning
        comp_lat: Comparable sale latitude
        comp_lng: Comparable sale longitude
        distance_miles: Pre-calculated distance in miles
        
    Returns:
        Similarity score from 0-100
    """
    # Calculate acreage similarity (40% weight)
    acreage_score = 0.0
    if target_acreage and comp_acreage and target_acreage > 0:
        # Calculate percentage difference
        diff = abs(target_acreage - comp_acreage) / target_acreage
        # Score: 100% if identical, decreases linearly
        # Perfect match (0% diff) = 100, 50% diff = 50, 100%+ diff = 0
        acreage_score = max(0.0, 100.0 - (diff * 100.0))
    acreage_weighted = acreage_score * 0.4
    
    # Calculate zoning similarity (30% weight)
    zoning_score = 0.0
    if target_zoning and comp_zoning:
        target_zoning_norm = target_zoning.strip().upper()
        comp_zoning_norm = comp_zoning.strip().upper()
        
        if target_zoning_norm == comp_zoning_norm:
            zoning_score = 100.0
        elif target_zoning_norm in comp_zoning_norm or comp_zoning_norm in target_zoning_norm:
            # Partial match (e.g., "R-1" vs "R-1A")
            zoning_score = 70.0
        else:
            # Check for same category (e.g., both start with "R" for residential)
            if target_zoning_norm and comp_zoning_norm:
                if target_zoning_norm[0] == comp_zoning_norm[0]:
                    zoning_score = 40.0
    zoning_weighted = zoning_score * 0.3
    
    # Calculate distance similarity (30% weight)
    distance_score = 0.0
    if distance_miles is not None:
        # Score based on distance:
        # 0-0.5 mi = 100, 0.5-1 mi = 90, 1-2 mi = 70, 2-5 mi = 50, 5+ mi = 30
        if distance_miles <= 0.5:
            distance_score = 100.0
        elif distance_miles <= 1.0:
            distance_score = 90.0
        elif distance_miles <= 2.0:
            distance_score = 70.0
        elif distance_miles <= 5.0:
            distance_score = 50.0
        else:
            distance_score = max(0.0, 30.0 - ((distance_miles - 5.0) * 2.0))
    distance_weighted = distance_score * 0.3
    
    # Total score
    total_score = acreage_weighted + zoning_weighted + distance_weighted
    
    # Round to 2 decimal places for determinism
    return round(total_score, 2)


def calculate_distance_miles(
    lat1: float, lng1: float, lat2: float, lng2: float
) -> float:
    """
    Calculate distance between two coordinates using Haversine formula.
    
    Args:
        lat1, lng1: First point coordinates
        lat2, lng2: Second point coordinates
        
    Returns:
        Distance in miles
    """
    from math import radians, sin, cos, sqrt, atan2
    
    # Earth's radius in miles
    R = 3959.0
    
    # Convert to radians
    lat1_rad = radians(lat1)
    lng1_rad = radians(lng1)
    lat2_rad = radians(lat2)
    lng2_rad = radians(lng2)
    
    # Haversine formula
    dlat = lat2_rad - lat1_rad
    dlng = lng2_rad - lng1_rad
    
    a = sin(dlat / 2) ** 2 + cos(lat1_rad) * cos(lat2_rad) * sin(dlng / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    
    distance = R * c
    return round(distance, 4)  # Round to 4 decimal places
