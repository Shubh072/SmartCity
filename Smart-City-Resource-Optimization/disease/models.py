from pydantic import BaseModel, Field
import datetime

class DiseaseRecord(BaseModel):
    record_id: str = Field(..., description="Unique identifier for the hospital record")
    area: str = Field(..., description="City zone where the cases originated")
    disease: str = Field(..., description="Type of disease (e.g., Dengue, Malaria)")
    date: datetime.date = Field(..., description="Date the cases were reported")
    cases: int = Field(..., ge=0, description="Number of confirmed cases")

class DiseaseAlert(BaseModel):
    area: str = Field(..., description="City zone")
    disease: str = Field(..., description="Type of disease tracked")
    current_cases: int = Field(..., ge=0, description="Cases reported in the most recent week")
    growth_rate: float = Field(..., ge=0, description="Week over week multiplier for the disease spread")
    predicted_next_week: float = Field(..., description="Model prediction for next week's cases")
    is_alert: bool = Field(False, description="Whether this triggers a critical threshold warning")
