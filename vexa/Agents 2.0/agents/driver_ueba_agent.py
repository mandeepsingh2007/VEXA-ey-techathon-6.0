# agents/driver_ueba_agent.py

from __future__ import annotations

from typing import List, Dict, Any
from datetime import datetime

from models import TelematicsEvent
from database import DatabaseManager


class DriverUEBAAgent:
    """
    Lightweight UEBA for driver behaviour.

    Uses telematics window to:
      - detect aggressive acceleration
      - detect harsh braking
      - detect speeding
    and compute a simple "safety score".
    """

    def __init__(self, db: DatabaseManager) -> None:
        self.db = db

    def detect_driver_anomalies(
        self,
        driver_id: str,
        events: List[TelematicsEvent],
    ) -> Dict[str, Any]:
        if not events:
            return {
                "driver_id": driver_id,
                "metrics": {},
                "anomalies": [],
                "safety_score": 10.0,
                "timestamp": datetime.utcnow().isoformat(),
            }

        metrics = self._compute_metrics(events)
        anomalies: List[Dict[str, Any]] = []

        hb = metrics["harsh_brake_events"]
        ha = metrics["harsh_accel_events"]
        sv = metrics["speed_violations"]

        # Very simple "expected" values for this trip/window
        baseline_hb = max(3, metrics["total_events"] * 0.1)
        baseline_ha = max(3, metrics["total_events"] * 0.1)
        baseline_sv = max(1, metrics["total_events"] * 0.02)

        if hb > baseline_hb * 1.5:
            sev = self._severity(hb, baseline_hb)
            anomalies.append(
                {
                    "type": "DRIVER_HARSH_BRAKING",
                    "severity": sev,
                    "risk_level": "HIGH" if sev >= 7 else "MEDIUM",
                    "context": f"Driver used harsh braking {hb} times (baseline ~{baseline_hb:.1f})",
                }
            )

        if ha > baseline_ha * 1.5:
            sev = self._severity(ha, baseline_ha)
            anomalies.append(
                {
                    "type": "DRIVER_AGGRESSIVE_ACCELERATION",
                    "severity": sev,
                    "risk_level": "MEDIUM" if sev < 8 else "HIGH",
                    "context": f"Driver accelerated aggressively {ha} times (baseline ~{baseline_ha:.1f})",
                }
            )

        if sv > baseline_sv * 2:
            sev = self._severity(sv, baseline_sv)
            anomalies.append(
                {
                    "type": "DRIVER_SPEEDING",
                    "severity": sev,
                    "risk_level": "HIGH",
                    "context": f"Driver had {sv} high-speed events (>100 km/h) (baseline ~{baseline_sv:.1f})",
                }
            )

        # Safety score: start at 10, subtract based on anomalies
        if anomalies:
            avg_sev = sum(a["severity"] for a in anomalies) / len(anomalies)
            safety_score = max(0.0, 10.0 - avg_sev)
        else:
            safety_score = 10.0

        result = {
            "driver_id": driver_id,
            "metrics": metrics,
            "anomalies": anomalies,
            "safety_score": safety_score,
            "timestamp": datetime.utcnow().isoformat(),
        }

        self.db.log_driver_anomalies(driver_id, anomalies)

        return result

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    def _compute_metrics(self, events: List[TelematicsEvent]) -> Dict[str, Any]:
        total = len(events)
        harsh_brake_events = 0
        harsh_accel_events = 0
        speed_violations = 0

        for ev in events:
            harsh_brake_events += int(ev.hard_brake_events_last_10min)
            harsh_accel_events += int(ev.harsh_accel_events_last_10min)
            if ev.speed_kmph > 100:
                speed_violations += 1

        return {
            "total_events": total,
            "harsh_brake_events": harsh_brake_events,
            "harsh_accel_events": harsh_accel_events,
            "speed_violations": speed_violations,
        }

    def _severity(self, actual: float, baseline: float) -> float:
        if baseline <= 0:
            return min(10.0, float(actual))
        ratio = actual / baseline
        if ratio < 1.2:
            return 2.0
        if ratio < 1.5:
            return 4.0
        if ratio < 2.0:
            return 6.0
        if ratio < 3.0:
            return 8.0
        return 10.0
