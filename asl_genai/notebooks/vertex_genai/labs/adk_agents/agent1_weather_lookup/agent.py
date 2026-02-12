# pylint: skip-file
from google.adk.agents import Agent

MODEL = "gemini-2.5-flash"

from .tools import get_weather

root_agent = None  # TODO - define the weather agent
