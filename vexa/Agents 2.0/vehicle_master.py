# vehicle_master.py

from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, Optional


@dataclass
class VehicleMeta:
    vehicle_id: str
    manufacturer: str
    model: str
    year: int
    engine_type: Optional[str] = None


# Simple in-memory "vehicle master" table for the hackathon.
VEHICLE_MASTER: Dict[str, VehicleMeta] = {
    "VH-1000": VehicleMeta("VH-1000", "Toyota", "Innova", 2020, "2.0L Diesel"),
    "VH-1001": VehicleMeta("VH-1001", "Honda", "Civic", 2019, "1.8L Petrol"),
    "VH-1002": VehicleMeta("VH-1002", "Maruti", "Swift", 2021, "1.2L Petrol"),
    "VH-1003": VehicleMeta("VH-1003", "Hyundai", "Creta", 2022, "1.5L Diesel"),
    "VH-1004": VehicleMeta("VH-1004", "Tata", "Nexon", 2021, "1.2L Petrol"),
}


def get_vehicle_meta(vehicle_id: str) -> Optional[VehicleMeta]:
    """Lookup vehicle metadata by ID."""
    return VEHICLE_MASTER.get(vehicle_id)
