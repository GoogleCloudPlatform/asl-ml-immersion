"""
Remote A2A Agent - Entry Point
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import uvicorn
from google.adk.a2a.utils.agent_to_a2a import to_a2a
from starlette.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from remote_weather_agent import root_agent


def main():
    port = 10020
    host = "0.0.0.0"
    base_url = f"http://localhost:{port}"

    a2a_app = to_a2a(root_agent, port=10020)

    a2a_app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    uvicorn.run(a2a_app, host=host, port=port)


if __name__ == "__main__":
  # Load environment variables from .env file
  try:    
      env_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env")
      print(f"Loading .env from {env_file}")
      load_dotenv(dotenv_path=env_file)
  except Exception as e:
      print(f"Error loading .env file: {e}")
  main()