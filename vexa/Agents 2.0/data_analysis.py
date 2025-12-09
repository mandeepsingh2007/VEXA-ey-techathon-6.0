from typing import List, Dict

from models import (
    TelematicsEvent,
    MaintenanceRecord,
    HealthSummary,
    DemandForecast,
)
from feature_engineering import compute_windowed_features
from health_scoring import compute_all_components
from demand_forecasting import forecast_demand_for_center
from window_store import TelematicsWindowManager


def run_data_analysis_batch(
    telematics_events: List[TelematicsEvent],
    maintenance_history: List[MaintenanceRecord],
) -> HealthSummary:
    if not telematics_events:
        raise ValueError("No telematics events provided")

    features = compute_windowed_features(telematics_events, maintenance_history)
    component_scores = compute_all_components(features)
    latest_ts = sorted(telematics_events, key=lambda e: e.timestamp)[-1].timestamp
    vehicle_id = telematics_events[-1].vehicle_id

    return HealthSummary(
        vehicle_id=vehicle_id,
        timestamp=latest_ts,
        component_health=component_scores,
    )


def run_data_analysis_streaming(
    event: TelematicsEvent,
    maintenance_history: List[MaintenanceRecord],
    window_manager: TelematicsWindowManager,
) -> HealthSummary:
    store = window_manager.add_event(event)
    events = store.get_events()
    features = compute_windowed_features(events, maintenance_history)
    component_scores = compute_all_components(features)

    return HealthSummary(
        vehicle_id=event.vehicle_id,
        timestamp=event.timestamp,
        component_health=component_scores,
    )


def run_demand_forecast(
    center_ids: List[str],
    horizon_days: int,
    vehicle_to_center: Dict[str, str],
    health_summaries: List[HealthSummary],
) -> List[DemandForecast]:
    forecasts: List[DemandForecast] = []
    for cid in center_ids:
        df = forecast_demand_for_center(
            center_id=cid,
            horizon_days=horizon_days,
            vehicle_to_center=vehicle_to_center,
            health_summaries=health_summaries,
        )
        forecasts.append(df)
    return forecasts
