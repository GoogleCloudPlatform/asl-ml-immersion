import time, uuid
from google.adk.agents import LlmAgent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types
from google.adk.tools import VertexAiSearchTool

## TODO: change to using .env values
# GCP Globals
PROJECT_ID = "qwiklabs-asl-00-58d3f08e551b"
REGION = "global"

# VertexAISearch app/datastore information
VERTEXAI_SEARCH_APP_NAME = "agents"
DATASTORE_ID = "mock-keyiq-datastore_1761844635062"
DATASTORE_PATH = f"projects/{PROJECT_ID}/locations/{REGION}/collections/default_collection/dataStores/{DATASTORE_ID}"

# Generative Model to use
GENERATIVE_MODEL = "gemini-2.5-flash"

# VertexAISearch tool to be used in rag_agent
vertex_search_tool = VertexAiSearchTool(data_store_id=DATASTORE_PATH)

#TODO: add functionality to pass in the system instruction (Another thing to tune for)
def get_root_agent(temperature, top_p, top_k):
    return LlmAgent(
    # name, description available to other agents (Clear and descriptive metadata)
    name="vertex_search_app",
    description=f"Agent to answer user questions using indexed documents in the <{VERTEXAI_SEARCH_APP_NAME}> VertexAISearch app.",
    # Needs to be a gemini model, instruction is the system instruction for agent
    model=GENERATIVE_MODEL,
    generate_content_config=types.GenerateContentConfig(
                                temperature=temperature,
                                top_p=top_p,
                                top_k=top_k,
                            ),
    instruction=f"""
        <PERSONA>
            You are an english literature academic with expertise on old english books.
        </PERSONA>
        <INSTRUCTIONS>
            1. Use the vertexai search tool to find information relevant to the question you are asked.
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
)

async def create_session(session_service, user_id: str, session_id: str):
    return await session_service.create_session(
                                    app_name=VERTEXAI_SEARCH_APP_NAME, 
                                    user_id=user_id, 
                                    session_id=session_id
                                )

# Agent Interaction Function
## TODO: Each call to the rag agent should be a new session
## TODO: Want to create a singluar tuning data structure that includes (question, temperature, top_p, top_k)
async def call_rag_agent(question, temperature, top_p, top_k):
    print(f"\n--- Running Vertex AI Search Agent ---")
    print(f"User Question: <{question}>")
    start_time = time.perf_counter()

    # Agent Definition (Intiailizing this everytime so not biasing the test results)
    root_agent = get_root_agent(temperature, top_p, top_k)
    session_service_vertexai_search = InMemorySessionService()
    runner_vertexai_search = Runner(
            agent=root_agent, app_name=VERTEXAI_SEARCH_APP_NAME, session_service=session_service_vertexai_search
    )

    # Create session every time rag agent is invoked
    session_creation_start = time.perf_counter()
    session_id = str(uuid.uuid4())
    user_id = str(uuid.uuid4())
    session = await create_session(session_service_vertexai_search, user_id=user_id, session_id=session_id)
    session_id = session.id
    user_id = session.user_id
    session_creation_end = time.perf_counter()
    print(f"Created session <{session_id}> in <{session_creation_end-session_creation_start}> seconds.")


    content = types.Content(role='user', parts=[types.Part(text=question)])
    agent_response = {
        'question': question,
        'answer': 'No answer generated',
        'context': []
    }

    try:
        start_time = time.perf_counter()
        for event in runner_vertexai_search.run(
            user_id=user_id, session_id=session_id, new_message=content
        ):
            # results embedded in model's response
            if event.is_final_response() and event.content:
                agent_answer = event.content.parts[0].text.strip()
                agent_response['answer'] = agent_answer

                chunk_idx = 0
                for chunk in event.grounding_metadata.grounding_chunks:
                    chunk_text = chunk.retrieved_context.text.strip()
                    chunk_source = chunk.retrieved_context.uri
                    agent_response['context'].append({
                        "text": chunk_text,
                        "source": chunk_source
                    })

        end_time = time.perf_counter()
        print(f"Agent RunTime: <{end_time - start_time}> secs.")

        return agent_response
    except Exception as error:
        print(f"An error occured during agent invokation or execution.\nError: <{error}>")

        return agent_response

# Notes
# callback
# after tool use callback takes the event
# grab the event grounding metadata (seen below)
# Agent Engine
# Write deployment.app to deploy to agent engine
# Docs on the tool: https://github.com/google/adk-python/blob/main/src/google/adk/tools/vertex_ai_search_tool.py
# To deploy (docs: https://google.github.io/adk-docs/deploy/agent-engine/#prerequisites-ad)
    ## Run "uvx agent-starter-pack enhance --adk -d agent_engine" from rag-pipeline
    ## Run "make backend" from rag-pipeline