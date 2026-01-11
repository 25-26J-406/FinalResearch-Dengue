"""
Resource Management Routes
CRUD operations for dengue control resources
"""

from fastapi import APIRouter, HTTPException, status
from typing import Dict
from datetime import datetime

from backend.schemas import (
    ResourceUpdate,
    ResourceResponse,
    ResourceAssignment,
    AssignmentResponse,
    ErrorResponse,
    SuccessResponse
)
from backend.json_store import get_store
from backend.utils import (
    validate_resources,
    check_resource_availability,
    calculate_total_resources,
    get_timestamp,
    create_error_response,
    create_success_response,
    sanitize_district_name
)
from backend.config import DEFAULT_RESOURCES

router = APIRouter(prefix="/resources", tags=["Resource Management"])


@router.get("/", response_model=ResourceResponse)
async def get_resources():
    """
    Task 1: GET endpoint for resources
    
    Get current available resource counts
    """
    try:
        store = get_store()
        available = store.get_available_resources()
        
        # If no resources set, use defaults
        if not available:
            available = DEFAULT_RESOURCES.copy()
            store.set_available_resources(available)
        
        return ResourceResponse(
            available_resources=available,
            total_resources=calculate_total_resources(available),
            timestamp=get_timestamp()
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve resources: {str(e)}"
        )


@router.post("/", response_model=SuccessResponse)
async def create_or_update_resources(resources: ResourceUpdate):
    """
    Task 2: POST endpoint to add/update resources
    
    Set or completely replace available resource counts
    """
    try:
        # Convert to dict and filter None values
        resource_dict = {k: v for k, v in resources.dict().items() if v is not None}
        
        if not resource_dict:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No resources provided"
            )
        
        # Validate resources
        is_valid, error_msg = validate_resources(resource_dict)
        if not is_valid:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=error_msg
            )
        
        # Save to store
        store = get_store()
        store.set_available_resources(resource_dict)
        
        return SuccessResponse(
            message="Resources updated successfully",
            data={
                "resources": resource_dict,
                "total": calculate_total_resources(resource_dict)
            },
            timestamp=get_timestamp()
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update resources: {str(e)}"
        )
@router.get("/total-allocated", response_model=SuccessResponse)
async def get_total_allocated_resources():
    """
    Get total allocated (assigned) resources across all districts
    """
    try:
        store = get_store()
        assignments = store.get_resource_assignments()

        total_allocated = {}

        for assignment in assignments:
            for resource, qty in assignment["resources"].items():
                total_allocated[resource] = total_allocated.get(resource, 0) + qty

        return SuccessResponse(
            message="Total allocated resources calculated successfully",
            data={
                "total_allocated": total_allocated,
                "total": calculate_total_resources(total_allocated)
            },
            timestamp=get_timestamp()
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to calculate total allocated resources: {str(e)}"
        )

@router.put("/{resource_name}", response_model=SuccessResponse)
async def update_resource_quantity(resource_name: str, quantity: int):
    """
    Task 3: PUT endpoint to modify resource counts
    
    Update quantity of a specific resource type
    """
    try:
        # Validate resource name
        valid_resources = ['Fogging_Units', 'Health_Inspectors', 'Inspection_Teams', 'Treatment_Units']
        if resource_name not in valid_resources:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid resource name. Must be one of: {valid_resources}"
            )
        
        # Validate quantity
        if quantity < 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Quantity cannot be negative"
            )
        
        # Update in store
        store = get_store()
        store.update_resource_quantity(resource_name, quantity)
        
        # Get updated resources
        updated_resources = store.get_available_resources()
        
        return SuccessResponse(
            message=f"{resource_name} updated successfully",
            data={
                "resource": resource_name,
                "new_quantity": quantity,
                "all_resources": updated_resources
            },
            timestamp=get_timestamp()
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update resource: {str(e)}"
        )


@router.post("/assign", response_model=AssignmentResponse)
async def assign_resources(assignment: ResourceAssignment):
    """
    Assign resources to a specific district
    
    Task 1: Validate resource availability
    Task 2: Assign resources to districts
    Task 3: Update remaining resources
    """
    try:
        store = get_store()
        
        # Sanitize district name
        district = sanitize_district_name(assignment.district)
        
        # Get requested resources (non-zero only)
        requested = {
            k: v for k, v in assignment.dict().items() 
            if k not in ['district', 'notes'] and v > 0
        }
        
        if not requested:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No resources specified for assignment"
            )
        
        # Validate resources
        is_valid, error_msg = validate_resources(requested)
        if not is_valid:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=error_msg
            )
        
        # Check availability
        available = store.get_available_resources()
        is_available, error_msg = check_resource_availability(requested, available)
        
        if not is_available:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=error_msg
            )
        
        # Deduct resources
        success = store.deduct_resources(requested)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to deduct resources"
            )
        
        # Save assignment record
        assignment_record = {
            "district": district,
            "resources": requested,
            "notes": assignment.notes
        }
        store.save_resource_assignment(assignment_record)
        
        # Get updated available resources
        remaining = store.get_available_resources()
        
        return AssignmentResponse(
            status="success",
            message=f"Resources assigned to {district} successfully",
            district=district,
            assigned_resources=requested,
            remaining_resources=remaining,
            assigned_at=get_timestamp()
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to assign resources: {str(e)}"
        )


@router.get("/assignments", response_model=Dict)
async def get_resource_assignments(district: str = None):
    """
    Get resource assignment history
    
    Optional query parameter to filter by district
    """
    try:
        store = get_store()
        assignments = store.get_resource_assignments(district=district)
        
        return {
            "status": "success",
            "count": len(assignments),
            "district_filter": district,
            "assignments": assignments,
            "timestamp": get_timestamp()
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve assignments: {str(e)}"
        )


@router.delete("/assignments", response_model=SuccessResponse)
async def clear_assignments():
    """
    Clear all resource assignments (does not restore resources)
    """
    try:
        store = get_store()
        store.clear_assignments()
        
        return SuccessResponse(
            message="All assignments cleared successfully",
            data={"cleared": True},
            timestamp=get_timestamp()
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to clear assignments: {str(e)}"
        )


@router.post("/reset", response_model=SuccessResponse)
async def reset_resources():
    """
    Reset resources to default values
    """
    try:
        store = get_store()
        store.set_available_resources(DEFAULT_RESOURCES.copy())
        
        return SuccessResponse(
            message="Resources reset to defaults",
            data={"resources": DEFAULT_RESOURCES},
            timestamp=get_timestamp()
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to reset resources: {str(e)}"
        )