#!/bin/bash
export PATH=$PATH:~/.local/bin
uv run --active uvicorn agent_05_remote_sub_agent_a2a.remote_weather_agent:a2a_app --host localhost --port 10020
