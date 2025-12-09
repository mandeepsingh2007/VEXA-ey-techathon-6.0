from typing import Dict, List
from synthetic_data import generate_stream_dataset
from models import TelematicsEvent, MaintenanceRecord


class SensorAgent:
    """
    Simulates vehicle sensor / telematics feed.
    In real system this would consume MQTT/Kafka.
    """

    def generate_dataset(self, num_vehicles: int = 10) -> Dict[str, Dict[str, List]]:
        return generate_stream_dataset(num_vehicles=num_vehicles)

    def get_vehicle_stream(
        self, dataset: Dict[str, Dict[str, List]], vehicle_id: str
    ) -> tuple[list[TelematicsEvent], list[MaintenanceRecord]]:
        data = dataset[vehicle_id]
        return data["events"], data["maintenance"]
