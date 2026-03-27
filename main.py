# main.py - FastAPI Backend for Equilibria Technology

import logging
import time
import uuid
from contextvars import ContextVar
from typing import Dict

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, field_validator

from backend.core.base import Stream
from backend.core.exceptions import BalanceError, DomainValidationError, ThermodynamicError
from backend.simulation.flowsheet import simulate_distillation_column

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | request_id=%(request_id)s | %(name)s | %(message)s",
)

logger = logging.getLogger("equilibria")
request_id_context: ContextVar[str] = ContextVar("request_id", default="-")
APP_VERSION = "1.0.0"


class RequestIdFilter(logging.Filter):
    """Inject request_id into all log records."""

    def filter(self, record: logging.LogRecord) -> bool:
        record.request_id = request_id_context.get()
        return True


logger.addFilter(RequestIdFilter())

app = FastAPI(
    title="Equilibria Technology API",
    description="Distillation column simulation endpoint",
    version=APP_VERSION
)

@app.middleware("http")
async def add_request_id_middleware(request: Request, call_next):
    request_id = str(uuid.uuid4())
    token = request_id_context.set(request_id)
    start = time.perf_counter()

    logger.info("request started %s %s", request.method, request.url.path)

    try:
        response = await call_next(request)
    finally:
        duration_ms = (time.perf_counter() - start) * 1000
        logger.info("request completed duration_ms=%.2f", duration_ms)
        request_id_context.reset(token)

    response.headers["X-Request-ID"] = request_id
    return response


@app.get("/health")
def health_check():
    return {"status": "ok", "version": APP_VERSION}

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

    @field_validator("composition")
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
    logger.warning("domain validation error: %s", exc)
    return JSONResponse(status_code=400, content=build_error_response(exc))

@app.exception_handler(ThermodynamicError)
async def thermodynamic_exception_handler(request: Request, exc: ThermodynamicError):
    logger.warning("thermodynamic error: %s", exc)
    return JSONResponse(status_code=422,
                        content=build_error_response(exc)
    )

@app.exception_handler(BalanceError)
async def balance_exception_handler(request: Request, exc: BalanceError):
    logger.error("balance error: %s", exc)
    return JSONResponse(
        status_code=500,
        content=build_error_response(exc)
    )

@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    logger.exception("unexpected error")
    return JSONResponse(
        status_code=500,
        content=build_error_response(exc)
    )

# =====================================
# API ENDPOINTS
# =====================================
@app.post("/simulate/distillation", response_model=SimulationResult)
async def simulate_distillation(request: DistillationRequest):
    run_id = str(uuid.uuid4())
    start = time.perf_counter()

    logger.info("simulation started run_id=%s path=/simulate/distillation", run_id)

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

    duration_ms = (time.perf_counter() - start) * 1000
    logger.info(
        "simulation completed run_id=%s unit_op=DistillationColumn duration_ms=%.2f",
        run_id,
        duration_ms,
    )

    return SimulationResult(
        success=True,
        message="Distillation simulation completed successfully",
        distillate=convert_stream_to_model(column.outlet_streams[0]),
        bottoms=convert_stream_to_model(column.outlet_streams[1])
    )

@app.get("/")
async def root():
    return {"message": "Equilibria API is running.", "version": APP_VERSION}

@app.on_event("startup")
async def startup_event():
    logger.info("Equilibria Technology API starting up")
    logger.info("Distillation simulation endpoint ready")
    logger.info("API documentation available at /docs")