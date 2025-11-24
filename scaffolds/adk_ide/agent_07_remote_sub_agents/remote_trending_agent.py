"""
Remote Trending Topics Agent
"""

import logging

from dotenv import load_dotenv
from google.adk.a2a.utils.agent_to_a2a import to_a2a
from google.adk.agents import Agent
from google.adk.tools import google_search

logger = logging.getLogger(__name__)
logging.basicConfig(format="[%(levelname)s]: %(message)s", level=logging.INFO)

load_dotenv()

logger.info("Creating ADK Trending Topics Agent")

root_agent = Agent(
    model="gemini-2.5-flash",
    name="trending_topics_agent",
    instruction="""
    You are a social media trends analyst related to python topics.
    Your job is to search the web for current python trending topics,
    particularly from social platforms.

    When asked about trends:
    1. Search for "recent python trending topics" or similar queries
    2. Extract the top 3 trending topics
    3. Return them in a JSON format

    Focus on actual trends from the last 2 weeks.

    You MUST return your response in the following JSON format:
    {
        "trends": [
            {
                "topic": "Topic name",
                "description": "Brief description (1-2 sentences)",
                "reason": "Why it's trending"
            },
            {
                "topic": "Topic name",
                "description": "Brief description (1-2 sentences)",
                "reason": "Why it's trending"
            },
            {
                "topic": "Topic name",
                "description": "Brief description (1-2 sentences)",
                "reason": "Why it's trending"
            }
        ]
    }

    Only return the JSON object, no additional text.
    """,
    tools=[google_search],
)

# Make the agent A2A-compatible
a2a_app = to_a2a(root_agent, port=10020)
