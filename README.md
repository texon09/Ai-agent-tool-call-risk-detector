# AI Agent Tool Call Risk Detector

This project is a proxy-style guardrail for AI agents. It intercepts tool-call plans and evaluates their risk before execution, using a mix of deterministic rules and ML models. The system classifies plans into ALLOW, CONFIRM, REVISE, or BLOCK.

## Structure
- `backend/app/`: FastAPI application and core logic
- `backend/training/`: Offline data generation and ML model training
- `frontend/`: Streamlit dashboard
- `tests/`: Automated test suite
- `data/`: Local dataset storage (not committed)
- `artifacts/`: Model binaries and metrics (not committed)

## Setup and Run (Windows PowerShell)

```powershell
# Create and activate virtual environment
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements-dev.txt

# Run the API
make run-api

# Run the UI (in a new terminal, activate venv first)
make run-ui

# Run tests
make test
```

## Make Targets
- `setup`, `run-api`, `run-ui`, `test`, `lint`, `format`
- `data`, `train`, `eval` (stubs)
- `docker-up`, `docker-down`

Status: Skeleton only: no logic, data, or models yet.
