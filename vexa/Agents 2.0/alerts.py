from typing import List, Dict
from models import HealthSummary


def _component_severity_emoji(risk: str) -> str:
    if risk == "HIGH":
        return "🚨"
    if risk == "MEDIUM":
        return "⚠️"
    return "✅"


def summarize_health_en(summary: HealthSummary) -> List[str]:
    messages: List[str] = []
    for c in summary.component_health:
        emoji = _component_severity_emoji(c.risk_level)
        if c.component == "brake_pad":
            if c.risk_level == "HIGH":
                msg = (
                    f"{emoji} Brakes need urgent attention. "
                    f"Health score: {c.health_score:.2f}. "
                    "Recommend inspection as soon as possible."
                )
            elif c.risk_level == "MEDIUM":
                msg = (
                    f"{emoji} Brakes show moderate wear. "
                    "Recommend inspection within the next few weeks."
                )
            else:
                msg = f"{emoji} Brakes are in good condition."
        elif c.component == "battery":
            if c.risk_level == "HIGH":
                msg = (
                    f"{emoji} Battery health is low. "
                    "You may face starting issues soon."
                )
            elif c.risk_level == "MEDIUM":
                msg = (
                    f"{emoji} Battery is aging. "
                    "Consider checking it at your next service."
                )
            else:
                msg = f"{emoji} Battery health looks good."
        elif c.component == "tire":
            if c.risk_level == "HIGH":
                msg = (
                    f"{emoji} Tyre pressure/condition looks risky. "
                    "Please check tyre pressure and tread depth."
                )
            else:
                msg = f"{emoji} Tyres look okay in recent data."
        elif c.component == "engine":
            if c.risk_level == "HIGH":
                msg = (
                    f"{emoji} Engine shows signs of stress "
                    "(overheating, DTCs or harsh driving). "
                    "Recommend detailed inspection."
                )
            else:
                msg = f"{emoji} Engine parameters look normal."
        else:
            msg = f"{emoji} {c.component}: risk={c.risk_level}"

        messages.append(msg)
    return messages


def summarize_health_hi(summary: HealthSummary) -> List[str]:
    messages: List[str] = []
    for c in summary.component_health:
        emoji = _component_severity_emoji(c.risk_level)
        if c.component == "brake_pad":
            if c.risk_level == "HIGH":
                msg = (
                    f"{emoji} ब्रेक की हालत काफ़ी खराब है। "
                    "जितनी जल्दी हो सके ब्रेक चेक कराएँ।"
                )
            elif c.risk_level == "MEDIUM":
                msg = (
                    f"{emoji} ब्रेक में मिड-लेवल घिसावट दिख रही है। "
                    "आने वाले कुछ हफ़्तों में ब्रेक चेक कराना बेहतर रहेगा।"
                )
            else:
                msg = f"{emoji} ब्रेक अभी ठीक स्थिति में हैं।"
        elif c.component == "battery":
            if c.risk_level == "HIGH":
                msg = (
                    f"{emoji} बैटरी की हेल्थ कम है। "
                    "जल्द ही गाड़ी स्टार्ट होने में दिक्कत आ सकती है।"
                )
            elif c.risk_level == "MEDIUM":
                msg = (
                    f"{emoji} बैटरी पुरानी हो रही है। "
                    "अगली सर्विस में बैटरी चेक करवाना अच्छा रहेगा।"
                )
            else:
                msg = f"{emoji} बैटरी की हेल्थ ठीक लग रही है।"
        elif c.component == "tire":
            if c.risk_level == "HIGH":
                msg = (
                    f"{emoji} टायर प्रेशर/कंडीशन सुरक्षित नहीं दिख रही। "
                    "कृपया टायर प्रेशर और ट्रेड डेप्थ चेक कराएँ।"
                )
            else:
                msg = f"{emoji} हाल के डेटा के अनुसार टायर ठीक दिख रहे हैं।"
        elif c.component == "engine":
            if c.risk_level == "HIGH":
                msg = (
                    f"{emoji} इंजन पर ज़्यादा लोड/स्ट्रेस दिख रहा है "
                    "(ओवरहीटिंग, DTC या हार्श ड्राइविंग)। "
                    "डिटेल इंजन चेकअप कराएँ।"
                )
            else:
                msg = f"{emoji} इंजन के पैरामीटर सामान्य दिख रहे हैं।"
        else:
            msg = f"{emoji} {c.component}: जोखिम स्तर {c.risk_level}"

        messages.append(msg)
    return messages


def build_bilingual_alert(summary: HealthSummary) -> Dict[str, List[str]]:
    return {
        "en": summarize_health_en(summary),
        "hi": summarize_health_hi(summary),
    }
