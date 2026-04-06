# Equilibria: Distillation Simulation Platform

**Most process simulators hide their assumptions. Equilibria makes model fidelity explicit.**

Equilibria is a modular chemical engineering simulation platform for modeling separation processes with **progressive realism** — a design approach where systems evolve from simplified academic assumptions to industry-grade physical accuracy.

**Tech Stack:** Python · FastAPI · Streamlit · pytest · CoolProp

![Equilibria Demo](assets/demo.gif)

---

## Why This Matters

Engineers today choose between:

- **Simplified academic tools** — fast and accessible, but disconnected from real-world behavior
- **Enterprise simulators** — accurate, but expensive, opaque, and slow to learn

**Equilibria bridges this gap with progressive realism.**

Model fidelity is explicit, measurable, and evolves with the user. You always know what assumptions you're making — and what it would take to remove them.

---

## Current Capabilities

- **Binary Distillation Simulation** — Configure feed conditions, operating parameters, and split fractions with real-time results
- **Certainty Engine** — Structured model fidelity tracking (Foundational → Industry+)
- **Validated Mass & Energy Balances** — Tolerance-based checks ensure physical consistency
- **CoolProp Integration** — Real thermophysical properties, not hardcoded constants
- **Clean API** — FastAPI backend with Swagger docs at `/docs`

---

## Certainty Engine

The Certainty Engine provides a structured proxy for **model fidelity** — answering:

> *How much of the relevant physical reality does this simulation currently capture?*

This is a **relative fidelity index**, not formal statistical uncertainty quantification.

### Fidelity Dimensions

Model fidelity is evaluated across four dimensions:

| Dimension | Weight | Description |
|-----------|--------|-------------|
| Thermodynamic Rigor | 40% | VLE models, activity coefficients, EOS |
| Transport & Hydraulics | 25% | Pressure drops, mass transfer, tray efficiency |
| Operational Realism | 20% | Startup behavior, control systems, degradation |
| Validation Maturity | 15% | Balance checks, experimental correlation, plant data |

### Fidelity Levels

1. **Foundational (≤30%)** — Simplified, balance-validated
2. **Intermediate (≤55%)** — Non-ideal behavior, energy coupling
3. **Advanced Academic (≤75%)** — Pressure effects, complex phase behavior
4. **Industry Sim (≤90%)** — Safety margins, failure modes
5. **Industry+ (≤98%)** — Toward plant validation and uncertainty-aware modeling

**Current State:** Foundational (~30%)

---

## System Overview

Equilibria is built as a **composable simulation system**. Unit operations encapsulate physical behavior independently and can be assembled into flowsheets without tight coupling.

### Architecture

```
Streamlit UI  →  FastAPI Backend  →  Simulation Layer  →  Domain Core
   (app.py)        (main.py)        (flowsheet.py)      (Stream, UnitOps)
```

| Layer | Responsibility |
|-------|----------------|
| **Frontend** | Interactive UI for simulation configuration and results |
| **Backend** | API endpoints, validation, and simulation orchestration |
| **Simulation** | Flowsheet logic, stream propagation, system-level validation |
| **Core** | Unit operations with embedded mass and energy balances |
| **Certainty** | Model fidelity scoring across defined dimensions |

### Design Decisions

- **FastAPI over Flask** — Native Pydantic validation and async scalability
- **Tolerance-based balance checks** — Reliable handling of floating-point precision
- **CoolProp for thermophysics** — Enables transition from ideal to real-fluid modeling
- **Certainty as first-class feature** — Model assumptions are surfaced, not hidden

---

## Quick Start

### 1. Clone the repository
```bash
git clone git@github.com:alejandratena/distillation_sim_v1.git
cd distillation_sim_v1
```

### 2. Set up environment
```bash
python3 -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Run the application

**Terminal 1 — Backend:**
```bash
uvicorn main:app --reload
```
- API: http://localhost:8000
- Docs: http://localhost:8000/docs

**Terminal 2 — Frontend:**
```bash
streamlit run app.py
```
- UI: http://localhost:8501

---

## Running Tests
```bash
pytest backend/tests/
```

Validates mass balance consistency, energy balance tolerances, and system-level integration.

---

## Project Structure
```
equilibria/
├── backend/
│   ├── core/           # Unit operations and base classes
│   ├── simulation/     # Flowsheet orchestration
│   ├── certainty/      # Certainty Engine
│   └── tests/          # pytest suite
├── main.py             # FastAPI entry point
├── app.py              # Streamlit frontend
└── requirements.txt
```

---

## Roadmap

### Shipped
- Binary distillation with CoolProp integration
- Mass and energy balance validation
- Certainty Engine (multi-dimensional fidelity scoring)
- FastAPI backend with Swagger docs
- Streamlit frontend with real-time results

### Next
- Activity coefficient models (NRTL / UNIQUAC)
- Simulation persistence (database integration)
- Experiment-based mixing rules

###  Future
- Recycle streams and convergence algorithms
- React-based flowsheet builder
- ML-assisted parameter estimation
- Progressive realism UI controls

---

## Contributing

- Use small, descriptive commits grouped by functionality
- Avoid committing system files (`.idea/`, `__pycache__/`, `.DS_Store`)
- Document meaningful changes in code or README

---

## Contact

Questions, ideas, or collaboration: [@alejandratena](https://github.com/alejandratena)