from datetime import datetime, timedelta
from typing import List, Dict

from models import TelematicsEvent, MaintenanceRecord


def _parse_ts(ts: str) -> datetime:
    return datetime.fromisoformat(ts)


def _km_since_last_replacement(
    history: List[MaintenanceRecord],
    latest_odometer: float,
    component: str,
) -> float:
    last_odo = 0.0
    for r in history:
        for part in r.parts_replaced:
            if part.component == component and r.odometer_km > last_odo:
                last_odo = r.odometer_km
    if last_odo == 0:
        return latest_odometer
    return max(latest_odometer - last_odo, 0.0)


def _window_by_time(events: List[TelematicsEvent], days: int) -> List[TelematicsEvent]:
    if not events:
        return []
    events_sorted = sorted(events, key=lambda e: e.timestamp)
    latest_ts = _parse_ts(events_sorted[-1].timestamp)
    cutoff = latest_ts - timedelta(days=days)
    return [e for e in events_sorted if _parse_ts(e.timestamp) >= cutoff]


def _window_by_distance(
    events: List[TelematicsEvent],
    km_window: float,
) -> List[TelematicsEvent]:
    if not events:
        return []
    events_sorted = sorted(events, key=lambda e: e.odometer_km)
    latest_odo = events_sorted[-1].odometer_km
    min_odo = max(latest_odo - km_window, 0.0)
    return [e for e in events_sorted if e.odometer_km >= min_odo]


def _window_last_n_events(
    events: List[TelematicsEvent],
    n: int,
) -> List[TelematicsEvent]:
    return events[-n:] if len(events) > n else events[:]


