# test_api.py

from __future__ import annotations

from datetime import datetime, timedelta, timezone

from agents.scheduling_agent import SchedulingAgent
from agents.spare_parts_agent import SparePartsAgent


def test_nylas_scheduler() -> None:
    print("=== Testing Nylas SchedulingAgent ===")
    try:
        agent = SchedulingAgent()
    except Exception as e:
        print(f"[SKIP] Could not init SchedulingAgent: {e}")
        return

    now = datetime.now(timezone.utc)
    try:
        slots = agent.get_available_slots(
            start=now,
            end=now + timedelta(days=2),
            duration_minutes=30,
        )
        print(f"Found {len(slots)} candidate slots.")
        if slots:
            print("First slot:", slots[0].to_dict())
    except Exception as e:
        print(f"[ERROR] Nylas availability call failed: {e}")


def test_tecdoc_parts() -> None:
    print("\n=== Testing TecDoc SparePartsAgent ===")
    try:
        agent = SparePartsAgent()
    except Exception as e:
        print(f"[SKIP] Could not init SparePartsAgent: {e}")
        return

    vehicle_id = "VH-1000"
    component = "brake_pad"

    try:
        available = agent.is_available_for_vehicle(vehicle_id, component_type=component, qty=1)
        reservation = agent.reserve_for_vehicle(vehicle_id, component_type=component, qty=1)
        print("Available:", available)
        print("Reservation payload:", reservation)
    except Exception as e:
        print(f"[ERROR] TecDoc vehicle+parts search failed: {e}")


if __name__ == "__main__":
    test_nylas_scheduler()
    test_tecdoc_parts()
