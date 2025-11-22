# storage.py
"""
Health storage layer for Smart Health Journal Agent.

This module encapsulates how health data (symptoms & medications)
is stored and retrieved. Currently uses in-memory storage, but
can be swapped for Firestore/DB later without touching agent logic.
"""

from __future__ import annotations
from datetime import datetime
from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)


class HealthStore:
    """
    In-memory storage for health data.

    Design:
    - Keeps symptoms and medications in simple Python lists.
    - Adds timestamps to all entries.
    - Provides helper methods to retrieve recent items.

    In production, this could be replaced with:
    - Firestore
    - Cloud SQL
    - Local database

    without changing agent/tool code.
    """

    def __init__(self) -> None:
        self.symptoms: List[Dict[str, Any]] = []
        self.medications: List[Dict[str, Any]] = []
        logger.info("HealthStore initialized")

    # ---------- Symptom methods ----------

    def add_symptom(self, data: Dict[str, Any]) -> None:
        """Add symptom entry with automatic logging."""
        self.symptoms.append(data)
        logger.info(
            "Symptom added: %s (severity: %s)",
            data.get("symptom"),
            data.get("severity"),
        )

    def get_symptoms(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Retrieve recent symptoms with limit."""
        results = self.symptoms[-limit:]
        logger.info("Retrieved %d symptoms", len(results))
        return results

    # ---------- Medication methods ----------

    def add_medication(self, data: Dict[str, Any]) -> None:
        """Add medication entry with automatic logging."""
        self.medications.append(data)
        logger.info(
            "Medication tracked: %s (%s)",
            data.get("medication"),
            data.get("dosage"),
        )

    def get_medications(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Retrieve recent medications with limit."""
        results = self.medications[-limit:]
        logger.info("Retrieved %d medications", len(results))
        return results


# Global store instance used by tools & agents
store = HealthStore()