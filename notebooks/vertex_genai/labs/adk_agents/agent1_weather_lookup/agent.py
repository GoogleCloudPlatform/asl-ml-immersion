# pylint: skip-file
from google.adk.agents import Agent

MODEL = "gemini-2.0-flash"

from .tools import get_weather

root_agent = None  # TODO - define the weather agent
