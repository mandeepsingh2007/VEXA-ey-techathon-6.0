# agents/driver_behavior_agent.py

from typing import List, Dict, Any, Optional
from datetime import datetime
from models import TelematicsEvent


class DriverBehaviorCoachAgent:
    """
    Driver Behavior Coach Agent

    Instead of generic advice, this agent looks at recent telematics
    events and derives concrete driver behaviour metrics, such as:

    - harsh braking count
    - rapid acceleration count
    - high-speed incidents
    - excessive idling time

    It accepts a list of TelematicsEvent (Pydantic) or dicts with
    equivalent keys.
    """

    def __init__(self) -> None:
        # Thresholds can be tuned based on domain calibration
        self.BRAKE_PRESSURE_THRESHOLD = 0.7   # fraction of max braking
        self.ACCEL_THRESHOLD = 1.5            # m/s^2 (example)
        self.SPEED_THRESHOLD = 100.0          # km/h
        self.IDLE_SPEED_THRESHOLD = 2.0       # km/h considered "stopped"
        self.IDLE_MIN_DURATION_SEC = 30       # how long before we call it "excessive idling"

    # ------------------------------------------------------------------
    # Internal: normalize a single event to a dictionary
    # ------------------------------------------------------------------
    def _event_to_dict(self, ev: Any) -> Dict[str, Any]:
        """
        Convert TelematicsEvent (Pydantic) or dict into a plain dict
        with known keys. If we can't parse, return {}.
        """
        if hasattr(ev, "model_dump"):  # Pydantic model
            data = ev.model_dump()
        elif isinstance(ev, dict):
            data = ev
        else:
            return {}

        return data

    # ------------------------------------------------------------------
    # Core behaviour analysis
    # ------------------------------------------------------------------
    def analyze_events(self, events: List[Any]) -> Dict[str, float]:
        harsh_brakes = 0
        rapid_acc = 0
        high_speed_incidents = 0
        total_idle_time_sec = 0.0

        idle_start: Optional[datetime] = None

        # We assume events are in chronological order. If not, we can
        # sort them by timestamp.
        for ev in events:
            data = self._event_to_dict(ev)
            if not data:
                continue

            # --- Extract fields using your actual TelematicsEvent model ---
            speed = float(data.get("speed_kmph", 0.0))
            brake_pressure = float(data.get("brake_pedal_pressure", 0.0))
            accel_long = float(data.get("accel_longitudinal", 0.0))
            ts_raw = data.get("timestamp")

            # Parse timestamp
            if isinstance(ts_raw, datetime):
                ts = ts_raw
            elif isinstance(ts_raw, str):
                try:
                    ts = datetime.fromisoformat(ts_raw)
                except Exception:
                    # If timestamp cannot be parsed, skip idle calculations
                    ts = None
            else:
                ts = None

            # --- Harsh braking detection ---
            if brake_pressure >= self.BRAKE_PRESSURE_THRESHOLD:
                harsh_brakes += 1

            # --- Rapid acceleration detection ---
            if accel_long >= self.ACCEL_THRESHOLD:
                rapid_acc += 1

            # --- High-speed incidents ---
            if speed >= self.SPEED_THRESHOLD:
                high_speed_incidents += 1

            # --- Idling detection ---
            if ts is not None:
                if speed <= self.IDLE_SPEED_THRESHOLD:
                    # Vehicle considered "idle" or nearly stopped
                    if idle_start is None:
                        idle_start = ts
                else:
                    # Vehicle moving now, end of any idle period
                    if idle_start is not None:
                        idle_duration = (ts - idle_start).total_seconds()
                        if idle_duration >= self.IDLE_MIN_DURATION_SEC:
                            total_idle_time_sec += idle_duration
                        idle_start = None

        # Edge: if still idling at the end, we could close it using last ts,
        # but for the demo it's fine to ignore that small tail.

        return {
            "harsh_braking_count": harsh_brakes,
            "rapid_accel_count": rapid_acc,
            "high_speed_incidents": high_speed_incidents,
            "excessive_idle_seconds": total_idle_time_sec,
        }

    # ------------------------------------------------------------------
    # Public API: return a driver behaviour summary string
    # ------------------------------------------------------------------
    def run(self, events: List[Any]) -> str:
        """
        Main entry point: takes a list of TelematicsEvent (or dicts)
        and returns a human-readable summary of driving behaviour.
        """
        metrics = self.analyze_events(events)

        lines: List[str] = []
        lines.append("⚙️ Driver Behaviour Summary (last window):")

        hb = metrics["harsh_braking_count"]
        ra = metrics["rapid_accel_count"]
        hs = metrics["high_speed_incidents"]
        idle_sec = metrics["excessive_idle_seconds"]
        idle_min = idle_sec / 60.0 if idle_sec > 0 else 0.0

        # Harsh braking
        if hb > 0:
            severity = "⚠️ High" if hb >= 5 else "ℹ️ Moderate"
            lines.append(f"- Harsh braking events: {hb} ({severity})")
        else:
            lines.append("- Harsh braking events: 0 (✅ Good)")

        # Rapid acceleration
        if ra > 0:
            severity = "⚠️ High" if ra >= 5 else "ℹ️ Moderate"
            lines.append(f"- Rapid acceleration events: {ra} ({severity})")
        else:
            lines.append("- Rapid acceleration events: 0 (✅ Smooth driving)")

        # High-speed incidents
        if hs > 0:
            lines.append(f"- High-speed incidents (>{self.SPEED_THRESHOLD:.0f} km/h): {hs} (⚠️ Risky)")
        else:
            lines.append(f"- High-speed incidents (>{self.SPEED_THRESHOLD:.0f} km/h): 0 (✅ Safe speeds)")

        # Excessive idling
        if idle_sec > 0:
            lines.append(f"- Excessive idling time: {idle_min:.1f} minutes (ℹ️ Consider reducing idle)")
        else:
            lines.append("- Excessive idling time: 0 minutes (✅ Efficient)")

        lines.append("📝 Tip: Smoother acceleration & braking can extend brake, tyre and engine life.")

        return "\n".join(lines)
