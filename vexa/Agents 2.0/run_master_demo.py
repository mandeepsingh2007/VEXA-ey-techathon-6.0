from agents.master_agent import MasterAgent


def main():
    master = MasterAgent()
    vehicle_id = "VH-1001"

    result = master.process_vehicle(vehicle_id)

    print("\n=== MASTER AGENT END-TO-END DEMO ===\n")

    # Health summary
    print(">> Health Summary (from Data Analysis Agent)\n")
    for c in result["health_summary"]["component_health"]:
        print(
            f"- {c['component']}: score={c['health_score']:.2f}, "
            f"risk={c['risk_level']}, eta_km={c['eta_km']}"
        )

    # Diagnosis
    print("\n>> Internal Diagnostic Report (Diagnosis Agent)\n")
    print(result["diagnosis_report"])

    # Driver behaviour
    print("\n>> Driver Coaching Tips (Driver Behavior Coach Agent)\n")
    print(result["driver_tips"])

    # Booking proposal (not auto-booked)
    booking_info = result.get("booking_info")
    urgency = result.get("urgency")

    if booking_info:
        print("\n>> Booking Proposal (Scheduling + Spare Parts Agents)\n")
        status = booking_info.get("status")
        slot = booking_info.get("slot_suggestion") or {}
        reservation = booking_info.get("reservation") or {}

        print(f"Status: {status}")

        if slot:
            print(
                f"Suggested slot: {slot.get('start')} → {slot.get('end')} "
                f"({slot.get('timezone')})"
            )
        else:
            print("No slot suggestion available.")

        if reservation:
            print(
                f"Part candidate: {reservation.get('article_no')} "
                f"for {reservation.get('component_type')} "
                f"(available={reservation.get('available')})"
            )

        print(
            "\n(Note: This is NOT auto-booked. "
            "Voice/chat agent should ask owner: 'Do you confirm this slot? (YES/NO)')"
        )
    else:
        if urgency in ("CRITICAL", "HIGH"):
            print(
                "\n>> Booking Info: urgent case but no spare parts/slot proposal "
                "(escalate to human).\n"
            )
        else:
            print(
                "\n>> Booking Info: no auto-booking for non-urgent case "
                "(owner can request service manually).\n"
            )

    # Customer-facing message
    print("\n>> Customer-facing Message (Customer Engagement Agent)\n")
    text = result["customer_message"]
    audio = result["customer_message_audio"]

    print("ENGLISH:\n")
    print(text.get("english", ""))
    print("\nHINDI:\n")
    print(text.get("hindi", ""))

    print("\nVoice Files (primary interface):")
    print(audio)

    # UEBA report
    print("\n>> UEBA Anomaly Report\n")
    for event in result["ueba_report"]["events"]:
        print(event)
    print("Anomalies:", result["ueba_report"]["anomalies"])

    # Manufacturing insights
    print("\n>> Manufacturing Quality Insights\n")
    print(result["manufacturing_insights"])


if __name__ == "__main__":
    main()
