from typing import Dict, List

from synthetic_data import generate_stream_dataset
from window_store import TelematicsWindowManager
from data_analysis import run_data_analysis_streaming, run_demand_forecast
from models import HealthSummary, DemandForecast


def main():
    dataset = generate_stream_dataset(num_vehicles=5)
    window_manager = TelematicsWindowManager(max_days=7)

    vehicle_to_center: Dict[str, str] = {
        vid: "CENTER-01" for vid in dataset.keys()
    }

    all_health_summaries: List[HealthSummary] = []

    print("=== STREAMING DEMO (rolling windows) ===\n")

    for vid, data in dataset.items():
        maint = data["maintenance"]
        events = data["events"]

        latest_summary: HealthSummary | None = None
        for e in events:
            latest_summary = run_data_analysis_streaming(
                event=e,
                maintenance_history=maint,
                window_manager=window_manager,
            )

        if latest_summary:
            all_health_summaries.append(latest_summary)
            print(f"Vehicle {latest_summary.vehicle_id} final component health:")
            for c in latest_summary.component_health:
                print(
                    f"  - {c.component}: score={c.health_score:.2f}, "
                    f"risk={c.risk_level}, eta_km={c.eta_km}"
                )
            print()

    forecasts: List[DemandForecast] = run_demand_forecast(
        center_ids=["CENTER-01"],
        horizon_days=30,
        vehicle_to_center=vehicle_to_center,
        health_summaries=all_health_summaries,
    )

    for df in forecasts:
        print(f"Center {df.center_id} 30-day forecast:")
        for p in df.predictions:
            print(f"  - {p.component}: {p.predicted_jobs} jobs")
        print("-" * 40)


if __name__ == "__main__":
    main()
