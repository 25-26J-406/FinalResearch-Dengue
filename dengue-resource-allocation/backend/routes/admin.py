"""
Admin Dashboard Routes
Provides overview and comprehensive data for administrators
"""

from fastapi import APIRouter, HTTPException, status
from typing import Dict, List
import pandas as pd

from backend.schemas import AdminOverview, HotspotInfo, PredictionSummary
from backend.json_store import get_store
from backend.utils import (
    get_timestamp,
    calculate_prediction_summary,
    merge_predictions_and_recommendations,
    filter_recent_assignments,
    get_district_list
)

router = APIRouter(prefix="/admin", tags=["Admin Dashboard"])


@router.get("/overview", response_model=Dict)
async def get_admin_overview():
    """
    Task 1: Create admin overview endpoint
    Task 2: Return district risks, hotspots, and recommendations
    Task 3: Return current resource availability
    
    Get comprehensive dashboard overview including:
    - Summary statistics
    - Available resources
    - Hotspots
    - High-risk districts
    - Recent assignments
    """
    try:
        store = get_store()
        
        # Get all data
        predictions = store.get_district_predictions()
        hotspots = store.get_hotspots()
        recommendations = store.get_resource_recommendations()
        available_resources = store.get_available_resources()
        all_assignments = store.get_resource_assignments()
        
        # Merge predictions with recommendations
        if predictions and recommendations:
            complete_data = merge_predictions_and_recommendations(
                predictions, recommendations
            )
        else:
            complete_data = predictions
        
        # Calculate summary
        summary = calculate_prediction_summary(complete_data)
        
        # Get recent assignments
        recent_assignments = filter_recent_assignments(all_assignments, limit=10)
        
        # Format hotspots with recommendations
        hotspot_details = []
        for hotspot in hotspots:
            district = hotspot.get('District')
            
            # Find recommendation for this district
            rec = next(
                (r for r in recommendations if r.get('District') == district),
                {}
            )
            
            hotspot_details.append({
                'District': district,
                'Risk_Level': hotspot.get('Risk_Level', 'High'),
                'High_Probability': hotspot.get('High_Probability', 0),
                'Recommended_Fogging_Units': rec.get('Fogging_Units', 0),
                'Recommended_Health_Inspectors': rec.get('Health_Inspectors', 0),
                'Recommended_Inspection_Teams': rec.get('Inspection_Teams', 0),
                'Recommended_Treatment_Units': rec.get('Treatment_Units', 0)
            })
        
        # Get high-risk districts
        high_risk_districts = [
            p for p in predictions 
            if p.get('Risk_Level') == 'High'
        ]
        
        return {
            "status": "success",
            "summary": summary,
            "available_resources": available_resources,
            "hotspots": hotspot_details,
            "high_risk_districts": high_risk_districts,
            "recent_assignments": recent_assignments,
            "districts": get_district_list(predictions),
            "timestamp": get_timestamp()
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate admin overview: {str(e)}"
        )


@router.get("/statistics", response_model=Dict)
async def get_statistics():
    """
    Get detailed statistical analysis
    """
    try:
        store = get_store()
        predictions = store.get_district_predictions()
        recommendations = store.get_resource_recommendations()
        
        if not predictions:
            return {
                "status": "success",
                "message": "No data available",
                "statistics": {},
                "timestamp": get_timestamp()
            }
        
        # Convert to DataFrame for analysis
        pred_df = pd.DataFrame(predictions)
        
        # Risk level distribution
        risk_distribution = pred_df['Risk_Level'].value_counts().to_dict()
        
        # Calculate probability statistics
        prob_stats = {
            'High_Risk': {
                'mean': float(pred_df['High_Probability'].mean()),
                'max': float(pred_df['High_Probability'].max()),
                'min': float(pred_df['High_Probability'].min())
            },
            'Medium_Risk': {
                'mean': float(pred_df['Medium_Probability'].mean()),
                'max': float(pred_df['Medium_Probability'].max()),
                'min': float(pred_df['Medium_Probability'].min())
            },
            'Low_Risk': {
                'mean': float(pred_df['Low_Probability'].mean()),
                'max': float(pred_df['Low_Probability'].max()),
                'min': float(pred_df['Low_Probability'].min())
            }
        }
        
        # Resource statistics if available
        resource_stats = {}
        if recommendations:
            rec_df = pd.DataFrame(recommendations)
            resource_cols = ['Fogging_Units', 'Health_Inspectors', 
                           'Inspection_Teams', 'Treatment_Units']
            
            for col in resource_cols:
                if col in rec_df.columns:
                    resource_stats[col] = {
                        'total': int(rec_df[col].sum()),
                        'mean': float(rec_df[col].mean()),
                        'max': int(rec_df[col].max()),
                        'min': int(rec_df[col].min())
                    }
        
        return {
            "status": "success",
            "statistics": {
                "risk_distribution": risk_distribution,
                "probability_statistics": prob_stats,
                "resource_statistics": resource_stats,
                "total_districts": len(pred_df)
            },
            "timestamp": get_timestamp()
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to calculate statistics: {str(e)}"
        )


