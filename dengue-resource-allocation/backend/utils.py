"""
Utility Functions Module
Helper functions for the backend
"""

from datetime import datetime
from typing import Dict, List
import pandas as pd


def get_timestamp() -> str:
    """Get current timestamp in ISO format"""
    return datetime.now().isoformat()


def validate_resources(resources: Dict[str, int]) -> tuple[bool, str]:
    """
    Task 1: Validate resource availability
    
    Args:
        resources: Dictionary of resource names and quantities
    
    Returns:
        Tuple of (is_valid, error_message)
    """
    valid_resources = ['Fogging_Units', 'Health_Inspectors', 'Inspection_Teams', 'Treatment_Units']
    
    for resource, quantity in resources.items():
        # Check if resource type is valid
        if resource not in valid_resources:
            return False, f"Invalid resource type: {resource}"
        
        # Check if quantity is positive
        if quantity < 0:
            return False, f"Resource quantity cannot be negative: {resource}={quantity}"
    
    return True, ""


def check_resource_availability(requested: Dict[str, int], available: Dict[str, int]) -> tuple[bool, str]:
    """
    Check if requested resources are available
    
    Args:
        requested: Dictionary of requested resources
        available: Dictionary of available resources
    
    Returns:
        Tuple of (is_available, error_message)
    """
    for resource, quantity in requested.items():
        available_qty = available.get(resource, 0)
        
        if quantity > available_qty:
            return False, f"Insufficient {resource}: requested {quantity}, available {available_qty}"
    
    return True, ""


def calculate_total_resources(resources: Dict[str, int]) -> int:
    """Calculate total number of resource units"""
    return sum(resources.values())


def format_district_predictions(predictions_df: pd.DataFrame) -> List[Dict]:
    """Format predictions DataFrame for API response"""
    if predictions_df.empty:
        return []
    
    # Convert to dict records
    records = predictions_df.to_dict('records')
    
    # Ensure all required fields are present
    for record in records:
        if 'Is_Hotspot' not in record:
            record['Is_Hotspot'] = record.get('Risk_Level') == 'High'
        if 'Hotspot_Priority' not in record:
            record['Hotspot_Priority'] = record.get('High_Probability', 0.0)
    
    return records


def format_hotspots(predictions_df: pd.DataFrame) -> List[Dict]:
    """Extract and format hotspot information"""
    if predictions_df.empty:
        return []
    
    # Filter for hotspots
    hotspots = predictions_df[predictions_df.get('Is_Hotspot', False) == True].copy()
    
    if hotspots.empty:
        return []
    
    # Sort by priority
    if 'Hotspot_Priority' in hotspots.columns:
        hotspots = hotspots.sort_values('Hotspot_Priority', ascending=False)
    
    return hotspots.to_dict('records')


def merge_predictions_and_recommendations(
    predictions: List[Dict],
    recommendations: List[Dict]
) -> List[Dict]:
    """Merge prediction and recommendation data by district"""
    # Convert to DataFrames for easier merging
    pred_df = pd.DataFrame(predictions)
    rec_df = pd.DataFrame(recommendations)
    
    if pred_df.empty or rec_df.empty:
        return predictions
    
    # Merge on District
    merged = pred_df.merge(rec_df, on='District', how='left', suffixes=('', '_recommended'))
    
    # Rename recommendation columns
    resource_cols = ['Fogging_Units', 'Health_Inspectors', 'Inspection_Teams', 'Treatment_Units']
    for col in resource_cols:
        if col in merged.columns:
            merged[f'Recommended_{col}'] = merged[col]
            merged.drop(col, axis=1, inplace=True)
    
    return merged.to_dict('records')


