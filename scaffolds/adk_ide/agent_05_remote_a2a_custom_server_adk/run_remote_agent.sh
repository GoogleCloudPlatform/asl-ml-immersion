#!/bin/bash
export PATH=$PATH:~/.local/bin
uv run --active uvicorn agent_05_remote_a2a_custom_server_adk.remote_weather_agent:a2a_app --host localhost --port 10020
