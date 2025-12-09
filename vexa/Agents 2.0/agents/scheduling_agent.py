# agents/scheduling_agent.py

from __future__ import annotations

import os
from datetime import datetime, timedelta, timezone
from typing import Dict, Any, List, Optional

import requests
from dotenv import load_dotenv

load_dotenv()

NYLAS_API_KEY = os.getenv("NYLAS_API_KEY")
NYLAS_BASE_URL = os.getenv("NYLAS_BASE_URL", "https://api.us.nylas.com")
NYLAS_CALENDAR_ID = os.getenv("NYLAS_CALENDAR_ID")
DEFAULT_TZ = os.getenv("SERVICE_TZ", "Asia/Kolkata")


class SchedulingAgent:
    """
    Scheduling Agent using Nylas Availability API.

    - propose_slot(urgency) → finds a slot window depending on urgency tier
    - handle_appointment_declined() → auto-reschedules up to N times (then escalate)
    """

    def __init__(self) -> None:
        if not NYLAS_API_KEY or not NYLAS_CALENDAR_ID:
            print("[WARN] Nylas not fully configured; scheduling will be mocked.")
        self.session = requests.Session()
        self.session.headers.update(
            {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {NYLAS_API_KEY}",
            }
        )

    # ------------------------------------------------------------------
    # Core: propose slot based on urgency
    # ------------------------------------------------------------------
    def propose_slot(self, urgency: str, customer_email: Optional[str] = None) -> Dict[str, Any]:
        """
        Maps urgency to time window and asks Nylas for availability.

        CRITICAL: now → +6 hours
        HIGH:     now → +2 days
        MEDIUM:   +1 day → +7 days
        LOW:      +3 days → +14 days
        """
        now = datetime.now(timezone.utc)

        if urgency == "CRITICAL":
            start = now
            end = now + timedelta(hours=6)
        elif urgency == "HIGH":
            start = now
            end = now + timedelta(days=2)
        elif urgency == "MEDIUM":
            start = now + timedelta(days=1)
            end = now + timedelta(days=7)
        else:
            start = now + timedelta(days=3)
            end = now + timedelta(days=14)

        slots = self.get_available_slots(start, end, duration_minutes=30)

        slot = slots[0] if slots else None

        return {
            "slot": slot,
            "event": None,  # For now we only show slot; creating calendar events can be wired later
        }

    # ------------------------------------------------------------------
    # Nylas Availability API
    # ------------------------------------------------------------------
    def get_available_slots(
        self,
        start: datetime,
        end: datetime,
        duration_minutes: int = 30,
    ) -> List[Dict[str, Any]]:
        """
        Query Nylas for availability.

        Returns a simplified list of { start, end, timezone } or [] on failure.
        """
        if not NYLAS_API_KEY or not NYLAS_CALENDAR_ID:
            # Mocked slots
            return [
                {
                    "start": (start + timedelta(hours=1)).isoformat(),
                    "end": (start + timedelta(hours=1, minutes=duration_minutes)).isoformat(),
                    "participants": [],
                    "timezone": DEFAULT_TZ,
                }
            ]

        url = f"{NYLAS_BASE_URL}/v3/calendars/availability"

        body = {
            "calendars": [
                {
                    "id": NYLAS_CALENDAR_ID,
                    "time_slots": [
                        {
                            "start_time": int(start.timestamp()),
                            "end_time": int(end.timestamp()),
                        }
                    ],
                }
            ],
            "duration": duration_minutes,
            "interval": 15,
            "start_time": int(start.timestamp()),
            "end_time": int(end.timestamp()),
            "buffer": 0,
        }

        try:
            resp = self.session.post(url, json=body, timeout=30)
            resp.raise_for_status()
        except Exception as e:
            print(f"[ERROR] Nylas availability call failed: {e}")
            return []

        data = resp.json()
        slots_raw = data.get("time_slots", []) or data.get("availability", [])

        slots: List[Dict[str, Any]] = []
        for s in slots_raw:
            # Normalize slot format
            s_start = s.get("start_time") or s.get("start")
            s_end = s.get("end_time") or s.get("end")

            if isinstance(s_start, (int, float)):
                s_start = datetime.fromtimestamp(s_start, tz=timezone.utc).isoformat()
            if isinstance(s_end, (int, float)):
                s_end = datetime.fromtimestamp(s_end, tz=timezone.utc).isoformat()

            slots.append(
                {
                    "start": s_start,
                    "end": s_end,
                    "participants": [],
                    "timezone": DEFAULT_TZ,
                }
            )

        if slots:
            print(f"Found {len(slots)} candidate slots.")
            print("First slot:", slots[0])
        else:
            print("[WARN] No slots found from Nylas (or API failed). Falling back to mock.")
            # Fallback mock slot
            return [
                {
                    "start": (start + timedelta(hours=1)).isoformat(),
                    "end": (start + timedelta(hours=1, minutes=duration_minutes)).isoformat(),
                    "participants": [],
                    "timezone": DEFAULT_TZ,
                }
            ]

        return slots

    # ------------------------------------------------------------------
    # Appointment Decline Handler (Option 4 + 3 logic)
    # ------------------------------------------------------------------
    def handle_appointment_declined(
        self,
        booking_id: str,
        reason: Optional[str] = None,
        attempts: int = 1,
    ) -> Dict[str, Any]:
        """
        Handle customer appointment decline / cancellation with auto-reschedule.

        Policy (Option 4 + 3):
        - Try up to 3 automatic reschedules.
        - Each time: search for slots in next 3 days.
        - If no slot or attempts >= 3 → escalate for manual handling
          (including re-checking urgency with the driver).
        """
        print(f"[DECLINED] Booking {booking_id}: {reason} (attempt {attempts})")

        if attempts >= 3:
            return {
                "status": "escalate",
                "original_booking": booking_id,
                "reason": reason or "customer_declined",
                "attempts": attempts,
                "action": "contact_customer_manually_and_reassess_urgency",
            }

        alt_start = datetime.now(timezone.utc)
        alt_end = alt_start + timedelta(days=3)

        alt_slots = self.get_available_slots(
            start=alt_start,
            end=alt_end,
            duration_minutes=30,
        )

        if alt_slots:
            new_slot = alt_slots[0]
            return {
                "status": "rescheduled",
                "original_booking": booking_id,
                "new_slot": new_slot,
                "reason": reason or "customer_declined",
                "attempts": attempts,
            }
        else:
            return {
                "status": "escalate",
                "original_booking": booking_id,
                "reason": "no_alternative_slots",
                "attempts": attempts,
                "action": "contact_customer_manually_and_reassess_urgency",
            }
