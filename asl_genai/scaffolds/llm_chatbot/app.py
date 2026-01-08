"""Streamlit Chatbot App"""

import os
import time

import streamlit as st
from google import genai
from google.genai.types import Content, Part

st.set_page_config(page_title="Chat with Gemini", page_icon="♊")

st.title("Chat with Gemini")

st.markdown("Welcome to this simple web application to chat with Gemini")

PROJECT_ID = os.environ.get("GCP_PROJECT")
LOCATION = os.environ.get("GCP_REGION")

client = genai.Client(project=PROJECT_ID, vertexai=True, location=LOCATION)

if "gemini_model" not in st.session_state:
    st.session_state["gemini_model"] = "gemini-2.0-flash"

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(name=message["role"], avatar=message["avatar"]):
        st.markdown(message["content"])


def generate_response(input_text):
    chat = client.chats.create(
        model=st.session_state["gemini_model"],
        history=[
            Content(
                role=message["role"],
                parts=[Part.from_text(text=message["content"])],
            )
            for message in st.session_state.messages[:-1]
        ],
    )
    return chat.send_message(input_text)


def stream(text):
    for word in text.split(" "):
        yield word + " "
        time.sleep(0.02)


# React to user input
if prompt := st.chat_input("Write a promt"):
    # 1. Write the user message
    with st.chat_message(name="user", avatar=None):
        st.write(prompt)
    # 2. Add user message to message history
    st.session_state.messages.append(
        {"role": "user", "content": prompt, "avatar": None}
    )

    # 3. Call Gemini and write the response
    with st.chat_message(name="assistant", avatar="assets/gemini-icon.png"):
        response = generate_response(prompt)
        st.write_stream(stream(response.text))
    # 4. Add Gemini response to message history
    st.session_state.messages.append(
        {
            "role": "model",
            "content": response.text,
            "avatar": "assets/gemini-icon.png",
        }
    )
