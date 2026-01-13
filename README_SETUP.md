# Equilibria: Distillation Simulation Platform

Equilibria is a modular chemical engineering simulation platform designed to model separation processes with **progressive realism**.
This MVP demonstrates a binary distillation column with a FastAPI backend, validated unit operations, and a Streamlit-based interactive frontend.

**Tech Stack:** Python · FastAPI · Streamlit · pytest · CoolProp (thermophysical properties)

## Backend (FastAPI + Simulation Core)

### 1. Start the backend server (Terminal 1)

```bash
uvicorn main:app --reload
```
- FastAPI backend runs at: http://localhost:8000

## Frontend (Streamlit)

### 2. Start Streamlit Frontend (Terminal 2)
```bash
streamlit run app.py
```
- Streamlit frontend runs at: http://localhost:8501

> ⚠️**Make sure your virtual environment is activated in both terminals.**
---

## Quick Start

### 1. Clone the repository

```bash
git clone git@github.com:alejandratena/distillation_sim_v1.git
cd distillation_sim_v1
```

### 2. Create and activate a virtual environment

Type the appropriate command in your terminal:

**Mac/Linux:**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

**Windows:**
```bash
python -m venv .venv
.venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

---

## Project Structure

```
distillation_sim_v1/
│
├── backend/
│   ├── core/                # Base classes and unit operations
│   ├── simulation/          # Flowsheet and integration logic
│   ├── tests/               # Full test suite (pytest)
│
├── main.py                  # Entry point and FastAPI integration
├── app.py                   # Streamlit Frontend
├── requirements.txt         # Python dependencies
├── .gitignore               # Ignore IDE/system junk
└── README.md                # Documentation styling guide
└── README_SETUP.md          # You're here!
```

---

## Running Tests

```bash
pytest backend/tests/
```

---

## Notes for Collaborators

- **Follow clean commit practices:** small, descriptive commits grouped by function.

- **Avoid pushing system/IDE files** (`__pycache__`, `.idea/`, `.DS_Store`, etc.).

- **Please update appropriate READ_ME.md or add comments** to new modules when contributing major changes.

---

## Contact

**Questions? Ideas?** DM or @alejandratena