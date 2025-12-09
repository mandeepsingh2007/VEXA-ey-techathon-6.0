from typing import List, Dict
from dataclasses import dataclass
import math


@dataclass
class DTCDocument:
    code: str
    title: str
    description: str
    severity: str
    probable_causes: List[str]


DTC_KB: List[DTCDocument] = [
    DTCDocument(
        code="P0300",
        title="Random/Multiple Cylinder Misfire Detected",
        description="Engine control module detected random or multiple misfires in cylinders.",
        severity="HIGH",
        probable_causes=[
            "Faulty spark plugs or ignition coils",
            "Vacuum leak",
            "Fuel delivery issue",
        ],
    ),
    DTCDocument(
        code="P0420",
        title="Catalyst System Efficiency Below Threshold (Bank 1)",
        description="Catalytic converter efficiency below threshold on bank 1.",
        severity="MEDIUM",
        probable_causes=[
            "Aging catalytic converter",
            "Rich/lean running condition",
            "Faulty oxygen sensor",
        ],
    ),
    DTCDocument(
        code="P0171",
        title="System Too Lean (Bank 1)",
        description="Fuel trim indicates the mixture is too lean on bank 1.",
        severity="MEDIUM",
        probable_causes=[
            "Vacuum leak",
            "Weak fuel pump or clogged filter",
            "Dirty MAF sensor",
        ],
    ),
    DTCDocument(
        code="U0100",
        title="Lost Communication with ECM/PCM",
        description="Communication with engine/powertrain control module has been lost intermittently.",
        severity="HIGH",
        probable_causes=[
            "CAN bus wiring issues",
            "ECM power/ground problem",
            "Failing ECM",
        ],
    ),
]


def _tokenize(text: str) -> List[str]:
    return [t.lower() for t in text.replace("/", " ").replace(",", " ").split()]


def _to_bow(tokens: List[str]) -> Dict[str, int]:
    out: Dict[str, int] = {}
    for t in tokens:
        out[t] = out.get(t, 0) + 1
    return out


def _cosine_sim(a: Dict[str, int], b: Dict[str, int]) -> float:
    vocab = set(a.keys()) | set(b.keys())
    dot = sum(a.get(w, 0) * b.get(w, 0) for w in vocab)
    norm_a = math.sqrt(sum(v * v for v in a.values()))
    norm_b = math.sqrt(sum(v * v for v in b.values()))
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / (norm_a * norm_b)


def dtc_rag_lookup(query: str, top_k: int = 3) -> List[Dict]:
    q_tokens = _tokenize(query)
    q_bow = _to_bow(q_tokens)

    scored: List[tuple[float, DTCDocument]] = []
    for doc in DTC_KB:
        doc_text = f"{doc.code} {doc.title} {doc.description} {' '.join(doc.probable_causes)}"
        d_tokens = _tokenize(doc_text)
        d_bow = _to_bow(d_tokens)
        sim = _cosine_sim(q_bow, d_bow)
        scored.append((sim, doc))

    scored.sort(key=lambda x: x[0], reverse=True)
    results: List[Dict] = []
    for sim, doc in scored[:top_k]:
        results.append(
            {
                "similarity": sim,
                "code": doc.code,
                "title": doc.title,
                "description": doc.description,
                "severity": doc.severity,
                "probable_causes": doc.probable_causes,
            }
        )
    return results
