# 🚗 VEXA: Vehicler Executer AI

![VEXA Banner](https://img.shields.io/badge/Status-Prototype-success?style=for-the-badge) ![Tech](https://img.shields.io/badge/Tech-CrewAI%20%7C%20FastAPI%20%7C%20Flutter-blue?style=for-the-badge) ![AI](https://img.shields.io/badge/AI-Multi--Agent%20System-purple?style=for-the-badge)

> **Where Mobility Meets Intelligence.**
> VEXA moves the automotive industry from *Reactive Repair* to **Predictive Reliability** by connecting Vehicle Owners, Service Centers, and Manufacturers into one self-healing ecosystem.

---

## 🌟 The Vision

Today's vehicle ecosystem is fragmented. Owners ignore warning lights, Service Centers struggle with scheduling, and Manufacturers (OEMs) lack real-time feedback.

**VEXA solves this with a Multi-Agent System.** Instead of static dashboards, we deploy **10 specialized AI Agents** that collaborate to:
1.  **Predict Failures** before they happen.
2.  **Automate Actions** (Booking, Ordering Parts).
3.  **Secure Data** against cyber threats.
4.  **Close the Feedback Loop** for R&D.

---

## 🤖 The 10-Agent Architecture

VEXA is powered by **CrewAI** and **FastAPI**, orchestrating a symphony of agents:

### � Data & Diagnosis Layer
*   **1. Synthetic Sensor Agent**: The Digital Twin. Generates realistic, high-frequency telemetry (Speed, RPM, Heat, Vibration) simulating a connected ECU.
*   **2. Data Analysis Agent**: The Watchdog. Monitors live streams using statistical rolling windows to detect immediate anomalies.
*   **3. Diagnosis Agent (LLM)**: The Mechanic. Uses Large Language Models (LLM) to correlate sensor spikes with DTC codes, providing root-cause analysis (e.g., *"Brake pad wear critical due to sustained friction"*).
*   **4. Driver Behavior Agent**: The Coach. Analyzes acceleration and braking patterns to calculate safety scores and provide personalized driving tips.

### 🗣️ Engagement & Action Layer
*   **5. Customer Engagement Agent**: The Concierge. Triggers real-time alerts via **Voice (Sarvam AI)** or Text when critical issues arise, explaining technical terms in plain language.
*   **6. Spare Parts Agent**: The Logistican. Checks inventory at local service centers in real-time to ensure required parts (e.g., "Brake Pad Type-X") are in stock.
*   **7. Scheduling Agent**: The Planner. Integrates with **Nylas Calendar API** to find optimal service slots, balancing urgency with service center availability (load balancing < 5 concurrent slots).

### 🏭 Ecosystem & Feedback Layer
*   **8. Service Agent**: The Assistant. Auto-generates detailed Job Cards for mechanics, pre-filled with the AI's diagnostic data to reduce diagnostic time.
*   **9. Manufacturing Quality Agent**: The Engineer. Aggregates failure data across the fleet using **Vector Search (RAG)** to identify emerging defects (e.g., "Batch #402 Friction Material Failure") for the engineering team.

### 🛡️ Security Layer
*   **10. UEBA Security Agent**: The Guardian. Uses User & Entity Behavior Analytics with dynamic statistical thresholds (Mean + StdDev) to detect and block API attacks (e.g., unauthorized telematics access) in real-time.

---

## � Key Features

### For Vehicle Owners
*   **Live Digital Twin**: Real-time visualization of car health.
*   **AI Voice Alerts**: proactive calls when danger is detected.
*   **3-Click Booking**: Instant appointment scheduling when parts are confirmed.
*   **Security Shield**: Visual indication of API security status.

### For Service Centers
*   **Smart Job Cards**: Incoming cars arrive with a diagnosis already done.
*   **Dynamic Scheduling**: AI manages the calendar to prevent overcrowding.
*   **Inventory Sync**: Parts are reserved automatically.

### For Manufacturers (OEMs)
*   **Real-time R&D**: See failure trends hours after they happen, not months.
*   **RAG Chatbot**: "Ask AI Lead" to query thousands of service records in natural language.
*   **Cost Savings**: Drastically reduce warranty claims through predictive fixes.

---

## 🛠️ Tech Stack

*   **Frontend**: Flutter (Web & Mobile) - *Responsive, Glassmorphism Design*.
*   **Backend**: Python FastAPI - *High-performance async API*.
*   **AI Orchestration**: CrewAI - *Agent role assignment and task delegation*.
*   **LLM Integrations**: OpenCV / OpenAI / Sarvam AI.
*   **Integrations**:
    *   **Nylas**: Calendar & Scheduling.
    *   **Twilio/Sarvam**: Voice & SMS.
    *   **Vector DB**: For RAG-based quality insights.

---

## 🚀 Getting Started

### Prerequisites
*   Python 3.10+
*   Flutter SDK

### Installation

1.  **Clone the Repository**
    ```bash
    git clone https://github.com/yourusername/vexa.git
    cd vexa
    ```

2.  **Backend Setup**
    ```bash
    cd "Agents 2.0"
    python -m venv venv
    ./venv/Scripts/Activate  # Windows
    pip install -r requirements.txt
    python main.py
    ```

3.  **Frontend Setup**
    ```bash
    # Open a new terminal
    cd vexa
    flutter pub get
    flutter run -d chrome
    ```

---

*Built for the EY Techathon 6.0 | Transforming Mobility 🚗*
