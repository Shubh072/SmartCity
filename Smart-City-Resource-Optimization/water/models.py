from pydantic import BaseModel, Field
import datetime

class WaterSensorRecord(BaseModel):
    sensor_id: str = Field(..., description="Unique ID for the water pipeline sensor")
    area: str = Field(..., description="Zone or area where the sensor is located")
    timestamp: datetime.datetime = Field(..., description="Time the reading was recorded")
    pressure_psi: float = Field(..., description="Water pressure measured in PSI")
    flow_rate_lpm: float = Field(..., ge=0, description="Water flow rate measured in liters per minute")
    turbidity_ntu: float = Field(..., ge=0, description="Water turbidity level (cloudiness)")
    chlorine_mgl: float = Field(..., ge=0, description="Chlorine concentration in mg/L")
    pH: float = Field(..., ge=0, le=14, description="pH level of the water")
    is_leak_simulated: int = Field(0, description="Internal flag used for simulation purposes")

class WaterDemandForecast(BaseModel):
    date: datetime.date = Field(..., description="Date of the forecast")
    actual_flow_rate: float = Field(0, description="Actual recorded flow rate on this date")
    predicted_next_day_demand: float = Field(..., description="Machine learning prediction for next day demand")
