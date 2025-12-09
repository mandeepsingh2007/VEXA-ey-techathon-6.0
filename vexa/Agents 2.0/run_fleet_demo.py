# run_fleet_demo.py

import asyncio

from agents.master_agent import MasterAgent


async def main():
    master = MasterAgent()

    # Single vehicle (existing behaviour)
    print("Processing single vehicle VH-1001...")
    single_result = master.process_vehicle("VH-1001")
    print(f"Urgency: {single_result['urgency']}")
    print(f"Booking Info: {single_result['booking_info']}\n")

    # Fleet demo
    print("Processing fleet of 10 vehicles...")
    fleet_ids = [f"VH-{1000 + i}" for i in range(10)]
    fleet_result = await master.process_fleet_batch(fleet_ids)

    print("\n=== FLEET SUMMARY ===")
    print(f"  Total vehicles     : {fleet_result['total_vehicles']}")
    print(f"  CRITICAL           : {fleet_result['critical_count']}")
    print(f"  HIGH urgency       : {fleet_result['high_urgency_count']}")
    print(f"  Appointments booked: {fleet_result['appointments_booked']}")
    print(f"  Booking success %  : {fleet_result['success_rate'] * 100:.1f}%")
    print(f"  Top failing parts  : {fleet_result['top_failing_parts']}")
    print(f"  Service load       : {fleet_result['service_center_load']}")


if __name__ == "__main__":
    asyncio.run(main())
