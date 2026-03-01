from pydantic import BaseModel, Field
import datetime

class WasteRecord(BaseModel):
    bin_id: str = Field(..., description="Unique ID for the waste bin")
    area: str = Field(..., description="Zone or area of the city where the bin is located")
    fill_percentage: float = Field(..., ge=0, le=100, description="Fill level of the bin from 0 to 100")
    overflow_risk: int = Field(..., ge=0, le=1, description="Binary flag indicating if the bin is at high risk of overflowing")
    population_density: float = Field(..., ge=0, description="Population density surrounding the bin (people per sq km)")
    timestamp: datetime.datetime = Field(..., description="Time the reading was recorded")

class WasteRouteRequest(BaseModel):
    truck_capacity: int = Field(20, ge=1, description="Maximum number of bins the truck can collect")
    priority_threshold: float = Field(12.0, ge=0, description="Minimum priority score needed to schedule a collection")
