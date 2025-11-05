import time, uuid
from google.adk.agents import LlmAgent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

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

# Tools
# TODO: should have a tool for each hyperparameter? (Test and see what works better)
# TODO: Finish docstring
# TODO: Implement functionality with global state
def change_hyperparameters(temperature: float, top_p: float, top_k: int):
    """
    Changes the hyperparameters of the test state

    Description
    -----------
    This function changes the hyperparameter values temperature, top_p, and top_k of the test state.
    These values are used in the generator of a RAG system to generate answers to users questions after the retriever has retrieved relevant documents.
    
    Args
    ----
    temperature (float) : x
    top_p (float) : x
    top_k (int) : x

    Returns
    -------
    None : Nothing is returned. The hyperparameter values are update in the global state object as a side effect.
    """
    # Update state hyperparameter values using the global state object
    # state.set_temp(temperature)
    # state.set_top_p(top_p)
    # state.set_top_k(top_k)
    print("Changing hyperparameters")

# TODO: Finish docstring
# TODO: Implement functionality with global state
def change_workspace_prompt(prompt: str):
    """
    Changes the workspace prompt of the test state

    Description
    -----------
    This function changes the workspace prompt value of the test state.
    This value is used in the generator of a RAG system to generate answers to user's questions after the retriever has retrieved relevant documents.
    
    Args
    ----
    prompt (str) : The system instruction 

    Returns
    -------
    None : Nothing is returned. The workspace prompt value is updated in the global state object as a side effect.
    """
    # Update state workspace prompt using the global state object
    # state.set_workspace_prompt(prompt)
    print("Changing Workspace Prompt")

#TODO: Does this need to be a different kind of agent? Just need to decide what tool to use and use it
#TODO: Finish system instruction
def get_root_agent():
    return LlmAgent(
        # name, description available to other agents (Clear and descriptive metadata)
        name="mechanic_agent",
        description=f"Changes the test state (hyperparameters, system_prompt, and/or questions) of a RAG system to improve system performance.",
        # Needs to be a gemini model, instruction is the system instruction for agent
        model=GENERATIVE_MODEL,
        instruction=f"""
            <PERSONA>
                You are an AI agent with updating the test state to improve the issues identified in <INTERPRETATIONS>
            </PERSONA>
            <GOAL>
                Change the test state state in a way that w
            </GOAL>
            <INSTRUCTIONS>
                1. Use the vertexai serach tool to find information relevant to the question you are asked.
                2. Use the relevant information you found to answer the question.
            <RULES>
                1. Only use data in the datastore to answer questions.
            </RULES>
            <TOOLS>
                change_hyperparameters - Use this function to update the hyper
                2. Answers should have an english literature academic tone and focus
            </TOOLS>
        """,
        # What the mechanic agent can change in state to improve testing results
        tools=[change_hyperparameters, change_workspace_prompt]
    )

# mechanic agent should have a singluar session_id (remember all the previous changes)
async def create_session(session_service, user_id: str, session_id: str):
    return await session_service.create_session(
                                    app_name=VERTEXAI_SEARCH_APP_NAME, 
                                    user_id=user_id, 
                                    session_id=session_id
                                )

# Agent Interaction Function
async def call_mechanic_agent(interpretations: dict, session_id: str = None):
    print(f"\n--- Running Mechanic Agent ---")
    print(f"Q/A Interpretations: <{interpretations}>")
    prompt_text = f"""
    <INTERPRETATIONS>
        {interpretations}
    </INTERPRETATIONS>
    """
    start_time = time.perf_counter()

    # Agent Definition (Intiailizing this everytime so not biasing the test results)
    ## TODO: Want memory to persist so that agent has context on what it changed last. Should this stuff happen everytime?
    root_agent = get_root_agent()
    session_service_vertexai_search = InMemorySessionService()
    runner_vertexai_search = Runner(
            agent=root_agent, app_name=VERTEXAI_SEARCH_APP_NAME, session_service=session_service_vertexai_search
    )

    # Only want one session throghout the whole system run. Want the agent to know what has been tried in the past.
    user_id = str(uuid.uuid4())
    if not session_id:
        session_creation_start = time.perf_counter()

        session_id = str(uuid.uuid4())
        session = await create_session(session_service_vertexai_search, user_id=user_id, session_id=session_id)
        session_id = session.id

        session_creation_end = time.perf_counter()
        print(f"Created session <{session_id}> in <{session_creation_end-session_creation_start}> seconds.")


    content = types.Content(role='user', parts=[types.Part(text=prompt_text)])

    # TODO: Handle agent response appropriately
    try:
        start_time = time.perf_counter()
        for event in runner_vertexai_search.run(
            user_id=user_id, session_id=session_id, new_message=content
        ):
            # results embedded in model's response
            if event.is_final_response() and event.content:
                print(f"Possible agent results here")

        end_time = time.perf_counter()
        print(f"Agent RunTime: <{end_time - start_time}> secs.")
    except Exception as error:
        print(f"An error occured during agent invokation or execution.\nError: <{error}>")