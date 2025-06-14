# main.py - FastAPI Backend for Equilibria Technology
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field, validator
from typing import Dict, Optional
import logging
from backend.core.base import Stream
from backend.simulation.flowsheet import simulate_distillation_column
app = FastAPI(
    title="Equilibria Technology API",
    description="Distillation column simulation endpoint",
    version="1.0.0"
)
logging.basicConfig(level=logging.INFO)
# =====================================
# COMPONENTS AND CONSTANTS
# =====================================
COMPONENTS = ["Water", "Ethanol"]
# =====================================
# REQUEST/RESPONSE MODELS
# =====================================
class StreamData(BaseModel):
    temperature: float = Field(..., description="Temperature in °C")
    pressure: float = Field(..., description="Pressure in kPa")
    mass_flow: float = Field(..., description="Mass flow rate in kg/h")
    composition: Dict[str, float] = Field(..., description="Component mass fractions")
    @validator("composition")
    def validate_composition(cls, v):
        total = sum(v.values())
        if abs(total - 1.0) > 0.01:
            raise ValueError("Component mass fractions must sum to 1.0 ±0.01")
        for comp in v:
            if comp not in COMPONENTS:
                raise ValueError(f"Invalid component: {comp}. Must be one of {COMPONENTS}")
        return v
class DistillationRequest(BaseModel):
    feed_stream: StreamData
    distillate_split: Dict[str, float]
    bottoms_split: Dict[str, float]
    distillate_temperature: float
    bottoms_temperature: float
    pressure: float
class SimulationResult(BaseModel):
    success: bool
    message: str
    distillate: StreamData
    bottoms: StreamData
# =====================================
# UTILITY FUNCTIONS
# =====================================
def convert_stream_to_model(stream: Stream) -> StreamData:
    return StreamData(
        temperature=stream.temperature,
        pressure=stream.pressure,
        mass_flow=stream.flow_rate,
        composition=stream.composition
    )
# =====================================
# API ENDPOINTS
# =====================================
@app.post("/simulate/distillation", response_model=SimulationResult)
async def simulate_distillation(request: DistillationRequest):
    try:
        column = simulate_distillation_column(
            name="Column-001",
            feed_flow_rate=request.feed_stream.mass_flow,
            feed_temperature=request.feed_stream.temperature,
            feed_pressure=request.feed_stream.pressure,
            feed_composition=request.feed_stream.composition,
            distillate_split=request.distillate_split,
            bottoms_split=request.bottoms_split,
            distillate_temperature=request.distillate_temperature,
            bottoms_temperature=request.bottoms_temperature,
            pressure=request.pressure
        )
        return SimulationResult(
            success=True,
            message="Distillation simulation completed successfully",
            distillate=convert_stream_to_model(column.outlet_streams[0]),
            bottoms=convert_stream_to_model(column.outlet_streams[1])
        )
    except Exception as e:
        logging.error("Simulation failed", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Simulation failed: {str(e)}")
@app.get("/")
async def root():
    return {"message": "Equilibria API is running.", "version": "1.0.0"}
@app.on_event("startup")
async def startup_event():
    logging.info("🚀 Equilibria Technology API starting up...")
    logging.info("📊 Distillation simulation endpoint ready")
    logging.info("📖 API documentation available at /docs")