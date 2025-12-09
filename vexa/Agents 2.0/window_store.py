from collections import deque
from datetime import datetime, timedelta
from typing import Dict, List, Optional

from models import TelematicsEvent


def parse_ts(ts: str) -> datetime:
    return datetime.fromisoformat(ts)


class VehicleWindowStore:
    """Rolling buffer of events for a vehicle (last N days)."""

    def __init__(self, max_days: int = 7):
        self.max_days = max_days
        self.events: deque[TelematicsEvent] = deque()

    def add_event(self, event: TelematicsEvent) -> None:
        self.events.append(event)
        latest_ts = parse_ts(event.timestamp)
        cutoff = latest_ts - timedelta(days=self.max_days)

        while self.events and parse_ts(self.events[0].timestamp) < cutoff:
            self.events.popleft()

    def get_events(self) -> List[TelematicsEvent]:
        return list(self.events)


class TelematicsWindowManager:
    """Manages a rolling window store for each vehicle."""

    def __init__(self, max_days: int = 7):
        self.max_days = max_days
        self._stores: Dict[str, VehicleWindowStore] = {}

    def add_event(self, event: TelematicsEvent) -> VehicleWindowStore:
        vid = event.vehicle_id
        if vid not in self._stores:
            self._stores[vid] = VehicleWindowStore(max_days=self.max_days)
        store = self._stores[vid]
        store.add_event(event)
        return store

    def get_store(self, vehicle_id: str) -> Optional[VehicleWindowStore]:
        return self._stores.get(vehicle_id)