def calculate_prediction_summary(predictions: List[Dict]) -> Dict:
    """Calculate summary statistics from predictions"""
    if not predictions:
        return {
            'total_districts': 0,
            'high_risk_count': 0,
            'medium_risk_count': 0,
            'low_risk_count': 0,
            'hotspot_count': 0,
            'total_fogging_units': 0,
            'total_inspectors': 0,
            'total_teams': 0,
            'total_treatment_units': 0
        }
    
    df = pd.DataFrame(predictions)
    
    summary = {
        'total_districts': len(df),
        'high_risk_count': int((df['Risk_Level'] == 'High').sum()) if 'Risk_Level' in df.columns else 0,
        'medium_risk_count': int((df['Risk_Level'] == 'Medium').sum()) if 'Risk_Level' in df.columns else 0,
        'low_risk_count': int((df['Risk_Level'] == 'Low').sum()) if 'Risk_Level' in df.columns else 0,
        'hotspot_count': int(df['Is_Hotspot'].sum()) if 'Is_Hotspot' in df.columns else 0,
    }
    
    # Add resource totals if available
    resource_cols = {
        'total_fogging_units': 'Recommended_Fogging_Units',
        'total_inspectors': 'Recommended_Health_Inspectors',
        'total_teams': 'Recommended_Inspection_Teams',
        'total_treatment_units': 'Recommended_Treatment_Units'
    }
    
    for key, col in resource_cols.items():
        if col in df.columns:
            summary[key] = int(df[col].sum())
        else:
            summary[key] = 0
    
    return summary


def filter_recent_assignments(assignments: List[Dict], limit: int = 10) -> List[Dict]:
    """Get most recent resource assignments"""
    if not assignments:
        return []
    
    # Sort by timestamp (most recent first)
    sorted_assignments = sorted(
        assignments,
        key=lambda x: x.get('assigned_at', ''),
        reverse=True
    )
    
    return sorted_assignments[:limit]


def create_error_response(message: str, detail: str = None) -> Dict:
    """Create standardized error response"""
    return {
        'status': 'error',
        'message': message,
        'detail': detail,
        'timestamp': get_timestamp()
    }


def create_success_response(message: str, data: Dict = None) -> Dict:
    """Create standardized success response"""
    return {
        'status': 'success',
        'message': message,
        'data': data or {},
        'timestamp': get_timestamp()
    }


def sanitize_district_name(district: str) -> str:
    """Sanitize and normalize district name"""
    return district.strip().title()


def get_district_list(predictions: List[Dict]) -> List[str]:
    """Extract unique district names from predictions"""
    if not predictions:
        return []
    
    districts = set()
    for pred in predictions:
        if 'District' in pred:
            districts.add(pred['District'])
    
    return sorted(list(districts))


if __name__ == "__main__":
    # Test utility functions
    print("Testing utility functions...")
    
    # Test resource validation
    print("\n1. Testing resource validation:")
    valid, msg = validate_resources({
        'Fogging_Units': 10,
        'Health_Inspectors': 5
    })
    print(f"Valid resources: {valid}")
    
    invalid, msg = validate_resources({
        'Invalid_Resource': 10
    })
    print(f"Invalid resources: {invalid}, Message: {msg}")
    
    # Test availability check
    print("\n2. Testing availability check:")
    available = {
        'Fogging_Units': 100,
        'Health_Inspectors': 50
    }
    requested = {
        'Fogging_Units': 10,
        'Health_Inspectors': 5
    }
    is_avail, msg = check_resource_availability(requested, available)
    print(f"Resources available: {is_avail}")
    
    # Test summary calculation
    print("\n3. Testing summary calculation:")
    test_predictions = [
        {'District': 'A', 'Risk_Level': 'High', 'Is_Hotspot': True},
        {'District': 'B', 'Risk_Level': 'Medium', 'Is_Hotspot': False},
        {'District': 'C', 'Risk_Level': 'Low', 'Is_Hotspot': False},
    ]
    summary = calculate_prediction_summary(test_predictions)
    print(f"Summary: {summary}")
    
    print("\n✓ All utility tests passed!")