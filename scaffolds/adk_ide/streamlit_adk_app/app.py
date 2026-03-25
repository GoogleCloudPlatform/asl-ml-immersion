import streamlit as st
import httpx
import asyncio
import uuid
import base64

# --- Configuration ---
ADK_BASE_URL = "http://127.0.0.1:8502"
ADK_RUN_URL = f"{ADK_BASE_URL}/run"
APP_NAME = "agent_01_tool_func"
TIMEOUT_SEC = 120.0

st.set_page_config(page_title="Simple ADK Chat", page_icon="💬", layout="centered")

# --- Async API Communication Functions ---
async def create_adk_session_async(user_id: str) -> str:
    new_session_id = f"s_{uuid.uuid4().hex[:8]}"
    session_url = f"{ADK_BASE_URL}/apps/{APP_NAME}/users/{user_id}/sessions/{new_session_id}"
    
    async with httpx.AsyncClient() as client:
        response = await client.post(session_url, json={}, timeout=10.0)
        response.raise_for_status() 
        return response.json().get("id", new_session_id)

async def transmit_payload_async(payload: dict) -> httpx.Response:
    async with httpx.AsyncClient(timeout=TIMEOUT_SEC) as client:
        response = await client.post(ADK_RUN_URL, json=payload)
        response.raise_for_status()
        return response

def safe_extract_response(data: list | dict) -> str:
    last_text_response = "No response received."
    for event in data:
        if "content" not in event: continue
        if "parts" in event["content"] and len(event["content"]["parts"]) > 0:
            for part in event["content"]["parts"]:
                if "text" in part: last_text_response = part["text"]
    return last_text_response

# --- App Initialization ---
if "user_id" not in st.session_state: 
    st.session_state.user_id = f"user_{uuid.uuid4().hex[:6]}"

if "session_id" not in st.session_state:
    with st.spinner("Connecting to ADK Server..."):
        try:
            st.session_state.session_id = asyncio.run(create_adk_session_async(st.session_state.user_id))
        except Exception as e: 
            st.error(f"Failed to connect to ADK server. Is it running?\nError: {e}")
            st.stop()

if "messages" not in st.session_state: 
    st.session_state.messages = []

# --- UI Setup ---
st.title("💬 Simple ADK Chat")
st.caption(f"**Session:** `{st.session_state.session_id}` | **User:** `{st.session_state.user_id}`")

# --- Display Chat History ---
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- Optional File/Voice Input (Sidebar) ---
with st.sidebar:
    st.header("📎 Attachments")
    uploaded_file = st.file_uploader("Upload File", type=["txt", "mp4", "wav", "png", "jpg"])
    recorded_audio = st.audio_input("Record Audio")

# --- Chat Input & API Communication ---
if prompt := st.chat_input("Type your message to the agent..."):
    
    # 1. Display User Message
    with st.chat_message("user"):
        st.markdown(prompt)
        if uploaded_file: st.caption(f"*(Attached: {uploaded_file.name})*")
        if recorded_audio: st.caption("*(Attached: Voice Recording)*")
            
    st.session_state.messages.append({"role": "user", "content": prompt})

    # 2. Build ADK Payload
    message_parts = []
    
    # Process file as inline base64
    if uploaded_file:
        b64_data = base64.b64encode(uploaded_file.getvalue()).decode("utf-8")
        mime_type = uploaded_file.type if uploaded_file.type else "application/octet-stream"
        message_parts.append({"inlineData": {"mimeType": mime_type, "data": b64_data}})
            
    # Process audio as inline base64
    if recorded_audio:
        b64_audio = base64.b64encode(recorded_audio.getvalue()).decode("utf-8")
        message_parts.append({"inlineData": {"mimeType": "audio/wav", "data": b64_audio}})
            
    message_parts.append({"text": prompt})

    payload = {
        "appName": APP_NAME,
        "userId": st.session_state.user_id,
        "sessionId": st.session_state.session_id,
        "newMessage": { "role": "user", "parts": message_parts }
    }

    # 3. Transmit and Display Response
    with st.chat_message("assistant"):
        with st.spinner("Agent is thinking..."):
            try:
                response = asyncio.run(transmit_payload_async(payload))
                assistant_text = safe_extract_response(response.json())
                
                st.markdown(assistant_text)
                st.session_state.messages.append({"role": "assistant", "content": assistant_text})
                
            except Exception as e: 
                st.error(f"Transmission error: {e}")