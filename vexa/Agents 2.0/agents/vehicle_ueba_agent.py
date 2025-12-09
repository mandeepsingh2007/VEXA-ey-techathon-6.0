# agents/vehicle_ueba_agent.py

from __future__ import annotations

from typing import List, Dict, Any
from datetime import datetime

from models import TelematicsEvent, HealthSummary
from database import DatabaseManager


class VehicleUEBAAgent:
    """
    Lightweight UEBA for vehicle behaviour & component health.

    - Uses a simple heuristic "baseline" derived from the current window.
    - Flags:
        * Harsh braking spike
        * Harsh acceleration spike
        * Speeding spike
        * Excessive idling
        * Critical component health
    """

    def __init__(self, db: DatabaseManager) -> None:
        self.db = db

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def detect_vehicle_anomalies(
        self,
        vehicle_id: str,
        events: List[TelematicsEvent],
        health_summary: HealthSummary,
    ) -> Dict[str, Any]:
        if not events:
            return {
                "vehicle_id": vehicle_id,
                "metrics": {},
                "anomalies": [],
                "overall_risk": "LOW",
                "timestamp": datetime.utcnow().isoformat(),
            }

        metrics = self._compute_metrics(events)
        anomalies: List[Dict[str, Any]] = []

        # --- Harsh braking spike ---
        hb = metrics["harsh_brake_events"]
        hb_baseline = max(5, metrics["total_events"] * 0.2)
        if hb > hb_baseline * 1.5:
            severity = self._severity_count_ratio(hb, hb_baseline)
            anomalies.append(
                {
                    "type": "HARSH_BRAKING_SPIKE",
                    "severity": severity,
                    "risk_level": "HIGH" if severity >= 7 else "MEDIUM",
                    "context": f"Harsh braking events: {hb} (baseline ~{hb_baseline:.1f})",
                }
            )

        # --- Harsh acceleration spike ---
        ha = metrics["harsh_accel_events"]
        ha_baseline = max(5, metrics["total_events"] * 0.2)
        if ha > ha_baseline * 1.5:
            severity = self._severity_count_ratio(ha, ha_baseline)
            anomalies.append(
                {
                    "type": "HARSH_ACCELERATION_SPIKE",
                    "severity": severity,
                    "risk_level": "MEDIUM" if severity < 8 else "HIGH",
                    "context": f"Harsh acceleration events: {ha} (baseline ~{ha_baseline:.1f})",
                }
            )

        # --- Speed violations ---
        sv = metrics["speed_violations"]
        sv_baseline = max(1, metrics["total_events"] * 0.05)
        if sv > sv_baseline * 2:
            severity = self._severity_count_ratio(sv, sv_baseline)
            anomalies.append(
                {
                    "type": "SPEED_VIOLATION_SPIKE",
                    "severity": severity,
                    "risk_level": "HIGH",
                    "context": f"Speeding incidents (>100 km/h): {sv} (baseline ~{sv_baseline:.1f})",
                }
            )

        # --- Idling ---
        idle = metrics["idling_events"]
        idle_baseline = max(2, metrics["total_events"] * 0.1)
        if idle > idle_baseline * 2:
            severity = self._severity_count_ratio(idle, idle_baseline)
            anomalies.append(
                {
                    "type": "EXCESSIVE_IDLING",
                    "severity": severity,
                    "risk_level": "LOW" if severity < 5 else "MEDIUM",
                    "context": f"Idling events: {idle} (baseline ~{idle_baseline:.1f})",
                }
            )

        # --- Component health critical ---
        for comp in health_summary.component_health:
            if comp.health_score <= 0.2:
                anomalies.append(
                    {
                        "type": "COMPONENT_HEALTH_CRITICAL",
                        "severity": 9 if comp.health_score <= 0.05 else 7,
                        "risk_level": "CRITICAL"
                        if comp.health_score <= 0.05
                        else "HIGH",
                        "context": f"{comp.component} health={comp.health_score:.2f}, risk={comp.risk_level}",
                    }
                )

        overall = self._overall_risk(anomalies)

        result = {
            "vehicle_id": vehicle_id,
            "metrics": metrics,
            "anomalies": anomalies,
            "overall_risk": overall,
            "timestamp": datetime.utcnow().isoformat(),
        }

        # Persist anomalies in DB for later dashboards
        self.db.log_vehicle_anomalies(vehicle_id, anomalies)

        return result

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------
    def _compute_metrics(self, events: List[TelematicsEvent]) -> Dict[str, Any]:
        total = len(events)

        harsh_brake_events = 0
        harsh_accel_events = 0
        speed_violations = 0
        idling_events = 0

        for ev in events:
            # Pydantic model → attributes
            harsh_brake_events += int(ev.hard_brake_events_last_10min)
            harsh_accel_events += int(ev.harsh_accel_events_last_10min)

            if ev.speed_kmph > 100:
                speed_violations += 1

            if ev.speed_kmph < 5 and ev.engine_rpm > 0:
                idling_events += 1

        return {
            "total_events": total,
            "harsh_brake_events": harsh_brake_events,
            "harsh_accel_events": harsh_accel_events,
            "speed_violations": speed_violations,
            "idling_events": idling_events,
        }

    def _severity_count_ratio(self, actual: float, baseline: float) -> float:
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

    def _overall_risk(self, anomalies: List[Dict[str, Any]]) -> str:
        if not anomalies:
            return "LOW"
        max_sev = max(a.get("severity", 0) for a in anomalies)
        if max_sev >= 9:
            return "CRITICAL"
        if max_sev >= 7:
            return "HIGH"
        if max_sev >= 4:
            return "MEDIUM"
        return "LOW"
