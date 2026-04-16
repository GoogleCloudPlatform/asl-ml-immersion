import requests
import base64
import uuid
import os
import json

# --- CONFIGURATION ---
ADK_URL = "http://localhost:8000/run"  # Standard ADK endpoint
AGENT_NAME = "default"                 # Name of the agent defined in your ADK setup
FILE_PATH = "example.pdf"              # Path to your local PDF file

def encode_file_to_base64(file_path):
    """Reads a file and converts it to a Base64 string."""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")
        
    with open(file_path, "rb") as f:
        file_data = f.read()
        # Encode to base64 bytes, then decode to utf-8 string for JSON
        return base64.b64encode(file_data).decode('utf-8')

def send_request_with_artifact():
    # 1. Create a Session ID
    # In ADK, the client usually generates the UUID. Re-use this ID 
    # in subsequent calls to continue the conversation.
    session_id = str(uuid.uuid4())
    print(f"🔹 Starting Session: {session_id}")

    # 2. Prepare the Artifact (PDF)
    try:
        pdf_b64 = encode_file_to_base64(FILE_PATH)
        print(f"🔹 Encoded {FILE_PATH} ({len(pdf_b64)} bytes)")
    except Exception as e:
        print(f"❌ Error encoding file: {e}")
        return

    # 3. Construct the Payload
    # The structure follows the Google Generative AI 'Content' format.
    payload = {
        "agent_name": AGENT_NAME,
        "session_id": session_id,
        "query": {
            "role": "user",
            "parts": [
                # Text Instruction
                {
                    "text": "Please summarize this document and extract the key dates."
                },
                # Binary Artifact
                {
                    "inline_data": {
                        "mime_type": "application/pdf",
                        "data": pdf_b64
                    }
                }
            ]
        }
    }

    # 4. Send the Request
    print("🔹 Sending request to ADK...")
    try:
        response = requests.post(
            ADK_URL, 
            headers={"Content-Type": "application/json"},
            data=json.dumps(payload)
        )
        
        # 5. Handle Response
        if response.status_code == 200:
            result = response.json()
            # The actual text response is usually nested in the result
            print("\n✅ Response from Agent:")
            print("------------------------")
            # Adjust based on your specific ADK response schema, 
            # usually it is result['text'] or similar
            print(json.dumps(result, indent=2))
        else:
            print(f"❌ Error {response.status_code}: {response.text}")

    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to ADK. Is the server running on localhost:8000?")

if __name__ == "__main__":
    send_request_with_artifact()
