from fastapi import FastAPI, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
from agents.master_agent import MasterAgent
from agents.manufacturing_quality_agent import ManufacturingQualityAgent
import uvicorn
import os
from typing import Dict, Any

app = FastAPI(title="VEXA Agents API")

# Allow all origins for demo purposes
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory stores
bookings_db: Dict[str, Any] = {}
service_state_db: Dict[str, str] = {} # vehicle_id -> status (e.g., "COMPLETED")
feedback_db: Dict[str, Any] = {}

# Initialize agents
master_agent = MasterAgent()
manufacturing_agent = ManufacturingQualityAgent()

# Simple In-Memory User DB for Demo
users_db = {
    "admin": "password123",
    "owner": "123456", 
    "service": "mech2024"
}

@app.post("/auth/login")
def login(credentials: Dict[str, str] = Body(...)):
    username = credentials.get("username")
    password = credentials.get("password")
    
    print(f"Login attempt: {username}")
    
    if username in users_db and users_db[username] == password:
        return {
            "status": "success", 
            "token": f"mock-token-{username}",
            "role": "admin" if username == "admin" else "user"
        }
    
    # Auto-register for demo if not exists (per user request "saved in db")
    if username not in users_db:
        users_db[username] = password
        print(f"New user registered: {username}")
        return {
            "status": "success", 
            "token": f"mock-token-{username}", 
            "message": "User registered and logged in"
        }
        
    raise HTTPException(status_code=401, detail="Invalid credentials")

@app.get("/")
def read_root():
    return {"status": "VEXA Agents API is running"}

@app.get("/vehicle/{vehicle_id}/full_data")
def get_vehicle_data(vehicle_id: str, simulate: bool = True):
    """
    Orchestrates:
    1. Vehicle Data Retrieval
    2. Diagnosis & Health Check
    3. Part Availability & Scheduling
    """
    print(f"Processing vehicle: {vehicle_id}")
    
    # 1. Process via Master Agent
    try:
        result = master_agent.process_vehicle(vehicle_id, simulate=simulate)
        
        # Inject Booking Info
        if vehicle_id in bookings_db:
            # Handle potential None value from master agent
            current_info = result.get("booking_info")
            if current_info is None:
                current_info = {}
                
            result["booking_info"] = {
                **current_info,
                "status": "Confirmed",
                "details": bookings_db[vehicle_id]
            }
        
        # Inject Service Status (Post-Service Trigger)
        if vehicle_id in service_state_db:
            result["service_status"] = service_state_db[vehicle_id]
            
        return result
            
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/vehicle/{vehicle_id}/book")
def book_slot(vehicle_id: str, booking_data: Dict[str, Any] = Body(...)):
    print(f"Booking slot for {vehicle_id}: {booking_data}")
    bookings_db[vehicle_id] = booking_data
    return {"status": "success", "message": "Booking confirmed", "booking_id": f"BKG-{vehicle_id}"}

@app.post("/vehicle/{vehicle_id}/complete_service")
def complete_service(vehicle_id: str):
    print(f"Completing service for {vehicle_id}")
    service_state_db[vehicle_id] = "COMPLETED"
    return {"status": "success", "message": "Service marked as completed"}

@app.post("/vehicle/{vehicle_id}/feedback")
def submit_feedback(vehicle_id: str, feedback: Dict[str, Any] = Body(...)):
    print(f"Received feedback for {vehicle_id}: {feedback}")
    if vehicle_id not in feedback_db:
        feedback_db[vehicle_id] = []
    
    # Store as list of feedbacks or single object? Agent expects list or dict.
    # Let's simple append to list if it exists
    if isinstance(feedback_db[vehicle_id], list):
        feedback_db[vehicle_id].append(feedback)
    else:
        feedback_db[vehicle_id] = [feedback]
        
    return {"status": "success", "message": "Feedback received"}

@app.get("/manufacturing/insights")
def get_manufacturing_insights():
    """
    Returns aggregated insights for the Manufacturing Dashboard.
    Uses ManufacturingQualityAgent to analyze data.
    """
    return manufacturing_agent.generate_dashboard_insights(service_state_db, feedback_db)

@app.post("/manufacturing/chat")
def chat_with_manufacturing_agent(query_data: Dict[str, str] = Body(...)):
    """
    Chat with the Manufacturing AI Analyst.
    """
    query = query_data.get("query", "")
    print(f"Chat query: {query}")
    
    # Get current insights context
    insights = manufacturing_agent.generate_dashboard_insights(service_state_db, feedback_db)
    
    response = manufacturing_agent.chat_with_data(query, insights)
    return {"response": response}

from agents.ueba_agent import UEBAAgent
ueba_agent = UEBAAgent()

@app.post("/ueba/simulate_attack")
def simulate_attack():
    """
    Triggers a simulated security attack (burst of unauthorized access events).
    """
    print("Simulating security attack...")
    ueba_agent.simulate_attack()
    return {"status": "success", "message": "Attack simulation initiated"}

@app.post("/ueba/reset")
def reset_ueba():
    """
    Resets the UEBA agent state to normal.
    """
    print("Resetting UEBA agent...")
    ueba_agent.reset()
    return {"status": "success", "message": "UEBA agent reset"}

@app.get("/ueba/status")
def get_ueba_status():
    """
    Returns current UEBA anomalies.
    """
    anomalies = ueba_agent.detect_anomalies()
    return {
        "anomalies": anomalies, 
        "risk_level": "CRITICAL" if anomalies else "LOW"
    }



@app.post("/voice/trigger")
def trigger_voice_engagement(data: Dict[str, Any] = Body(...)):
    """
    Triggers an outbound call to the vehicle owner.
    """
    vehicle_id = data.get("vehicle_id")
    phone_number = data.get("phone_number")
    risk_level = data.get("risk_level", "High")
    
    print(f"Triggering voice call for {vehicle_id} to {phone_number}")
    
    # In a real deployed app, this callback_url must be publicly accessible (e.g. ngrok or deployed domain)
    # For local demo, we might rely on the 'Mock Mode' of the agent if credentials aren't set.
    callback_url = "https://1065dfdaa0c5.ngrok-free.app/voice/answer" 
    
    result = customer_engagement_agent.initiate_call(
        to_number=phone_number,
        vehicle_data={"vehicle_id": vehicle_id, "risk_level": risk_level},
        callback_url=callback_url
    )
    return result

from fastapi import Form, Response

@app.post("/voice/answer")
async def voice_answer(vehicle_id: str = "Unknown", risk: str = "High"):
    """
    Twilio Webhook: Called when the user answers the phone.
    """
    print(f"Voice Answered. Context: {vehicle_id}, {risk}")
    twiml = customer_engagement_agent.generate_initial_twiML({"vehicle_id": vehicle_id, "risk_level": risk})
    return Response(content=twiml, media_type="application/xml")

@app.post("/voice/handle_reply")
async def handle_voice_reply(SpeechResult: str = Form(None)):
    """
    Twilio Webhook: Called when the user speaks.
    """
    user_speech = SpeechResult or ""
    print(f"User Said: {user_speech}")
    
    twiml = customer_engagement_agent.handle_conversation(user_speech, "")
    return Response(content=twiml, media_type="application/xml")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
