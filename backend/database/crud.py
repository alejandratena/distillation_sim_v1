from sqlalchemy.orm import Session
from backend.database.models import SimulationRun
from backend.database.schemas import SimulationRunCreate


def create_simulation_run(db: Session, run: SimulationRunCreate) -> SimulationRun:
    """Save a simulation run to the database."""
    db_run = SimulationRun(
        name=run.name,
        input_payload=run.input_payload,
        output_results=run.output_results,
        certainty_score=run.certainty_score,
    )
    db.add(db_run)
    db.commit()
    db.refresh(db_run)
    return db_run


def get_simulation_run(db: Session, run_id: str) -> SimulationRun | None:
    """Get a single simulation run by ID."""
    return db.query(SimulationRun).filter(SimulationRun.id == run_id).first()


def get_simulation_runs(db: Session, skip: int = 0, limit: int = 100) -> list[SimulationRun]:
    """List all simulation runs."""
    return db.query(SimulationRun).order_by(SimulationRun.created_at.desc()).offset(skip).limit(limit).all()


def delete_simulation_run(db: Session, run_id: str) -> bool:
    """Delete a simulation run. Returns True if deleted, False if not found."""
    db_run = db.query(SimulationRun).filter(SimulationRun.id == run_id).first()
    if db_run:
        db.delete(db_run)
        db.commit()
        return True
    return False