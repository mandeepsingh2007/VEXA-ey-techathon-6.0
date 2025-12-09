from typing import Dict, List
from models import DemandForecast, CenterComponentForecast, HealthSummary


def forecast_demand_for_center(
    center_id: str,
    horizon_days: int,
    vehicle_to_center: Dict[str, str],
    health_summaries: List[HealthSummary],
) -> DemandForecast:
    counts: Dict[str, float] = {}

    for summary in health_summaries:
        assigned_center = vehicle_to_center.get(summary.vehicle_id)
        if assigned_center != center_id:
            continue

        for h in summary.component_health:
            if h.eta_km is None and h.eta_days is None:
                continue

            risk_wt = {"LOW": 0.1, "MEDIUM": 0.5, "HIGH": 0.9}.get(h.risk_level, 0.1)

            if h.eta_days is not None:
                eta = h.eta_days
            elif h.eta_km is not None:
                eta = h.eta_km / 40.0  # assume 40 km/day
            else:
                eta = horizon_days + 1

            if eta <= horizon_days and risk_wt > 0.1:
                counts[h.component] = counts.get(h.component, 0.0) + risk_wt

    predictions: List[CenterComponentForecast] = [
        CenterComponentForecast(component=c, predicted_jobs=int(round(v)))
        for c, v in counts.items()
    ]

    return DemandForecast(
        center_id=center_id,
        horizon_days=horizon_days,
        predictions=predictions,
    )
