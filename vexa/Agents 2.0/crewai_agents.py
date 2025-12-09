"""
CrewAI integration for:
- Diagnosis Agent (LLM reasoning on health + DTC RAG results)
- Customer Engagement Agent (LLM-based bilingual messaging)

We DO NOT expose Python tools directly to CrewAI here.
Instead we prepare text context (health summary, DTC context, alerts)
and feed it into the agents' prompts.
"""

from typing import List
import os

from crewai import Agent, Task, Crew
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv

from models import HealthSummary
from rag_dtc_tool import dtc_rag_lookup
from alerts import build_bilingual_alert

load_dotenv()


def build_llm() -> ChatOpenAI:
    api_key = os.getenv("OPENAI_API_KEY")
    model_name = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

    if not api_key:
        raise RuntimeError(
            "❌ OPENAI_API_KEY is not set.\n"
            "Add it to your .env file, e.g.:\n"
            "OPENAI_API_KEY=sk-xxxx...\n"
        )

    return ChatOpenAI(
        model=model_name,
        temperature=0.2,
    )


def health_summary_to_text(summary: HealthSummary) -> str:
    lines = [f"Vehicle ID: {summary.vehicle_id}", f"Timestamp: {summary.timestamp}", ""]
    for c in summary.component_health:
        lines.append(
            f"- {c.component}: score={c.health_score:.2f}, "
            f"risk={c.risk_level}, eta_km={c.eta_km}"
        )
    return "\n".join(lines)


def dtc_context_text(dtc_codes: List[str]) -> str:
    if not dtc_codes:
        return "No active DTC codes reported."

    lines: List[str] = []
    for code in dtc_codes:
        results = dtc_rag_lookup(code, top_k=1)
        if not results:
            lines.append(f"{code}: No known info in KB.")
            continue
        r = results[0]
        lines.append(
            f"{code} - {r['title']} (Severity: {r['severity']})\n"
            f"Description: {r['description']}\n"
            f"Probable Causes: {', '.join(r['probable_causes'])}\n"
        )
    return "\n".join(lines)


def bilingual_alerts_text(summary: HealthSummary) -> str:
    alerts = build_bilingual_alert(summary)
    lines: List[str] = []
    lines.append("English Alerts:")
    for m in alerts["en"]:
        lines.append(f"- {m}")
    lines.append("")
    lines.append("Hindi Alerts:")
    for m in alerts["hi"]:
        lines.append(f"- {m}")
    return "\n".join(lines)


def build_diagnosis_agent() -> Agent:
    return Agent(
        role="Diagnosis Agent",
        goal=(
            "Analyze vehicle health scores and DTC context to find which components "
            "are at highest risk and how urgent the maintenance is."
        ),
        backstory=(
            "You are an automotive diagnostic expert. You understand telematics-driven "
            "health scores and diagnostic trouble codes (DTCs)."
        ),
        llm=build_llm(),
        verbose=True,
    )


def build_customer_engagement_agent() -> Agent:
    return Agent(
        role="Customer Engagement Agent",
        goal=(
            "Convert technical diagnostics into short, friendly messages for the driver "
            "in both English and Hindi, using simple language and emojis."
        ),
        backstory=(
            "You are a service advisor who communicates with vehicle owners "
            "through app/chat and helps them understand when to visit the workshop."
        ),
        llm=build_llm(),
        verbose=True,
    )


def build_diagnostics_crew(
    health_summary: HealthSummary,
    dtc_codes: List[str],
) -> Crew:
    diagnosis_agent = build_diagnosis_agent()
    customer_agent = build_customer_engagement_agent()

    health_text = health_summary_to_text(health_summary)
    dtc_text = dtc_context_text(dtc_codes)
    alerts_text = bilingual_alerts_text(health_summary)

    diagnosis_task_desc = f"""
You are the Diagnosis Agent.

Below is the latest health summary for a vehicle:

[HEALTH SUMMARY]
{health_text}

Below is context from a DTC knowledge base (RAG results):

[DTC CONTEXT]
{dtc_text}

TASK:
1) Identify which components are at highest risk (brake_pad, battery, tire, engine, etc.).
2) For each risky component, give an urgency level: LOW / MEDIUM / HIGH for maintenance.
3) Provide 2-3 bullet points of probable root causes based on the health and DTC context.

Output a concise diagnostic report.
"""

    diagnosis_task = Task(
        description=diagnosis_task_desc,
        expected_output=(
            "A short diagnostic report including:\n"
            "- Components at risk with urgency (LOW/MEDIUM/HIGH)\n"
            "- 2-3 bullet points of probable causes"
        ),
        agent=diagnosis_agent,
    )

    customer_task_desc = f"""
You are the Customer Engagement Agent.

You have two sources of information:

[DIAGNOSTIC REPORT]
(You will receive this from the previous agent in the crew execution.)

[ALERT SUGGESTIONS (EN + HI)]
{alerts_text}

TASK:
Using the diagnostic report AND the alert suggestions above, generate a final message
that can be sent to the vehicle owner in BOTH English and Hindi.

Requirements:
- Use a friendly tone and emojis like 🚗, 🚨, ⚠️, ✅.
- English and Hindi should each be 3–5 short bullet-style lines.
- Be clear about how urgent the visit is and what the driver should do.

Format your answer exactly as:

ENGLISH:
- line 1
- line 2
...

HINDI:
- line 1
- line 2
...
"""

    customer_task = Task(
        description=customer_task_desc,
        expected_output=(
            "ENGLISH:\n- ...\n\nHINDI:\n- ..."
        ),
        agent=customer_agent,
    )

    crew = Crew(
        agents=[diagnosis_agent, customer_agent],
        tasks=[diagnosis_task, customer_task],
        verbose=True,
    )
    return crew


def run_crewai_demo(health_summary: HealthSummary, dtc_codes: List[str]) -> str:
    """
    Run Diagnosis + Customer Engagement agents with health + DTC context and
    return the final customer-facing bilingual message.
    """
    crew = build_diagnostics_crew(health_summary, dtc_codes)
    result = crew.kickoff()
    return str(result)