@router.get("/district-comparison", response_model=Dict)
async def compare_districts():
    """
    Get comparative analysis of all districts
    """
    try:
        store = get_store()
        predictions = store.get_district_predictions()
        recommendations = store.get_resource_recommendations()
        
        if not predictions:
            return {
                "status": "success",
                "message": "No data available",
                "comparison": [],
                "timestamp": get_timestamp()
            }
        
        # Merge data
        comparison_data = merge_predictions_and_recommendations(
            predictions, recommendations
        )
        
        # Sort by risk level and probability
        risk_order = {'High': 3, 'Medium': 2, 'Low': 1}
        comparison_data.sort(
            key=lambda x: (
                risk_order.get(x.get('Risk_Level', 'Low'), 0),
                x.get('High_Probability', 0)
            ),
            reverse=True
        )
        
        return {
            "status": "success",
            "message": "District comparison retrieved successfully",
            "count": len(comparison_data),
            "comparison": comparison_data,
            "timestamp": get_timestamp()
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to compare districts: {str(e)}"
        )


@router.get("/resource-gap", response_model=Dict)
async def analyze_resource_gap():
    """
    Analyze gap between recommended and available resources
    """
    try:
        store = get_store()
        recommendations = store.get_resource_recommendations()
        available = store.get_available_resources()
        
        if not recommendations:
            return {
                "status": "success",
                "message": "No recommendations available",
                "gap_analysis": {},
                "timestamp": get_timestamp()
            }
        
        # Calculate total recommended
        rec_df = pd.DataFrame(recommendations)
        resource_cols = ['Fogging_Units', 'Health_Inspectors', 
                        'Inspection_Teams', 'Treatment_Units']
        
        gap_analysis = {}
        for col in resource_cols:
            if col in rec_df.columns:
                total_recommended = int(rec_df[col].sum())
                available_qty = available.get(col, 0)
                gap = total_recommended - available_qty
                
                gap_analysis[col] = {
                    'total_recommended': total_recommended,
                    'currently_available': available_qty,
                    'gap': gap,
                    'gap_percentage': round((gap / total_recommended * 100) if total_recommended > 0 else 0, 2),
                    'sufficient': gap <= 0
                }
        
        # Overall assessment
        all_sufficient = all(v['sufficient'] for v in gap_analysis.values())
        
        return {
            "status": "success",
            "message": "Resource gap analysis completed",
            "gap_analysis": gap_analysis,
            "overall_sufficient": all_sufficient,
            "timestamp": get_timestamp()
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to analyze resource gap: {str(e)}"
        )


@router.get("/export", response_model=Dict)
async def export_data():
    """
    Export all data for external use or backup
    """
    try:
        store = get_store()
        all_data = store.get_all_data()
        
        return {
            "status": "success",
            "message": "Data exported successfully",
            "data": all_data,
            "timestamp": get_timestamp()
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to export data: {str(e)}"
        )


@router.get("/health", response_model=Dict)
async def health_check():
    """
    System health check for monitoring
    """
    try:
        store = get_store()
        
        # Check if data exists
        predictions = store.get_district_predictions()
        resources = store.get_available_resources()
        
        return {
            "status": "healthy",
            "message": "System is operational",
            "checks": {
                "storage_accessible": True,
                "predictions_available": len(predictions) > 0,
                "resources_configured": len(resources) > 0
            },
            "timestamp": get_timestamp()
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"System health check failed: {str(e)}"
        )