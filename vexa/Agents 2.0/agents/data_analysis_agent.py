from typing import List

from window_store import TelematicsWindowManager
from data_analysis import run_data_analysis_streaming
from models import TelematicsEvent, MaintenanceRecord, HealthSummary


class DataAnalysisAgent:
    """
    Consumes streaming events + maintenance history and
    outputs rolling HealthSummary per vehicle.
    """

    def __init__(self, window_days: int = 7):
        self.window_manager = TelematicsWindowManager(max_days=window_days)

    def handle_event(
        self,
        event: TelematicsEvent,
        maintenance_history: List[MaintenanceRecord],
    ) -> HealthSummary:
        summary = run_data_analysis_streaming(
            event=event,
            maintenance_history=maintenance_history,
            window_manager=self.window_manager,
        )
        return summary
