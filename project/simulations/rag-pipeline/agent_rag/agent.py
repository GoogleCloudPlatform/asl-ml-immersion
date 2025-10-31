import asyncio
from unittest import result
from google.adk.agents import LlmAgent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types
from google import genai
from google.adk.tools import VertexAiSearchTool

## TODO: change to using .env values
# GCP Globals
PROJECT_ID = "qwiklabs-asl-00-58d3f08e551b"
REGION = "global"

# VertexAISearch app/datastore information
VERTEXAI_SEARCH_APP_NAME = "mock_keyiq_search"
DATASTORE_ID = "mock-keyiq-datastore_1761844635062"
DATASTORE_PATH = f"projects/{PROJECT_ID}/locations/{REGION}/collections/default_collection/dataStores/{DATASTORE_ID}"

# Generative Model to use
GENERATIVE_MODEL = "gemini-2.5-flash"

# VertexAISearch tool to be used in rag_agent
vertex_search_tool = VertexAiSearchTool(data_store_id=DATASTORE_PATH)
def vertex_search_wrapper(query):
    result = vertex_search_tool.run({"query": query})
    return {"search_result": result }

# Test Session/User Constants
SESSION_ID = "session_vsearch_1"
USER_ID = "user_vsearch_1"

# Function to call after agent completes
def post_search_logic(
    tool,
    args,
    tool_context,
    tool_response
):
    results = tool_response.get("results", []) if isinstance(tool_response, dict) else []

    wrapped_results = []
    for r in results:
        snippet = r.get("snippet")
        metadata = r.get("metadata", {})
        wrapped_results.append({
            "snippet": snippet,
            "source": metadata.get("source"),
            "document_id": metadata.get('document_id'),
            "score": metadata.get("score")
        })

    new_response = {
        "wrapped_results": wrapped_results,
        "original_response": tool_response
    }
    
    return new_response

    """
    grounding_metadata = context.get("groundingMetadata", {})
    conversation_history = context.get("conversationHistory", [])

    # Extract snippet
    chunks = grounding_metadata.get("groundingChunks", [])
    snippet = chunks[0].get("snippet", "No snippet foud.") if chunks else "No reference found."
    source_uri = chunks[0].get("uri", "No source URI.") if chunks else "No source URI."

    # Get suggestions
    prompt = f\"""
    Based on the conversation history: {conversation_history}
    
    And the following grounding sources: {grounding_metadata}
    
    Suggst two follow-up questions the user might ask next.
    \"""

    client = genai.Client(vertexai=True, location="us-central1")
    suggestion_response = client.models.generate_content(
        model=GENERATIVE_MODEL, contents=prompt
    )
    suggestions = suggestion_response.text.strip().split("\n")

    response["source_snippet"] = {"snippet": snippet, "source": source_uri}
    response["suggestions"] = suggestions
    return response
    """

# Agent Definition
root_agent = LlmAgent(
    # name, description available to other agents (Clear and descriptive metadata)
    name="vertex_search_app",
    description=f"Agent to answer user questions using indexed documents in the <{VERTEXAI_SEARCH_APP_NAME}> VertexAISearch app.",
    # Needs to be a gemini model, instruction is the system instruction for agent
    model=GENERATIVE_MODEL,
    # TODO: Decide how you are setting these values
    generate_content_config=types.GenerateContentConfig(
                                temperature=0.9,
                                top_p=0.9,
                                top_k=40,
                            ),
    instruction=f"""
        <PERSONA>
            You are an english literature academic with expertise on old english books.
        </PERSONA>
        <INSTRUCTIONS>
            1. Use the vertexai serach tool to find information relevant to the question you are asked.
            2. Use the relevant information you found to answer the question.
        <RULES>
            1. Only use data in the datastore to answer questions.
        </RULES>
        <TONE>
            1. Answer should be clear and concise.
            2. Answers should have an english literature academic tone and focus
        </TONE>
    """,
    # What resources the agent has access to (This is connected to the VertexAISearch App that indexed all files from GCS bucket)
    tools=[vertex_search_tool],
    after_tool_callback=post_search_logic
)

# callback
# after tool use callback takes the event
# grab the event grounding metadata (seen below)
# Agent Engine
# Write deployment.app to deploy to agent engine
# Docs on the tool: https://github.com/google/adk-python/blob/main/src/google/adk/tools/vertex_ai_search_tool.py
# To deploy (docs: https://google.github.io/adk-docs/deploy/agent-engine/#prerequisites-ad)
    ## Run "uvx agent-starter-pack enhance --adk -d agent_engine" from rag-pipeline
    ## Run "make backend" from rag-pipeline
"""
# Session and Runner Setup
session_service_vertexai_search = InMemorySessionService()
runner_vertexai_search = Runner(
    agent=rag_agent, app_name=VERTEXAI_SEARCH_APP_NAME, session_service=session_service_vertexai_search
)
session_vsearch = session_service_vertexai_search.create_session(
    app_name=VERTEXAI_SEARCH_APP_NAME, user_id=USER_ID, session_id=SESSION_ID
)

# Agent Interaction Function
def call_rag_agent(question):
    print(f"\n--- Running Vertex AI Search Agent ---")
    print(f"User Question: <{question}>")

    content = types.Content(role='user', parts=[types.Part(text=question)])
    agent_answer = "No answer generated"

    try:
        for event in runner_vertexai_search.run_async(
            user_id=USER_ID, session_id=SESSION_ID, new_message=content
        ):
            # results embedded in model's response
            if event.is_final_response() and event.content and event.content.parts:
                agent_answer = event.content.parts[0].text.strip()
                print(f"Agent Answer: <{agent_answer}>")

                # check source citations
                if event.grounding_metadata:
                    print(f"Grounding Metadata use to generate \"Agent Answer\" from <{question}>: <{event.grounding_metadata}>")
    except Exception as error:
        print(f"An error occured during agent invokation or execution.\nError: <{error}>")

# --- Run Example ---
async def run_vertex_search_example():
    await call_rag_agent("Who was frankenstein?")
    await call_rag_agent("What happened to Romeo and Juliet?")

if __name__=="__main__":
    print("--- RUNNING AGENT LOCALLY ---")

    try:
        asyncio.run(run_vertex_search_example)
    except RuntimeError as error:
        if "cannot be called from a running event loop" in str(error):
            print(f"Skipping execution in running event loop (like Colab/Jupyter). Run locally.")
        else:
            raise error
"""