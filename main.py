# main.py - FastAPI Backend for Equilibria Technology

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, validator
from typing import Dict
import logging

from backend.core.base import Stream
from backend.simulation.flowsheet import simulate_distillation_column
from backend.core.exceptions import DomainValidationError, ThermodynamicError, BalanceError

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

def build_error_response(exc: Exception) -> dict:
    return {
        "error": {
            "type": exc.__class__.__name__,
            "message": str(exc),
            "context": getattr(exc, "context", {})
        }
    }
@app.exception_handler(DomainValidationError)
async def validation_exception_handler(request: Request, exc: DomainValidationError):
    return JSONResponse(
        status_code=400, content=build_error_response(exc)
    )
@app.exception_handler(ThermodynamicError)
async def thermodynamic_exception_handler(request: Request, exc: ThermodynamicError):
    return JSONResponse(status_code=422,
                        content=build_error_response(exc)
    )
@app.exception_handler(BalanceError)
async def balance_exception_handler(request: Request, exc: BalanceError):
    return JSONResponse(status_code=500,
                        content=build_error_response(exc)
    )
@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    return JSONResponse(status_code=500,
                        content=build_error_response(exc)
    )

# =====================================
# API ENDPOINTS
# =====================================
@app.post("/simulate/distillation", response_model=SimulationResult)
async def simulate_distillation(request: DistillationRequest):
    column = simulate_distillation_column(
        name="Distillation Column",
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

@app.get("/")
async def root():
    return {"message": "Equilibria API is running.", "version": "1.0.0"}

@app.on_event("startup")
async def startup_event():
    logging.info("Equilibria Technology API starting up...")
    logging.info("Distillation simulation endpoint ready")
    logging.info("API documentation available at /docs")