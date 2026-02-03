export PATH=$PATH:~/.local/bin
uv run --active uvicorn agent_05_a2a_simple.remote_math_agent:a2a_app --host localhost --port 10020