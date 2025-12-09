# agents/master_agent.py

from __future__ import annotations

from typing import Any, Dict, List, Optional
from datetime import datetime, timezone

from models import HealthSummary
from models import HealthSummary
from synthetic_data import generate_stream_dataset, evolve_vehicle_state

# ----------------------------------------------------------------------
# Sensor agent import (robust to different class names)
# ----------------------------------------------------------------------
try:
    # If your sensor_agent.py exposes this (old name we used)
    from agents.sensor_agent import SyntheticSensorAgent
except ImportError:
    try:
        # Fallback: maybe it's called SensorAgent
        from agents.sensor_agent import SensorAgent as SyntheticSensorAgent
    except ImportError:
        # Last fallback: maybe it's called TelematicsSensorAgent
        from agents.sensor_agent import TelematicsSensorAgent as SyntheticSensorAgent

from agents.diagnosis_agent import DiagnosisAgentLLM
from agents.data_analysis_agent import DataAnalysisAgent
from agents.driver_behavior_agent import DriverBehaviorCoachAgent
from agents.scheduling_agent import SchedulingAgent
from agents.spare_parts_agent import SparePartsAgent
from agents.feedback_agent import FeedbackAgent
from agents.manufacturing_quality_agent import ManufacturingQualityAgent
from agents.ueba_agent import UEBAAgent
from agents.fleet_agent import FleetAgent

from agents.vehicle_ueba_agent import VehicleUEBAAgent
from agents.driver_ueba_agent import DriverUEBAAgent

from database import DatabaseManager


