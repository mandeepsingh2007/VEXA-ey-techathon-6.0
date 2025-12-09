from typing import List, Optional
import os

from langchain_openai import ChatOpenAI
from dotenv import load_dotenv

from models import HealthSummary
from crewai_agents import health_summary_to_text, dtc_context_text

load_dotenv()


class DiagnosisAgentLLM:
    """
    LLM agent that reasons about component risk + DTC context
    and produces an internal diagnostic report.
    """

    def __init__(self, model_name: Optional[str] = None):
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise RuntimeError("OPENAI_API_KEY not set in .env")

        self.llm = ChatOpenAI(
            model=model_name or os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
            temperature=0.2,
        )

    def run(self, summary: HealthSummary, dtc_codes: List[str]) -> str:
        health_text = health_summary_to_text(summary)
        dtc_text = dtc_context_text(dtc_codes)

        prompt = f"""
You are an automotive diagnostics expert.

[HEALTH SUMMARY]
{health_text}

[DTC CONTEXT]
{dtc_text}

TASK:
1) List components at risk with urgency (LOW/MEDIUM/HIGH).
2) Give 2–3 bullet points of probable causes.
3) Be concise and technical; this is for internal workshop staff.

Return a short report.
"""
        response = self.llm.invoke(prompt)
        return response.content
