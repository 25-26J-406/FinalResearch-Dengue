"""
Pydantic Schemas Module
Defines request/response models for API validation
"""

from pydantic import BaseModel, Field, validator
from typing import Dict, List, Optional
from datetime import datetime


# Resource Schemas

class ResourceUpdate(BaseModel):
    """Schema for updating resource quantities"""
    Fogging_Units: Optional[int] = Field(None, ge=0, description="Number of fogging units")
    Health_Inspectors: Optional[int] = Field(None, ge=0, description="Number of health inspectors")
    Inspection_Teams: Optional[int] = Field(None, ge=0, description="Number of inspection teams")
    Treatment_Units: Optional[int] = Field(None, ge=0, description="Number of treatment units")
    
    class Config:
        json_schema_extra = {
            "example": {
                "Fogging_Units": 100,
                "Health_Inspectors": 50,
                "Inspection_Teams": 30,
                "Treatment_Units": 80
            }
        }


class ResourceResponse(BaseModel):
    """Schema for resource availability response"""
    available_resources: Dict[str, int]
    total_resources: int
    timestamp: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "available_resources": {
                    "Fogging_Units": 100,
                    "Health_Inspectors": 50,
                    "Inspection_Teams": 30,
                    "Treatment_Units": 80
                },
                "total_resources": 260,
                "timestamp": "2024-01-07T10:30:00"
            }
        }


# Prediction Schemas

class DistrictPrediction(BaseModel):
    """Schema for district risk prediction"""
    District: str
    Risk_Level: str
    Risk_Score: int
    Low_Probability: float
    Medium_Probability: float
    High_Probability: float
    Is_Hotspot: bool
    Hotspot_Priority: Optional[float] = None


class ResourceRecommendation(BaseModel):
    """Schema for resource recommendations"""
    District: str
    Fogging_Units: int
    Health_Inspectors: int
    Inspection_Teams: int
    Treatment_Units: int


class PredictionResponse(BaseModel):
    """Schema for prediction endpoint response"""
    status: str
    message: str
    predictions_count: int
    hotspots_count: int
    timestamp: str


class PredictionSummary(BaseModel):
    """Schema for prediction summary"""
    total_districts: int
    high_risk_count: int
    medium_risk_count: int
    low_risk_count: int
    hotspot_count: int
    total_fogging_units: int
    total_inspectors: int
    total_teams: int
    total_treatment_units: int


# Assignment Schemas

class ResourceAssignment(BaseModel):
    """Schema for assigning resources to a district"""
    district: str = Field(..., description="District name")
    Fogging_Units: int = Field(0, ge=0, description="Number of fogging units to assign")
    Health_Inspectors: int = Field(0, ge=0, description="Number of health inspectors to assign")
    Inspection_Teams: int = Field(0, ge=0, description="Number of inspection teams to assign")
    Treatment_Units: int = Field(0, ge=0, description="Number of treatment units to assign")
    notes: Optional[str] = Field(None, description="Additional notes for this assignment")
    
    @validator('district')
    def district_not_empty(cls, v):
        if not v or not v.strip():
            raise ValueError('District name cannot be empty')
        return v.strip()
    
    class Config:
        json_schema_extra = {
            "example": {
                "district": "Colombo",
                "Fogging_Units": 10,
                "Health_Inspectors": 5,
                "Inspection_Teams": 3,
                "Treatment_Units": 8,
                "notes": "High-priority hotspot allocation"
            }
        }


class AssignmentResponse(BaseModel):
    """Schema for assignment response"""
    status: str
    message: str
    district: str
    assigned_resources: Dict[str, int]
    remaining_resources: Dict[str, int]
    assigned_at: str


# Admin Dashboard Schemas

class HotspotInfo(BaseModel):
    """Schema for hotspot information"""
    District: str
    Risk_Level: str
    High_Probability: float
    Recommended_Fogging_Units: int
    Recommended_Health_Inspectors: int
    Recommended_Inspection_Teams: int
    Recommended_Treatment_Units: int


class AdminOverview(BaseModel):
    """Schema for admin dashboard overview"""
    summary: PredictionSummary
    available_resources: Dict[str, int]
    hotspots: List[HotspotInfo]
    high_risk_districts: List[DistrictPrediction]
    recent_assignments: List[Dict]
    timestamp: str


# Error Schemas

class ErrorResponse(BaseModel):
    """Schema for error responses"""
    status: str = "error"
    message: str
    detail: Optional[str] = None
    timestamp: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "status": "error",
                "message": "Resource not found",
                "detail": "The requested resource does not exist",
                "timestamp": "2024-01-07T10:30:00"
            }
        }


# Success Schemas

class SuccessResponse(BaseModel):
    """Generic success response"""
    status: str = "success"
    message: str
    data: Optional[Dict] = None
    timestamp: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "status": "success",
                "message": "Operation completed successfully",
                "data": {},
                "timestamp": "2024-01-07T10:30:00"
            }
        }