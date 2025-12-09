import random
import uuid
from datetime import datetime, timedelta
from typing import List, Dict, Optional

from models import TelematicsEvent, MaintenanceRecord, ReplacedPart


def generate_vehicle_ids(n: int = 10) -> List[str]:
    return [f"VH-{1000 + i}" for i in range(n)]


def generate_telematics_stream(
    vehicle_id: str,
    start_odometer: float,
    num_events: int = 200,
    base_time: Optional[datetime] = None,
) -> List[TelematicsEvent]:
    if base_time is None:
        base_time = datetime.utcnow() - timedelta(hours=3)

    events: List[TelematicsEvent] = []
    odometer = start_odometer

    for i in range(num_events):
        delta_km = random.uniform(0.1, 2.5)
        odometer += delta_km
        speed = random.uniform(0, 110)
        city_mode = random.random() < 0.6
        driving_mode = "city" if city_mode else "highway"

        dtc_pool = ["P0300", "P0420", "P0171", "U0100"]
        dtc = []
        if random.random() < 0.03:
            dtc.append(random.choice(dtc_pool))

        hard_brakes = random.randint(0, 4)
        harsh_accel = random.randint(0, 4)

        event = TelematicsEvent(
            event_id=str(uuid.uuid4()),
            vehicle_id=vehicle_id,
            timestamp=(base_time + timedelta(minutes=i * 2)).isoformat(),
            odometer_km=odometer,
            engine_hours=100 + odometer / 40.0,
            speed_kmph=speed,
            accel_longitudinal=random.uniform(-3, 3),
            brake_pedal_pressure=random.uniform(0, 100),
            steering_angle_deg=random.uniform(-45, 45),
            engine_coolant_temp_c=random.uniform(75, 110),
            engine_oil_temp_c=random.uniform(80, 120),
            engine_rpm=int(random.uniform(800, 4500)),
            battery_voltage_v=random.uniform(11.8, 13.8),
            fuel_level_pct=random.uniform(10, 100),
            ambient_temp_c=random.uniform(10, 45),
            tire_pressure_fl_psi=random.uniform(28, 36),
            tire_pressure_fr_psi=random.uniform(28, 36),
            tire_pressure_rl_psi=random.uniform(28, 36),
            tire_pressure_rr_psi=random.uniform(28, 36),
            driving_mode=driving_mode,
            hard_brake_events_last_10min=hard_brakes,
            harsh_accel_events_last_10min=harsh_accel,
            dtc_codes=dtc,
        )
        events.append(event)

    return events


def generate_maintenance_history(
    vehicle_id: str,
    current_odometer: float,
) -> List[MaintenanceRecord]:
    history: List[MaintenanceRecord] = []

    brake_odo = current_odometer - random.uniform(8000, 20000)
    if brake_odo < 0:
        brake_odo = current_odometer * 0.2

    brake_record = MaintenanceRecord(
        record_id=str(uuid.uuid4()),
        vehicle_id=vehicle_id,
        service_date=(datetime.utcnow() - timedelta(days=180)).date().isoformat(),
        odometer_km=brake_odo,
        service_center_id="CENTER-01",
        complaint_desc="Routine service and brake inspection",
        dtc_at_intake=[],
        operations=["OP100", "OP200"],
        parts_replaced=[
            ReplacedPart(
                part_number="BRK-1234",
                component="brake_pad",
                qty=4,
                reason_code="wear",
            )
        ],
        warranty_flag=False,
        rca_code="normal_wear",
        capa_id=None,
    )
    history.append(brake_record)

    if random.random() < 0.4:
        battery_odo = current_odometer - random.uniform(5000, 15000)
        battery_record = MaintenanceRecord(
            record_id=str(uuid.uuid4()),
            vehicle_id=vehicle_id,
            service_date=(datetime.utcnow() - timedelta(days=365)).date().isoformat(),
            odometer_km=max(battery_odo, 0),
            service_center_id="CENTER-01",
            complaint_desc="Weak start, replaced battery",
            dtc_at_intake=["P0562"],
            operations=["OP300"],
            parts_replaced=[
                ReplacedPart(
                    part_number="BAT-5678",
                    component="battery",
                    qty=1,
                    reason_code="defect",
                )
            ],
            warranty_flag=True,
            rca_code="manufacturing_defect",
            capa_id="CAPA-2024-01",
        )
        history.append(battery_record)

    return history


def generate_stream_dataset(num_vehicles: int = 5) -> Dict[str, Dict[str, list]]:
    dataset: Dict[str, Dict[str, list]] = {}
    vehicles = generate_vehicle_ids(num_vehicles)
    for vid in vehicles:
        start_odo = random.uniform(10000, 60000)
        events = generate_telematics_stream(vid, start_odo, num_events=200)
        history = generate_maintenance_history(vid, events[-1].odometer_km)
        dataset[vid] = {
            "events": events,
            "maintenance": history,
        }
    return dataset


# Global counter for 3-state cycle simulation via modulo
_sim_cycle_counter = 0

def evolve_vehicle_state(last_event: TelematicsEvent) -> TelematicsEvent:
    """
    Cycles through 3 fixed states for predictable demo:
    1. Cruising (Steady)
    2. Accelerating (Sporty)
    3. Braking/Cornering (Dynamic)
    """
    global _sim_cycle_counter
    _sim_cycle_counter = (_sim_cycle_counter + 1) % 3
    
    new_time = datetime.utcnow()
    
    # Base values preserved
    odometer = last_event.odometer_km + 0.5
    fuel = max(5.0, last_event.fuel_level_pct - 0.1)
    
    if _sim_cycle_counter == 0:
        # State 1: Cruising (Normal)
        speed = 65.0
        rpm = 2100
        steering = 0.5
        brake = 0.0
        coolant = 90.0
        oil = 95.0
        mode = "NORMAL"
        
    elif _sim_cycle_counter == 1:
        # State 2: Accelerating (Sport)
        speed = 82.0
        rpm = 3400
        steering = -2.5
        brake = 0.0
        coolant = 92.5
        oil = 98.0
        mode = "SPORT"
        
    else:
        # State 3: Braking/Cornering (Normal)
        speed = 45.0
        rpm = 1500
        steering = 12.0
        brake = 35.0
        coolant = 89.0
        oil = 94.0
        mode = "NORMAL"

    return TelematicsEvent(
        event_id=str(uuid.uuid4()),
        vehicle_id=last_event.vehicle_id,
        timestamp=new_time.isoformat(),
        odometer_km=odometer,
        engine_hours=last_event.engine_hours + 0.01,
        speed_kmph=speed,
        accel_longitudinal=0.0,
        brake_pedal_pressure=brake,
        steering_angle_deg=steering,
        engine_coolant_temp_c=coolant,
        engine_oil_temp_c=oil,
        engine_rpm=rpm,
        battery_voltage_v=13.5, # Steady
        fuel_level_pct=fuel,
        ambient_temp_c=last_event.ambient_temp_c,
        tire_pressure_fl_psi=33.0,
        tire_pressure_fr_psi=33.0,
        tire_pressure_rl_psi=33.0,
        tire_pressure_rr_psi=33.0,
        driving_mode=mode,
        hard_brake_events_last_10min=0,
        harsh_accel_events_last_10min=0,
        dtc_codes=last_event.dtc_codes, 
    )