class MasterAgent:
    """
    Orchestrator for MagicDev:

    - reads telematics
    - scores health
    - runs diagnosis
    - computes urgency (LOW/MEDIUM/HIGH/CRITICAL)
    - checks parts availability (TecDoc or mocked)
    - proposes schedule slot (Nylas or mocked)
    - generates bilingual voice message (Sarvam)
    - logs UEBA + DB + manufacturing feedback
    - (NEW) runs UEBA for vehicle + driver
    """

    def __init__(self) -> None:
        # Core agents
        self.sensor = SyntheticSensorAgent()
        self.data_analysis = DataAnalysisAgent()
        self.diagnosis = DiagnosisAgentLLM()
        self.driver_coach = DriverBehaviorCoachAgent()
        self.scheduler = SchedulingAgent()
        self.spare_parts = SparePartsAgent()
        self.feedback = FeedbackAgent()
        self.manufacturing = ManufacturingQualityAgent()
        self.ueba = UEBAAgent()
        self.db = DatabaseManager()

        # In-memory "Live" state
        self.vehicle_memory: Dict[str, List[Any]] = {}

        # Fleet
        self.fleet_agent = FleetAgent(self)

        # NEW UEBA agents
        self.vehicle_ueba_agent = VehicleUEBAAgent(self.db)
        self.driver_ueba_agent = DriverUEBAAgent(self.db)

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    def _last_dtc_codes(self, events) -> List[str]:
        for ev in reversed(events):
            if ev.dtc_codes:
                return list(ev.dtc_codes)
        return []

    def _decide_urgency(self, summary: HealthSummary) -> str:
        """
        Add CRITICAL tier:
        - CRITICAL: multiple HIGH-risk components with very low health
        - HIGH: any brake_pad HIGH
        - MEDIUM: some HIGH risk, but not above conditions
        - LOW: else
        """
        high_risks = [h for h in summary.component_health if h.risk_level == "HIGH"]
        high_count = len(high_risks)
        avg_health = (
            sum(h.health_score for h in high_risks) / high_count if high_risks else 1.0
        )

        if high_count >= 2 and avg_health < 0.2:
            return "CRITICAL"
        if any(h.component == "brake_pad" for h in high_risks):
            return "HIGH"
        if high_risks:
            return "MEDIUM"
        return "LOW"

    def _send_emergency_alert(self, vehicle_id: str, summary: HealthSummary) -> None:
        print(f"🚨 EMERGENCY ALERT for {vehicle_id}")
        print("Multiple systems in HIGH risk state:")
        for c in summary.component_health:
            if c.risk_level == "HIGH":
                print(f" - {c.component}: score={c.health_score:.2f}")
        self.ueba.log(
            "MasterAgent",
            "emergency_alert_sent",
            {
                "vehicle_id": vehicle_id,
                "components": [
                    c.component
                    for c in summary.component_health
                    if c.risk_level == "HIGH"
                ],
            },
        )

    # ------------------------------------------------------------------
    # Main single-vehicle workflow
    # ------------------------------------------------------------------
    def process_vehicle(self, vehicle_id: str, simulate: bool = True) -> Dict[str, Any]:
        """
        Full workflow for one vehicle:
        - Read telematics
        - Compute rolling-health
        - Driver behaviour summary
        - UEBA (vehicle + driver)
        - Determine urgency (LOW/MEDIUM/HIGH/CRITICAL)
        - Suggest parts + slots (no auto-booking)
        - Generate bilingual voice/text alert
        - Log UEBA + DB + manufacturing feedback
        """

        # 1) Smart Data Generation (Persistence)
        # Check if we have history
        if vehicle_id in self.vehicle_memory:
            history = self.vehicle_memory[vehicle_id]
            last_event = history[-1]
            
            if simulate:
                # Evolve one step
                new_event = evolve_vehicle_state(last_event)
                history.append(new_event)
                # Keep buffer size reasonable
                if len(history) > 200:
                    history.pop(0)
            
            events = history
            maintenance = [] 
        else:
            # First time load: Must generate initial state even if simulate=False
            dataset = generate_stream_dataset(num_vehicles=10)
            events, maintenance = self.sensor.get_vehicle_stream(dataset, vehicle_id)
            self.vehicle_memory[vehicle_id] = events

        latest_summary: Optional[HealthSummary] = None
        for ev in events:
            latest_summary = self.data_analysis.handle_event(ev, maintenance)

        if latest_summary is None:
            raise RuntimeError("No events for vehicle; cannot compute health.")

        summary_dict = latest_summary.model_dump()
        
        # Capture latest telematics for Live View
        latest_telematics = events[-1].model_dump()
        
        self.ueba.log(
            "DataAnalysisAgent", "health_computed", {"vehicle_id": vehicle_id}
        )

        # 2) Diagnosis (LLM)
        dtc_codes = self._last_dtc_codes(events)
        diag_report = self.diagnosis.run(latest_summary, dtc_codes=dtc_codes)
        self.ueba.log(
            "DiagnosisAgent", "diagnosis_completed", {"vehicle_id": vehicle_id}
        )

        # 3) Driver behaviour coaching (summary from events)
        driver_tips = self.driver_coach.run(events)
        self.ueba.log(
            "DriverBehaviorCoachAgent", "tips_generated", {"vehicle_id": vehicle_id}
        )

        # 4) UEBA (NEW): vehicle + driver anomalies
        vehicle_ueba_result = self.vehicle_ueba_agent.detect_vehicle_anomalies(
            vehicle_id=vehicle_id,
            events=events,
            health_summary=latest_summary,
        )

        # For demo: synthetic mapping driver ↔ vehicle
        driver_id = f"DRIVER-{vehicle_id}"
        driver_ueba_result = self.driver_ueba_agent.detect_driver_anomalies(
            driver_id=driver_id,
            events=events,
        )

        self.ueba.log(
            "VehicleUEBAAgent",
            "vehicle_analyzed",
            {
                "vehicle_id": vehicle_id,
                "overall_risk": vehicle_ueba_result["overall_risk"],
                "anomaly_count": len(vehicle_ueba_result["anomalies"]),
            },
        )

        self.ueba.log(
            "DriverUEBAAgent",
            "driver_analyzed",
            {
                "driver_id": driver_id,
                "safety_score": driver_ueba_result["safety_score"],
                "anomaly_count": len(driver_ueba_result["anomalies"]),
            },
        )

        # 5) Decide urgency (with CRITICAL tier)
        urgency = self._decide_urgency(latest_summary)

        # Emergency alert hook for CRITICAL
        if urgency == "CRITICAL":
            self._send_emergency_alert(vehicle_id, latest_summary)

        # 6) Log health into DB
        self.db.log_health(vehicle_id, latest_summary.model_dump(), urgency)

        # 7) Parts + Scheduling (no auto-booking; just proposal if possible)
        booking_info: Optional[Dict[str, Any]] = None

        if urgency in ("CRITICAL", "HIGH"):
            critical_component = "brake_pad"

            parts_ok = self.spare_parts.is_available_for_vehicle(
                vehicle_id, critical_component, qty=1
            )
            self.ueba.log(
                "SparePartsAgent",
                "availability_checked",
                {
                    "vehicle_id": vehicle_id,
                    "component": critical_component,
                    "available": parts_ok,
                },
            )

            if parts_ok:
                reservation_info = self.spare_parts.reserve_for_vehicle(
                    vehicle_id, critical_component, qty=1
                )

                slot_result = self.scheduler.propose_slot(
                    urgency=urgency,
                    customer_email=None,  # no auto-email in demo
                )

                self.ueba.log(
                    "SchedulingAgent",
                    "slot_proposed",
                    {"vehicle_id": vehicle_id, "slot": slot_result.get("slot")},
                )

                # IMPORTANT: we are NOT auto-booking with Nylas here.
                booking_info = {
                    "reservation": reservation_info,
                    "slot": slot_result.get("slot"),
                    "event": None,
                    "status": "pending_customer_confirmation",
                }

        # 8) Customer-facing bilingual message + voice (Sarvam)
        # CustomerEngagementAgent removed by user.
        # Fallback: Generate basic alert message manually.
        
        message_body = "Vehicle is operating normally."
        if urgency in ("CRITICAL", "HIGH"):
            high_risk_components = [h for h in latest_summary.component_health if h.risk_level == "HIGH"]
            
            lines = [f"🚨 Safety Alert for {vehicle_id}!\n"]
            for h in high_risk_components:
                lines.append(f"• {h.component.replace('_', ' ').title()} is critical (health score {h.health_score:.2f}). Please service soon!")
            
            lines.append("\nWe recommend urgent inspection to avoid breakdowns. 🚗")
            message_body = "\n".join(lines)
            
        elif urgency == "MEDIUM":
             message_body = "Vehicle requires maintenance soon. Please check tire pressure and oil levels."
        
        customer_message_text: Dict[str, str] = {
            "english": message_body,
            "hindi": "वाहन को तत्काल सेवा की आवश्यकता है।" if urgency in ("CRITICAL", "HIGH") else "वाहन सामान्य रूप से चल रहा है।"
        }
        
        customer_message_audio: Dict[str, Any] = {}

        # self.ueba.log(
        #     "CustomerEngagementAgent",
        #     "message_generated",
        #     ...
        # )

        # 9) Feedback (simulated)
        feedback = self.feedback.collect_feedback(
            rating=9,
            comments="Voice alert was clear and easy to understand.",
        )
        self.ueba.log("FeedbackAgent", "feedback_collected", {"vehicle_id": vehicle_id})

        # 10) Manufacturing insights (RCA / CAPA)
        manuf_failures = self.manufacturing.summarize_failures([latest_summary])
        manuf_dtc = self.manufacturing.dtc_insights(dtc_codes)
        self.ueba.log(
            "ManufacturingQualityAgent",
            "insights_generated",
            {"vehicle_id": vehicle_id},
        )

        # 11) UEBA report (existing simple UEBAAgent)
        ueba_report = self.ueba.report()

        return {
            "vehicle_id": vehicle_id,
            "health_summary": summary_dict,
            "diagnosis_report": diag_report,
            "driver_tips": driver_tips,
            "urgency": urgency,
            "booking_info": booking_info,
            "feedback": feedback,
            "customer_message": customer_message_text,
            "customer_message_audio": customer_message_audio,
            "manufacturing_insights": {
                "failures": manuf_failures,
                "dtc_insights": manuf_dtc,
            },
            "ueba_report": ueba_report,
            "dtc_codes": dtc_codes,
            # NEW UEBA outputs
            "vehicle_ueba": vehicle_ueba_result,
            "driver_ueba": driver_ueba_result,
            "latest_telematics": latest_telematics, # <--- NEW for Live Dashboard
        }

    # ------------------------------------------------------------------
    # Fleet wrapper
    # ------------------------------------------------------------------
    async def process_fleet_batch(self, vehicle_ids: List[str]) -> Dict[str, Any]:
        """Process multiple vehicles with fleet-level analytics (async)."""
        return await self.fleet_agent.process_fleet(vehicle_ids)
