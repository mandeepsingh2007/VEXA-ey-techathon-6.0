from datetime import datetime, UTC
from agents.customer_engagement_agent import CustomerEngagementAgent
from models import HealthSummary, HealthScore


def make_test_summary():
    return HealthSummary(
        vehicle_id="VH-DEMO",
        timestamp=datetime.now(UTC).isoformat(),
        component_health=[
            HealthScore(component="brake_pad", health_score=0.0, risk_level="HIGH"),
            HealthScore(component="tire", health_score=0.10, risk_level="HIGH"),
            HealthScore(component="engine", health_score=0.20, risk_level="HIGH"),
            HealthScore(component="battery", health_score=0.90, risk_level="LOW"),
        ],
    )


def main():
    summary = make_test_summary()
    dtc_codes = ["P0300"]

    agent = CustomerEngagementAgent()
    result = agent.run(summary, dtc_codes)

    print("\n=== Owner Message ===\n")
    print(result["text"])

    print("\n=== Voice Files ===")
    print(result["audio_files"])


if __name__ == "__main__":
    main()
