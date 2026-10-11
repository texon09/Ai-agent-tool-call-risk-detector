"""Read-only model metrics endpoint handler (route registration belongs to P4)."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

from app.schemas import MetricsResponse, ModelMetrics
from fastapi import APIRouter

router = APIRouter()
REPO_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_METRICS_PATH = REPO_ROOT / "artifacts" / "metrics" / "results.json"


def _number(metrics: dict[str, Any], key: str) -> float | None:
    value = metrics.get(key)
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


@router.get("/metrics", response_model=MetricsResponse)
async def get_metrics() -> MetricsResponse:
    """Return per-model metrics, or an explicit unavailable response."""
    report_path = Path(os.getenv("MODEL_METRICS_PATH", str(DEFAULT_METRICS_PATH)))
    if not report_path.is_file():
        return MetricsResponse(models={}, available=False, detail="Metrics report is not available")
    try:
        report = json.loads(report_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError):
        return MetricsResponse(
            models={}, available=False, detail="Metrics report could not be read"
        )

    source = report.get("models", report) if isinstance(report, dict) else {}
    models: dict[str, ModelMetrics] = {}
    for name, raw_metrics in source.items():
        if not isinstance(raw_metrics, dict):
            continue
        values = {
            key: _number(raw_metrics, key)
            for key in ("f1", "precision", "recall", "auroc", "latency_ms")
        }
        if all(value is not None for value in values.values()):
            models[str(name)] = ModelMetrics(**values)
    if not models:
        return MetricsResponse(
            models={}, available=False, detail="Report has no complete per-model metrics"
        )
    return MetricsResponse(models=models, available=True)
