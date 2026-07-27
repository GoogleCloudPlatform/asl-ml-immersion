import streamlit as st
import asyncio
import uuid
import os
import vertexai
from vertexai import agent_engines

# --- 1. Cloud & Agent Engine Configuration ---
# Set these variables or export them as environment variables
PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT", "PROJECT_ID")
LOCATION = os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1")
AGENT_ENGINE_ID = os.getenv("GOOGLE_CLOUD_AGENT_ENGINE_ID", "projects/PROJECT_ID/locations/us-central1/reasoningEngines/AGENT_ENGINE_ID")

st.set_page_config(page_title="Production Agent Engine Chat", page_icon="💬", layout="centered")

# Initialize Vertex AI SDK
if not PROJECT_ID or not AGENT_ENGINE_ID:
    st.error("Missing GCP Environment Configuration. Ensure GOOGLE_CLOUD_PROJECT and GOOGLE_CLOUD_AGENT_ENGINE_ID are set.")
    st.stop()

vertexai.init(project=PROJECT_ID, location=LOCATION)

# --- 2. Retrieve & Cache Deployed Agent Resource ---
@st.cache_resource
def get_deployed_agent(resource_id: str):
    """Retrieves and caches the deployed Agent Engine resource."""
    try:
        # Resolves fully qualified name: projects/{project}/locations/{location}/reasoningEngines/{id}
        return agent_engines.get(resource_id)
    except Exception as e:
        st.error(f"Failed to retrieve deployed Agent Engine: {e}")
        st.stop()

remote_agent = get_deployed_agent(AGENT_ENGINE_ID)

# --- 3. Async Stream Parsing Generators ---
async def stream_agent_text_async(user_id: str, session_id: str, message_content: dict):
    """Asynchronously calls Agent Engine and yields incremental text parts."""
    try:
        async for event in remote_agent.async_stream_query(
            user_id=user_id,
            session_id=session_id,
            message=message_content
        ):
            # Safe-extract text part from the ADK Event object
            if hasattr(event, "content") and event.content:
                parts = getattr(event.content, "parts", [])
                for part in parts:
                    if hasattr(part, "text") and part.text:
                        yield part.text
            # Fallback wrapper for raw dictionary responses
            elif isinstance(event, dict) and "content" in event:
                content = event["content"]
                if content and "parts" in content:
                    for part in content["parts"]:
                        if "text" in part and part["text"]:
                            yield part["text"]
    except Exception as e:
        yield f"\n\n⚠️ **Streaming error occurred**: {e}"

def run_async_generator(async_gen):
    """Utility helper to run an async generator synchronously for Streamlit."""
    loop = asyncio.new_event_loop()
    try:
        while True:
            try:
                chunk = loop.run_until_complete(async_gen.__anext__())
                yield chunk
            except StopAsyncIteration:
                break
    finally:
        loop.close()

# --- 4. Streamlit App Initialization ---
if "user_id" not in st.session_state: 
    # Changed from "_" to "-" to prevent validation errors
    st.session_state.user_id = f"user-{uuid.uuid4().hex[:6]}"

if "session_id" not in st.session_state:
    # Changed from "_" to "-" to adhere to GCP's session naming conventions
    st.session_state.session_id = f"s-{uuid.uuid4().hex[:8]}"
    
    with st.spinner("Registering secure Cloud Session..."):
        try:
            # Pre-register our custom session ID on Google Cloud's Agent Engine
            asyncio.run(remote_agent.async_create_session(
                user_id=st.session_state.user_id,
                session_id=st.session_state.session_id
            ))
        except Exception as e: 
            st.error(f"Could not initialize Agent Engine session. Is your GCP SDK authenticated?\nError: {e}")
            st.stop()

if "messages" not in st.session_state: 
    st.session_state.messages = []

# --- 5. UI Setup ---
st.title("💬 Production Agent Engine Chat")
st.caption(f"**GCP Project:** `{PROJECT_ID}` | **Session:** `{st.session_state.session_id}`")

# Display Chat History
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- 6. Media Attachments (Sidebar) ---
with st.sidebar:
    st.header("📎 Attachments")
    uploaded_file = st.file_uploader("Upload File", type=["txt", "mp4", "wav", "png", "jpg"])
    recorded_audio = st.audio_input("Record Audio")

# --- 7. Interactive Input & Execution ---
if prompt := st.chat_input("Type your message..."):
    # Render user prompt
    with st.chat_message("user"):
        st.markdown(prompt)
        if uploaded_file: 
            st.caption(f"*(Attached: {uploaded_file.name})*")
        if recorded_audio: 
            st.caption("*(Attached: Voice Recording)*")

    st.session_state.messages.append({"role": "user", "content": prompt})

    # Prepare multimodal content list using official Schema formats
    message_parts = []
    
    if uploaded_file:
        message_parts.append({
            "inline_data": {
                "data": uploaded_file.getvalue(),  # Bytes payload
                "mime_type": uploaded_file.type or "application/octet-stream"
            }
        })
        
    if recorded_audio:
        message_parts.append({
            "inline_data": {
                "data": recorded_audio.getvalue(),
                "mime_type": "audio/wav"
            }
        })

    # Add the core prompt text
    message_parts.append({"text": prompt})

    # Build compliant LlmRequest payload structure
    message_content = {
        "role": "user",
        "parts": message_parts
    }

    # Stream back model tokens in real-time
    with st.chat_message("assistant"):
        async_generator = stream_agent_text_async(
            user_id=st.session_state.user_id,
            session_id=st.session_state.session_id,
            message_content=message_content
        )
        # Pass sync-wrapped generator to st.write_stream to handle real-time rendering
        assistant_text = st.write_stream(run_async_generator(async_generator))
        
    st.session_state.messages.append({"role": "assistant", "content": assistant_text})
