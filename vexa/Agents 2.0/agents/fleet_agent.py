# agents/fleet_agent.py

from __future__ import annotations

import asyncio
from typing import List, Dict, Any
from collections import defaultdict


class FleetAgent:
    """
    Fleet-level wrapper around MasterAgent.

    - Processes multiple vehicles in parallel (batched)
    - Calls MasterAgent.process_vehicle(..., enable_voice=False) to avoid TTS load
    - Returns aggregated analytics for dashboards / fleet ops
    """

    def __init__(self, master_agent) -> None:
        self.master_agent = master_agent

    async def process_fleet(self, vehicle_ids: List[str]) -> Dict[str, Any]:
        """Process vehicles in parallel (batched to avoid API throttling)."""
        results: Dict[str, Any] = {}
        errors: Dict[str, str] = {}

        BATCH_SIZE = 3

        for i in range(0, len(vehicle_ids), BATCH_SIZE):
            batch = vehicle_ids[i:i + BATCH_SIZE]

            batch_results = await asyncio.gather(
                *[
                    asyncio.to_thread(self._safe_process_vehicle, vid, errors)
                    for vid in batch
                ]
            )

            for vid, res in zip(batch, batch_results):
                if res is not None:
                    results[vid] = res

        return self._fleet_summary(results, errors)

    # -----------------------------------------------------------
    def _safe_process_vehicle(self, vehicle_id: str, errors: Dict[str, str]) -> Any:
        """
        Call master_agent.process_vehicle safely.

        - Disables TTS via enable_voice=False
        - Catches exceptions so one bad vehicle doesn't kill the fleet run
        """
        try:
            return self.master_agent.process_vehicle(vehicle_id, enable_voice=False)
        except Exception as e:
            errors[vehicle_id] = str(e)
            return None

    # -----------------------------------------------------------
    def _fleet_summary(self, results: Dict[str, Any], errors: Dict[str, str]) -> Dict[str, Any]:
        """Aggregate fleet-level insights safely."""
        total = len(results) + len(errors)

        critical = []
        high = []
        booked = []

        for res in results.values():
            urgency = res.get("urgency", "LOW")
            if urgency == "CRITICAL":
                critical.append(res)
            elif urgency == "HIGH":
                high.append(res)

            if res.get("booking_info"):
                booked.append(res)

        return {
            "total_vehicles": total,
            "processed_ok": len(results),
            "failed": list(errors.keys()),
            "critical_count": len(critical),
            "high_urgency_count": len(high),
            "appointments_booked": len(booked),
            "success_rate": len(booked) / len(results) if results else 0.0,
            "top_failing_parts": self._top_parts(results),
            "service_center_load": self._load_distribution(booked),
        }

    def _top_parts(self, results: Dict[str, Any]) -> List[tuple]:
        """Find most commonly failing parts across fleet."""
        part_counts = defaultdict(int)
        for res in results.values():
            hs = res.get("health_summary", {})
            for ch in hs.get("component_health", []):
                if ch.get("risk_level") == "HIGH":
                    part_counts[ch.get("component")] += 1

        return sorted(part_counts.items(), key=lambda x: x[1], reverse=True)[:5]

    def _load_distribution(self, bookings: List[Dict[str, Any]]) -> Dict[str, int]:
        """Simple load metric based on 'timezone' or center field in slot."""
        centers = defaultdict(int)
        for res in bookings:
            slot = res.get("booking_info", {}).get("slot", {}) if "booking_info" in res else res.get("slot", {})
            center = slot.get("timezone", "default")
            centers[center] += 1
        return dict(centers)
