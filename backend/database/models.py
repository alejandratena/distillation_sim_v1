from sqlalchemy import Column, String, Float, DateTime, JSON
from datetime import datetime
import uuid

from backend.database.database import Base


class SimulationRun(Base):
    __tablename__ = "simulation_runs"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    name = Column(String, nullable=True)
    input_payload = Column(JSON, nullable=False)
    output_results = Column(JSON, nullable=False)
    certainty_score = Column(Float, nullable=False)