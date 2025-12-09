from typing import Dict, List
from models import HealthScore


def _risk_from_score(score: float) -> str:
    if score < 0.3:
        return "HIGH"
    if score < 0.6:
        return "MEDIUM"
    return "LOW"


def compute_brake_health(features: Dict[str, float]) -> HealthScore:
    base_life_km = 30000.0
    baseline_hard_brakes = 5.0

    hard_brakes = features.get("hard_brakes_per_100km", baseline_hard_brakes)
    usage_factor = 1.0 + 0.6 * (hard_brakes / max(baseline_hard_brakes, 0.1))
    effective_life_km = base_life_km / max(usage_factor, 0.1)

    km_since_change = features.get("km_since_last_brake_change", 0.0)

    raw = 1.0 - km_since_change / max(effective_life_km, 1.0)
    health_score = max(0.0, min(1.0, raw))
    eta_km = max(0.0, health_score * effective_life_km)

    risk = _risk_from_score(health_score)

    return HealthScore(
        component="brake_pad",
        health_score=health_score,
        risk_level=risk,
        eta_km=eta_km,
        details={
            "km_since_last_change": km_since_change,
            "effective_life_km": effective_life_km,
            "hard_brakes_per_100km": hard_brakes,
        },
    )


def compute_battery_health(features: Dict[str, float]) -> HealthScore:
    baseline_voltage = 12.6
    min_voltage = features.get("avg_battery_voltage_v", baseline_voltage)
    km_since_change = features.get("km_since_last_battery_change", 0.0)

    max_life_km = 60000.0
    age_factor = km_since_change / max(max_life_km, 1.0)

    voltage_diff = baseline_voltage - min_voltage
    voltage_penalty = max(0.0, voltage_diff / 1.5)

    score = 1.0 - 0.7 * age_factor - 0.3 * voltage_penalty
    health_score = max(0.0, min(1.0, score))
    risk = _risk_from_score(health_score)

    remaining_ratio = max(0.0, health_score)
    eta_km = remaining_ratio * max_life_km

    return HealthScore(
        component="battery",
        health_score=health_score,
        risk_level=risk,
        eta_km=eta_km,
        details={
            "km_since_last_change": km_since_change,
            "avg_battery_voltage_v": min_voltage,
        },
    )


def compute_tire_health(features: Dict[str, float]) -> HealthScore:
    low_ratio = features.get("low_tire_pressure_ratio", 0.0)
    base_wear_penalty = low_ratio * 1.5

    score = 1.0 - base_wear_penalty
    health_score = max(0.0, min(1.0, score))
    risk = _risk_from_score(health_score)

    return HealthScore(
        component="tire",
        health_score=health_score,
        risk_level=risk,
        details={"low_tire_pressure_ratio": low_ratio},
    )


def compute_engine_health(features: Dict[str, float]) -> HealthScore:
    overheat_events = features.get("overheat_events", 0.0)
    max_coolant = features.get("max_coolant_temp_c", 90.0)
    dtc_count = features.get("dtc_count", 0.0)
    harsh_index = features.get("harsh_accel_braking_index", 0.0)

    overheat_penalty = min(overheat_events / 5.0, 1.0)
    temp_penalty = max(0.0, (max_coolant - 95.0) / 20.0)
    dtc_penalty = min(dtc_count / 5.0, 1.0)
    harsh_penalty = min(harsh_index / 2.0, 1.0)

    score = 1.0 - 0.4 * overheat_penalty - 0.2 * temp_penalty - 0.2 * dtc_penalty - 0.2 * harsh_penalty
    health_score = max(0.0, min(1.0, score))
    risk = _risk_from_score(health_score)

    return HealthScore(
        component="engine",
        health_score=health_score,
        risk_level=risk,
        details={
            "overheat_events": overheat_events,
            "max_coolant_temp_c": max_coolant,
            "dtc_count": dtc_count,
            "harsh_index": harsh_index,
        },
    )


def compute_all_components(features: Dict[str, float]) -> List[HealthScore]:
    return [
        compute_brake_health(features),
        compute_battery_health(features),
        compute_tire_health(features),
        compute_engine_health(features),
    ]
