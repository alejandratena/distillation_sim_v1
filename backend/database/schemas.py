from pydantic import BaseModel
from datetime import datetime
from typing import Any, Optional


class SimulationInput(BaseModel):
    """Input parameters for running a simulation."""
    name: Optional[str] = None
    feed_flow_rate: float
    feed_temperature: float
    feed_pressure: float
    feed_composition: dict[str, float]
    distillate_split: dict[str, float]
    bottoms_split: dict[str, float]
    distillate_temperature: float
    bottoms_temperature: float
    pressure: float


class SimulationRunCreate(BaseModel):
    """What we store after running a simulation."""
    name: Optional[str] = None
    input_payload: dict[str, Any]
    output_results: dict[str, Any]
    certainty_score: float


class SimulationRunResponse(BaseModel):
    """What we return from the API."""
    id: str
    created_at: datetime
    name: Optional[str]
    input_payload: dict[str, Any]
    output_results: dict[str, Any]
    certainty_score: float

    class Config:
        from_attributes = True  # Pydantic v2; use orm_mode = True for v1