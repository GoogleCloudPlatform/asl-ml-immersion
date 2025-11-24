# pylint: skip-file
from google.adk.agents import Agent, SequentialAgent
from google.adk.tools import google_search
from google.adk.tools.agent_tool import AgentTool

MODEL = "gemini-2.5-pro"

# Create the Python Trending Topics ADK Agent
trending_topics_agent = Agent(
    model=MODEL,
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

# Create the Trend Analyzer ADK Agent
analyzer_agent = Agent(
    model="gemini-2.5-pro",
    name="trend_analyzer_agent",
    instruction="""
    You are a data analyst specializing in trend analysis. When given a trending topic,
    perform deep research to find quantitative data and insights.

    For each trend you analyze:
    1. Search for statistics, numbers, and metrics related to the trend
    2. Look for:
       - Engagement metrics (views, shares, mentions)
       - Growth rates and timeline
       - Geographic distribution
       - Related hashtags or keywords
    3. Provide concrete numbers and data points

    Keep it somehow concise

    Always prioritize quantitative information over qualitative descriptions.
    """,
    tools=[google_search],
)

# Create the Host ADK Agent
host_agent = SequentialAgent(
    name="trend_analysis_host",
    sub_agents=[trending_topics_agent, analyzer_agent],
)
root_agent = host_agent