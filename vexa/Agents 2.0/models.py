from typing import List, Dict, Optional
from pydantic import BaseModel


class TelematicsEvent(BaseModel):
    event_id: str
    vehicle_id: str
    timestamp: str  # ISO string
    odometer_km: float
    engine_hours: float
    speed_kmph: float
    accel_longitudinal: float
    brake_pedal_pressure: float
    steering_angle_deg: float
    engine_coolant_temp_c: float
    engine_oil_temp_c: float
    engine_rpm: int
    battery_voltage_v: float
    fuel_level_pct: float
    ambient_temp_c: float
    tire_pressure_fl_psi: float
    tire_pressure_fr_psi: float
    tire_pressure_rl_psi: float
    tire_pressure_rr_psi: float
    driving_mode: str  # city/highway/mixed
    hard_brake_events_last_10min: int
    harsh_accel_events_last_10min: int
    dtc_codes: List[str]


class ReplacedPart(BaseModel):
    part_number: str
    component: str  # "brake_pad", "battery", etc.
    qty: int
    reason_code: str  # "wear", "defect", "accident", etc.


class MaintenanceRecord(BaseModel):
    record_id: str
    vehicle_id: str
    service_date: str  # ISO
    odometer_km: float
    service_center_id: str
    complaint_desc: str
    dtc_at_intake: List[str]
    operations: List[str]  # labour codes
    parts_replaced: List[ReplacedPart]
    warranty_flag: bool
    rca_code: Optional[str] = None
    capa_id: Optional[str] = None


class HealthScore(BaseModel):
    component: str
    health_score: float  # 0..1
    risk_level: str  # "LOW", "MEDIUM", "HIGH"
    eta_km: Optional[float] = None
    eta_days: Optional[float] = None
    details: Dict[str, float] = {}


class HealthSummary(BaseModel):
    vehicle_id: str
    timestamp: str
    component_health: List[HealthScore]


class CenterComponentForecast(BaseModel):
    component: str
    predicted_jobs: int


class DemandForecast(BaseModel):
    center_id: str
    horizon_days: int
    predictions: List[CenterComponentForecast]
