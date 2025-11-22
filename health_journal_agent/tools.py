# tools.py
"""
Custom tool functions for Smart Health Journal Agent.

These tools encapsulate business logic for:
- logging symptoms
- tracking medications
- analyzing patterns
- generating health summaries

They operate on the shared HealthStore instance from storage.py.
"""

from datetime import datetime
import logging
from typing import Dict, Any

from .storage import store

logger = logging.getLogger(__name__)


def log_symptom(symptom_name: str, severity: int, notes: str = "") -> Dict[str, Any]:
    """
    Logs a symptom with severity rating.

    Returns:
        Success: {"status": "success", "message": "..."}
        Error:   {"status": "error", "error_message": "..."}
    """
    logger.info("log_symptom called: %s, severity=%s", symptom_name, severity)

    # Input validation
    if not 1 <= severity <= 10:
        logger.warning("Invalid severity value: %s", severity)
        return {
            "status": "error",
            "error_message": "Severity must be between 1 and 10",
        }

    data = {
        "symptom": symptom_name,
        "severity": severity,
        "notes": notes,
        "timestamp": datetime.now().isoformat(),
    }

    store.add_symptom(data)

    return {
        "status": "success",
        "message": f"Logged {symptom_name} (severity {severity})",
    }


def track_medication(
    medication_name: str, dosage: str, time_taken: str = ""
) -> Dict[str, Any]:
    """
    Tracks medication intake.

    Auto-fills current time if not provided.
    """
    logger.info("track_medication called: %s, dosage=%s", medication_name, dosage)

    if not time_taken:
        from datetime import datetime as _dt

        time_taken = _dt.now().strftime("%H:%M")
        logger.debug("Auto-filled time: %s", time_taken)

    data = {
        "medication": medication_name,
        "dosage": dosage,
        "time": time_taken,
        "timestamp": datetime.now().isoformat(),
    }

    store.add_medication(data)

    return {
        "status": "success",
        "message": f"Tracked {medication_name} ({dosage})",
    }


def analyze_patterns() -> Dict[str, Any]:
    """
    Analyzes symptom patterns and frequencies.
    """
    logger.info("analyze_patterns called")

    symptoms = store.get_symptoms()

    if not symptoms:
        logger.info("No symptoms available for analysis")
        return {"status": "no_data", "message": "No symptoms logged yet"}

    counts = {}
    severity_sums = {}

    for s in symptoms:
        name = s["symptom"]
        sev = s["severity"]
        counts[name] = counts.get(name, 0) + 1
        severity_sums[name] = severity_sums.get(name, 0) + sev

    patterns = []
    for name, count in counts.items():
        avg = round(severity_sums[name] / count, 1)
        patterns.append(
            {
                "symptom": name,
                "count": count,
                "avg_severity": avg,
            }
        )

    patterns.sort(key=lambda x: x["count"], reverse=True)

    logger.info("Analysis complete: %d unique symptoms found", len(patterns))

    return {
        "status": "success",
        "patterns": patterns,
        "total_entries": len(symptoms),
    }


def get_health_summary() -> Dict[str, Any]:
    """
    Generates comprehensive health summary for doctor visits.
    """
    logger.info("get_health_summary called")

    symptoms = store.get_symptoms()
    meds = store.get_medications()
    patterns = analyze_patterns()

    summary = f"Health Summary - {datetime.now().strftime('%Y-%m-%d')}\n"
    summary += "=" * 50 + "\n"
    summary += f"Symptoms logged: {len(symptoms)}\n"
    summary += f"Medications tracked: {len(meds)}\n"

    if patterns.get("status") == "success":
        summary += "\nTop symptoms:\n"
        for p in patterns["patterns"][:3]:
            summary += (
                f"  - {p['symptom']}: {p['count']}x "
                f"(avg severity {p['avg_severity']})\n"
            )

    logger.info("Health summary generated successfully")

    return {
        "status": "success",
        "summary": summary,
        "symptoms": symptoms,
        "medications": meds,
    }


__all__ = [
    "log_symptom",
    "track_medication",
    "analyze_patterns",
    "get_health_summary",
]