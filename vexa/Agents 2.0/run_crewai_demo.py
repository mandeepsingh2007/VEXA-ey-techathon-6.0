from synthetic_data import generate_stream_dataset
from window_store import TelematicsWindowManager
from data_analysis import run_data_analysis_streaming
from models import HealthSummary
from crewai_agents import run_crewai_demo


def main():
    dataset = generate_stream_dataset(num_vehicles=1)
    vid, data = next(iter(dataset.items()))
    maint = data["maintenance"]
    events = data["events"]

    wm = TelematicsWindowManager(max_days=7)

    latest_summary: HealthSummary | None = None
    for e in events:
        latest_summary = run_data_analysis_streaming(
            event=e,
            maintenance_history=maint,
            window_manager=wm,
        )

    if latest_summary is None:
        print("No events processed.")
        return

    print("=== Health Summary ===")
    for c in latest_summary.component_health:
        print(
            f"- {c.component}: score={c.health_score:.2f}, "
            f"risk={c.risk_level}, eta_km={c.eta_km}"
        )
    print()

    dtc_codes = events[-1].dtc_codes or ["P0300"]

    print("=== CrewAI Diagnosis + Customer Message ===")
    final_message = run_crewai_demo(latest_summary, dtc_codes)
    print(final_message)


if __name__ == "__main__":
    main()
