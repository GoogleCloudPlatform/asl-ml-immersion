#!/bin/bash
export PATH=$PATH:~/.local/bin
uv python -m uvicorn agent_05_remote_a2a_custom_server_adk.remote_weather_agent --host localhost --port 10021