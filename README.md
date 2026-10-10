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
- `validate-data`, `train`, `eval`
- `docker-up`, `docker-down`

## Training and evaluation

### Requirements
Ensure you have the exact following library versions installed:
`numpy==2.4.6`, `pandas==3.0.6`, `scikit-learn==1.9.1`, `xgboost==3.2.0`, `shap==0.51.0`, `joblib==1.6.0`.

### Data
Data files are expected in `data/processed/`. Features files must strictly contain the 42 feature columns first (in the exact order of the feature list), followed by metadata columns: `plan_id`, `task_id`, `label`, `family`, `difficulty`.
Data, models, and metrics are never committed to version control; they are shared via drive.

### Pipeline Commands
1. **Validate Data**: `make validate-data`
2. **Train Models**: `make train` (defaults to `v2`)
3. **Evaluate**: `make eval` (defaults to evaluating `v2`)

**Important Notes:**
- The test evaluation is run-once. The `--force` flag on the evaluation script is for exceptional cases only and its use must be logged.
- Models located in `artifacts/models/v2` use tie-aware thresholds to strictly enforce safe False Positive Rates (FPR).