def _approx_last_trips(events: List[TelematicsEvent], num_trips: int = 5) -> List[List[TelematicsEvent]]:
    """Crude approximation: treat blocks of events as trips."""
    if not events:
        return []
    events_sorted = sorted(events, key=lambda e: e.timestamp)
    block_size = max(1, len(events_sorted) // (num_trips * 2))
    trips: List[List[TelematicsEvent]] = []
    for i in range(0, len(events_sorted), block_size):
        trips.append(events_sorted[i: i + block_size])
    return trips[-num_trips:]


def _aggregate_basic_stats(events: List[TelematicsEvent]) -> Dict[str, float]:
    if not events:
        return {}

    n = len(events)
    speeds = [e.speed_kmph for e in events]
    brake_pressures = [e.brake_pedal_pressure for e in events]
    coolant = [e.engine_coolant_temp_c for e in events]
    oil = [e.engine_oil_temp_c for e in events]
    rpm = [e.engine_rpm for e in events]
    batt = [e.battery_voltage_v for e in events]

    avg_speed = sum(speeds) / n
    avg_brake_pressure = sum(brake_pressures) / n
    avg_coolant = sum(coolant) / n
    avg_oil = sum(oil) / n
    avg_rpm = sum(rpm) / n
    avg_battery_voltage = sum(batt) / n

    max_brake_pressure = max(brake_pressures)
    max_coolant = max(coolant)
    max_rpm = max(rpm)

    total_hard_brakes = sum(e.hard_brake_events_last_10min for e in events)
    total_harsh_accel = sum(e.harsh_accel_events_last_10min for e in events)
    dtc_count = sum(len(e.dtc_codes) for e in events)

    km_covered = max(events[-1].odometer_km - events[0].odometer_km, 1.0)
    hard_brakes_per_100km = (total_hard_brakes / km_covered) * 100.0

    city_events = sum(1 for e in events if e.driving_mode == "city")
    city_ratio = city_events / n

    overheat_events = sum(1 for e in events if e.engine_coolant_temp_c > 105)

    low_pressure_events = sum(
        1
        for e in events
        if (
            e.tire_pressure_fl_psi < 30
            or e.tire_pressure_fr_psi < 30
            or e.tire_pressure_rl_psi < 30
            or e.tire_pressure_rr_psi < 30
        )
    )
    low_tire_pressure_ratio = low_pressure_events / n

    harsh_index = (total_hard_brakes + total_harsh_accel) / n

    return {
        "avg_speed_kmph": avg_speed,
        "avg_brake_pressure": avg_brake_pressure,
        "avg_coolant_temp_c": avg_coolant,
        "avg_oil_temp_c": avg_oil,
        "avg_rpm": avg_rpm,
        "avg_battery_voltage_v": avg_battery_voltage,
        "max_brake_pressure": max_brake_pressure,
        "max_coolant_temp_c": max_coolant,
        "max_rpm": max_rpm,
        "hard_brakes_per_100km": hard_brakes_per_100km,
        "city_ratio": city_ratio,
        "overheat_events": float(overheat_events),
        "low_tire_pressure_ratio": low_tire_pressure_ratio,
        "harsh_accel_braking_index": harsh_index,
        "dtc_count": float(dtc_count),
    }


def compute_windowed_features(
    events: List[TelematicsEvent],
    history: List[MaintenanceRecord],
) -> Dict[str, float]:
    """
    Compute features using:
    - rolling 7-day window
    - rolling 500 km window
    - last 50 events
    - last 5 trips
    """
    if not events:
        raise ValueError("No events provided")

    events_sorted = sorted(events, key=lambda e: e.timestamp)
    latest = events_sorted[-1]
    latest_odo = latest.odometer_km

    win_7d = _window_by_time(events_sorted, days=7)
    win_500km = _window_by_distance(events_sorted, km_window=500.0)
    win_50 = _window_last_n_events(events_sorted, n=50)
    trips = _approx_last_trips(events_sorted, num_trips=5)

    stats_7d = _aggregate_basic_stats(win_7d)
    stats_500 = _aggregate_basic_stats(win_500km)
    stats_50 = _aggregate_basic_stats(win_50)

    trip_max_brake = []
    trip_harsh_indexes = []
    for t in trips:
        s = _aggregate_basic_stats(t)
        if s:
            trip_max_brake.append(s["max_brake_pressure"])
            trip_harsh_indexes.append(s["harsh_accel_braking_index"])

    max_brake_per_trip_avg = sum(trip_max_brake) / len(trip_max_brake) if trip_max_brake else 0.0
    harsh_index_last_trips_avg = sum(trip_harsh_indexes) / len(trip_harsh_indexes) if trip_harsh_indexes else 0.0

    km_since_brake_change = _km_since_last_replacement(
        history, latest_odo, component="brake_pad"
    )
    km_since_battery_change = _km_since_last_replacement(
        history, latest_odo, component="battery"
    )

    return {
        "latest_odometer_km": latest_odo,
        "hard_brakes_per_100km": stats_500.get("hard_brakes_per_100km", 0.0),
        "avg_brake_pressure": stats_500.get("avg_brake_pressure", 0.0),
        "avg_battery_voltage_v": stats_500.get("avg_battery_voltage_v", 12.6),
        "low_tire_pressure_ratio": stats_500.get("low_tire_pressure_ratio", 0.0),
        "overheat_events": stats_7d.get("overheat_events", 0.0),
        "max_coolant_temp_c": stats_7d.get("max_coolant_temp_c", 90.0),
        "dtc_count": stats_7d.get("dtc_count", 0.0),
        "harsh_accel_braking_index": stats_7d.get("harsh_accel_braking_index", 0.0),
        "km_since_last_brake_change": km_since_brake_change,
        "km_since_last_battery_change": km_since_battery_change,
        "w7d_avg_speed_kmph": stats_7d.get("avg_speed_kmph", 0.0),
        "w7d_city_ratio": stats_7d.get("city_ratio", 0.0),
        "w500_avg_speed_kmph": stats_500.get("avg_speed_kmph", 0.0),
        "w50_avg_speed_kmph": stats_50.get("avg_speed_kmph", 0.0),
        "trip_max_brake_pressure_avg": max_brake_per_trip_avg,
        "trip_harsh_index_avg": harsh_index_last_trips_avg,
    }
