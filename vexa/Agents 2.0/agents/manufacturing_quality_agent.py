from typing import List, Dict


from models import HealthSummary
from rag_dtc_tool import dtc_rag_lookup
import os
import json
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

SARVAM_BASE_URL = os.getenv("SARVAM_BASE_URL", "https://api.sarvam.ai/v1")
SARVAM_API_KEY = os.getenv("SARVAM_API_KEY")


class ManufacturingQualityAgent:
    """
    Summarises high-risk components and common DTCs for OEM insights.
    """

    def summarize_failures(self, summaries: List[HealthSummary]) -> Dict:
        high_risk_counts: Dict[str, int] = {}
        for s in summaries:
            for c in s.component_health:
                if c.risk_level == "HIGH":
                    high_risk_counts[c.component] = high_risk_counts.get(
                        c.component, 0
                    ) + 1
        return {
            "high_risk_components": high_risk_counts,
        }

    def dtc_insights(self, dtc_codes: List[str]) -> List[Dict]:
        seen = set()
        insights: List[Dict] = []
        for code in dtc_codes:
            if code in seen:
                continue
            seen.add(code)
            res = dtc_rag_lookup(code, top_k=1)
            if res:
                insights.append(res[0])
    def generate_dashboard_insights(self, service_states: Dict, feedbacks: Dict) -> Dict:
        """
        Generates insights for the manufacturing dashboard based on service history and feedback.
        In a real system, this would query a large database. Here we simulate it or aggregate small data.
        """
        # Base mock trends
        defect_trends = {
            "Brake Pad": 45,
            "Battery": 32,
            "Clutch": 21,
            "Tyre": 15,
            "Suspension": 10
        }
        
        # Adjust based on completed services (simple simulation)
        completed_count = sum(1 for status in service_states.values() if status == "COMPLETED")
        
        # If we have completed services, artificially boost some numbers to show "live" updates
        if completed_count > 0:
            defect_trends["Brake Pad"] += completed_count * 2
            defect_trends["Battery"] += completed_count
            
        # Analyze feedback for negative sentiment (mock logic)
        negative_feedback_count = 0
        for fb_list in feedbacks.values():
            if isinstance(fb_list, dict): 
                if fb_list.get("rating", 5) < 3:
                     negative_feedback_count += 1
            # If list of feedbacks
            elif isinstance(fb_list, list):
                for fb in fb_list:
                    if fb.get("rating", 5) < 3:
                        negative_feedback_count += 1

        recommendations = []

        # Find top defect
        top_defect = max(defect_trends, key=defect_trends.get)
        
        # 1. Defect-specific insight
        if top_defect == "Brake Pad":
             recommendations.append("High wear rate detected in Brake Pads - Supplier X batch #42 under review")
        elif top_defect == "Battery":
             recommendations.append("Battery voltage irregularities correlated with extreme weather")
        else:
             recommendations.append(f"Rising trend in {top_defect} failures - check component specifications")

        # 2. Fix-based Validation Insight (The 'Real' part)
        if completed_count > 0:
             recommendations.append(f"Field data from {completed_count} recent repairs confirms {top_defect} prediction accuracy > 95%")
             recommendations.append(f"Corrective Action: Service centers instructed to replace {top_defect} with reinforced Batch #43")
        else:
             # Default insights if no services completed yet
             recommendations.append("Monitor Battery voltage drop trends in mid-size SUVs")
             recommendations.append("Awaiting field validation from service centers")
        
        if negative_feedback_count > 0:
            recommendations.append(f"Investigate {negative_feedback_count} recent negative customer reports immediately")

        # Generate Time Series Data (Simulated for Demo)
        # X-axis: 0 to 4 (representing weeks or months)
        # Y-axis: Failure count
        
        # Base cureves
        actual_failures = [10, 15, 12, 20, 18]
        predicted_failures = [8, 10, 8, 12, 10]
        
        # Modify based on completed jobs (simulating that we are catching more failures, so 'Actual' might drop or 'Predicted' gets closer)
        # Let's say: more completed services = better prediction matching or slightly higher 'prevented' count logic
        if completed_count > 0:
            # Shift the last few points to show improvement/change
            actual_failures[4] = max(10, actual_failures[4] - completed_count) # Failures go DOWN as we fix them
            predicted_failures[4] = predicted_failures[4] + (completed_count * 0.5) # Prediction model adjusts

        failure_trends = {
            "actual": [{"x": i, "y": y} for i, y in enumerate(actual_failures)],
            "predicted": [{"x": i, "y": y} for i, y in enumerate(predicted_failures)]
        }

        # Dynamic Root Cause Analysis (Mock Logic based on defects)
        # If Brake Pad (Supplier) is high -> Increase Supplier Quality %
        # If Suspension (Usage) is high -> Increase Driver Behaviour %
        
        total_defects = sum(defect_trends.values())
        supplier_issues = defect_trends.get("Brake Pad", 0) + defect_trends.get("Battery", 0)
        driver_issues = defect_trends.get("Clutch", 0) + defect_trends.get("Suspension", 0)
        
        # Calculate ratios
        supplier_pct = round(supplier_issues / total_defects, 2) if total_defects > 0 else 0.35
        driver_pct = round(driver_issues / total_defects, 2) if total_defects > 0 else 0.40
        design_pct = 0.15
        others_pct = max(0, 1.0 - (supplier_pct + driver_pct + design_pct))

        root_cause_analysis = [
            {'cause': 'Supplier quality', 'percent': supplier_pct},
            {'cause': 'Driver behaviour', 'percent': driver_pct},
            {'cause': 'Design issue', 'percent': design_pct},
            {'cause': 'Others', 'percent': round(others_pct, 2)},
        ]
        
        # Sort by percent descending
        root_cause_analysis.sort(key=lambda x: x['percent'], reverse=True)

        return {
            "defect_trends": defect_trends,
            "quality_score": 88.5 - (negative_feedback_count * 0.5), # Impact score based on feedback
            "recommendations": recommendations,
            "total_monitored": 12450 + len(service_states),
            "breakdowns_prevented": 184 + completed_count,
            "warranty_saved": f"₹{3.2 + (completed_count * 0.05):.1f} Cr",
            "failure_trends": failure_trends,
            "root_cause_analysis": root_cause_analysis
        }

    def chat_with_data(self, query: str, context: Dict) -> str:
        """
        Uses Sarvam AI (LLM) to respond to questions about the manufacturing data in any Indian language.
        Falls back to rule-based if API is not available.
        """
        if not SARVAM_API_KEY:
            # Fallback to legacy rule-based system
            return self._chat_rule_based(query, context)

        try:
            client = OpenAI(
                base_url=SARVAM_BASE_URL,
                api_key=SARVAM_API_KEY,
            ).with_options(max_retries=1)

            # Construct prompt context
            defect_trends = context.get("defect_trends", {})
            recommendations = context.get("recommendations", [])
            root_cause = context.get("root_cause_analysis", [])

            system_prompt = f"""
            You are the "VEXA AI Lead", an intelligent Manufacturing Quality Analyst.
            
            REAL-TIME DATA CONTEXT:
            - Defect Trends: {json.dumps(defect_trends)}
            - Root Cause Analysis: {json.dumps(root_cause)}
            - Key Recommendations: {json.dumps(recommendations)}
            
            YOUR GOAL:
            Answer the user's query mainly based on the provided data.
            Crucially: REPLY IN THE SAME LANGUAGE AS THE USER (e.g., Hindi, Tamil, Bengali, etc.).
            Keep answers concise, professional, and actionable.
            """

            reply = client.chat.completions.create(
                model="sarvam-m",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": query},
                ],
                max_tokens=300,
                temperature=0.1, # Low temperature for factual consistency
            )
            
            return reply.choices[0].message.content

        except Exception as e:
            print(f"Sarvam AI Error: {e}")
            return self._chat_rule_based(query, context)

    def _chat_rule_based(self, query: str, context: Dict) -> str:
        query = query.lower()
        defect_trends = context.get("defect_trends", {})
        recommendations = context.get("recommendations", [])

        if "brake" in query:
            val = defect_trends.get('Brake Pad', 0)
            return f"Brake Pads are currently the top defect with {val} reported issues. We have identified a quality issue with Supplier X (Batch #42)."
            
        if "battery" in query:
            val = defect_trends.get('Battery', 0)
            return f"Battery failures are trending at {val} cases. This is correlated with recent extreme weather conditions affecting mid-size SUVs."
            
        if any(k in query for k in ["recommend", "action", "better", "future", "improve", "fix"]):
            rec_text = "\n- ".join(recommendations[:3])
            return f"Based on the analysis, here are the key actions for future vehicle improvements:\n- {rec_text}"
            
        if "supplier" in query:
            return "Supplier X (Brake Pads) and Supplier Y (Batteries) are currently flagged for quality review based on recent failure patterns."
            
        return "I can help you analyze defect trends, supplier quality, and provide recommendations. Try asking about 'Brake Pads', 'Batteries', or 'Recommendations'."
