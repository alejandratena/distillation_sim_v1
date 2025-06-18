# 🧪 Equilibria: Distillation Simulation Frontend

## Running App Locally

### 1. **Start the backend server** in your terminal: 

```bash
uvicorn main:app --reload
```

### 2. **Open a second terminal** and run the Streamlit frontend
```bash
streamlit run app.py
```
> **Make sure your virtual environment is activated in both terminals.**

# 🧪 Equilibria: Distillation Simulation Backend

This repository contains the core backend logic, unit operations, simulation models, and tests for the Equilibria's MVP — a lightweight, modular simulation platform for educational, industry, and early R&D use cases.

---

## Quick Start

### 1. Clone the repository

```bash
git clone git@github.com:alejandratena/distillation_sim_v1.git
cd distillation_sim_v1
```

> **🔒 You must be added as a collaborator to access this private repo.**

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
├── requirements.txt         # Python dependencies
├── .gitignore               # Ignore IDE/system junk
└── READ_ME_DOC_GUIDE.md     # Documentation styling guide
└── READ_ME_SETUP.md         # You're here!
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

**Questions? Ideas?** DM or @ Alejandra (@alejandratena).

**Let's build the future of process simulation** ✨