import time, uuid
from google.adk.agents import LlmAgent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types
from state import system_state

## TODO: change to using .env values
# GCP Globals
PROJECT_ID = "qwiklabs-asl-00-58d3f08e551b"
REGION = "global"

# VertexAISearch app/datastore information
MECHANIC_APP_NAME = "agents"
DATASTORE_ID = "mock-keyiq-datastore_1761844635062"
DATASTORE_PATH = f"projects/{PROJECT_ID}/locations/{REGION}/collections/default_collection/dataStores/{DATASTORE_ID}"

# Generative Model to use
GENERATIVE_MODEL = "gemini-2.5-flash"

# Tools
# TODO: should have a tool for each hyperparameter? (Test and see what works better)
def change_hyperparameters(temperature: float, top_p: float, top_k: int):
    """
    Change the generation hyperparameters in the test state.

    This tool updates the RAG answer generation hyperparameters.
    These parameters affect how the model generates text after retrieval has selected relevant
    context documents.

    Parameters
    ----------
    temperature : float
        Controls randomness in generation. Higher values produce more varied output.
        Range: [0.0, 1.0]
    top_p : float
        Nucleus sampling parameter. Limits token selection to the most probable tokens whose 
        cumulative probability mass is <= top_p.
        Range: [0.0, 1.0]
    top_k : int
        Limits generation to the top-k most probable next tokens. 
        Range: [0, 60]

    Returns
    -------
    None

    Example
    -------
    # Increase creativity and indeterminacy in the RAG answer generation:
    The current hyperparameters are: {temperature=0.6, top_p=0.9, top_k=30}
    change_hyperparameters(temperature=0.9, top_p=0.9, top_k=50)
    """
    # Update state hyperparameter values using the global state object
    system_state.set_temperature(temperature)
    system_state.set_top_p(top_p)
    system_state.set_top_k(top_k)
    print("Changing hyperparameters")

def change_workspace_prompt(prompt: str):
    """
    Change the workspace system prompt used during answer generation.

    This tool updates an injection into the workspace system prompt for the RAG engine.
    The system prompt acts as the system instruction that guides how responses are generated after relevant documents have been retrieved in the RAG pipeline.

    Parameters
    ----------
    prompt : str
        The new system-level instruction text that the generator should follow.

    Returns
    -------
    None

    Example
    -------
    # Update the behavior of the generator:
    The results are too verbose and tend to hallucinate.
    change_workspace_prompt(
        prompt="Answer concisely and focus only on verified retrieved evidence."
    )
    """
    # Update state workspace prompt using the global state object
    system_state.set_system_prompt(prompt)
    print("Changing Workspace Prompt")

#TODO: Does this need to be a different kind of agent? Just need to decide what tool to use and use it
def get_root_agent():
    return LlmAgent(
        # name, description available to other agents (Clear and descriptive metadata)
        name="mechanic_agent",
        description=f"Changes the test state (hyperparameters and workspace prompt) of a RAG system to improve system performance.",
        # Needs to be a gemini model, instruction is the system instruction for agent
        model=GENERATIVE_MODEL,
        instruction=f"""
            <PERSONA>
                You are an expert at RAG fine-tuning based on a series of testing results.
            </PERSONA>
            <GOAL>
                Adjust the RAG Engine's workspace prompt and hyperparameters to resolve issues in <INTERPRETATIONS>.
            </GOAL>
            <INSTRUCTIONS>
                1. Read and understand the feedback provided by <INTERPRETATIONS>.
                2. Using the current hyperparameters and workspace prompt, decide whether to change hyperparameters, update the workspace prompt, both, or neither.
                3. Use the {{change_hyperparameters, change_workspace_prompt}} tools provided to you to make the relevant changes.
                4. If you determine that the feedback provided by <INTERPRETATIONS> is poor just because there are likely contradictions or conflicting information in the document base the RAG engine is retrieving from, stop running.
                5. Provide reasoning for your actions.
            </INSTRUCTIONS>
            <RULES>
                1. Ensure that you make relative changes to the hyperparameters and workspace prompt.
                2. If <INTERPRETATIONS> leads you to believe that the RAG performance was poor because of conflicting information in retrieval documents, do not make any changes.
                3. Respond only in JSON according to the schema provided in <OUTPUT>.
            </RULES>
            <EXAMPLES>
            (1)
                Interpretations: [
                    "The model\'s answer similarity is low (0.3), focusing on a different aspect of the Mad Hatter\'s relationship with Time compared to the Golden Answer. However, the answer is fully grounded in the retrieval context (1.0), which was highly relevant (1.0) and sourced correctly."
                    "The KeyIQ answer demonstrates high groundedness (1.0) and correctly identified the source. However, its semantic similarity to the golden answer is medium (0.6), as it misses several key thematic aspects and underlying motivations. The retrieval context also shows medium relevance (0.6) because it lacks explicit details about the reasons for the journey."
                ]
                State: {{temperature: 0.2, top-p: 0.4, top-k: 30, workspace_prompt: ''}}
                General Summary: The RAG system excels at summarizing the information based on the retrieved context, but, due to the relatively low similarity exhibited by the interpretations of the results, it must be struggling with retrieving the information being prompted of it. Therefore, there must be conflicting or missing information in the documents.
                Action(s): Exit; no parameter should change.
            (2)
                Interpretations: [
                    "The model successfully retrieved the correct source and provided highly relevant context. However, the semantic similarity between the KeyIQ answer and the Golden Answer is medium (0.6), with the KeyIQ answer focusing more on literal explanations versus the Golden Answer\'s symbolic depth. Additionally, the answer\'s groundedness is medium (0.7), indicating it is partially grounded, with some details less explicitly supported by the context.",
                    "The model\'s answer is highly similar to the reference answer (0.9) and correctly retrieved the source (True). While largely grounded in the provided context (0.8), the explanation notes that some details were not explicitly present in the context. The retrieval context itself was only moderately relevant (0.6), indicating it did not explicitly state the main villain, which likely affected the answer\'s full groundedness."
                ]
                State: {{temperature: 0.4, top-p: 0.9, top-k: 40, workspace_prompt: ''}}
                General Summary: The RAG system seems to be doing somewhat well with semantic similarity, but could improve on its groundedness and the search functionality. Therefore, some hyperparameters should be adjusted and a workspace prompt could be injected to improve search results.
                Action(s): Change hyperparameters to {{temperature: 0.1, top-p: 0.7, top-k: 30}}
                           Change workspace prompt to "Ensure that any specifics that are returned in the context that pertain to the prompt are generated"
            (3)
                Interpretations: [
                    "The model retrieved the correct source. However, the KeyIQ answer directly contradicts the Golden answer, indicating a very low semantic similarity (0.1). While the KeyIQ answer is highly grounded in the provided retrieval context (0.9), the retrieval context itself is largely irrelevant to the specific question, scoring low on relevance (0.1).",
                    "The KeyIQ answer demonstrates high groundedness (1.0) and correctly identified the source. However, its semantic similarity to the golden answer is medium (0.6), as it misses several key thematic aspects and underlying motivations. The retrieval context also shows medium relevance (0.6) because it lacks explicit details about the reasons for the journey."
                ]
                State: {{temperature: 0.4, top-p: 0.9, top-k: 40, workspace_prompt: ''}}
                General Summary: The RAG system seems to be performing poorly despite being highly grounded. Both the retrieval context and similarity are low, which indicates that the correct information is not being pulled out. Therefore, the workspace prompt should be changed.
                Action(s): Change workspace prompt to "Only retrieve chunks that are directly related to the following prompt:"
            </EXAMPLES>
            <OUTPUT>
            {{"reasoning":<explanation for why you changed hyperparameters or workspace prompt>}}
            </OUTPUT>
        """,
        # What the mechanic agent can change in state to improve testing results
        tools=[change_hyperparameters, change_workspace_prompt],
        generate_content_config=types.GenerateContentConfig(
            response_mime_type="application/json"
        )
    )

# mechanic agent should have a singluar session_id (remember all the previous changes)
async def create_session(session_service, user_id: str, session_id: str):
    return await session_service.create_session(
                                    app_name=MECHANIC_APP_NAME, 
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

    <STATE>
        {{"temperature":{system_state.get_temperature()}, "top-p":{system_state.get_top_p()}, "top-k":{system_state.get_top_k()}, "workspace_prompt":{system_state.get_system_prompt()}}}
    </STATE>
    """
    start_time = time.perf_counter()

    # Agent Definition (Intiailizing this everytime so not biasing the test results)
    ## TODO: Want memory to persist so that agent has context on what it changed last. Should this stuff happen everytime?
    root_agent = get_root_agent()
    session_service_vertexai_search = InMemorySessionService()
    runner_vertexai_search = Runner(
            agent=root_agent, app_name=MECHANIC_APP_NAME, session_service=session_service_vertexai_search
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

    try:
        start_time = time.perf_counter()
        for event in runner_vertexai_search.run(
            user_id=user_id, session_id=session_id, new_message=content
        ):
            # results embedded in model's response
            if event.is_final_response() and event.content:
                print(event.content.parts[0].text.strip())

        end_time = time.perf_counter()
        print(f"Agent RunTime: <{end_time - start_time}> secs.")
    except Exception as error:
        print(f"An error occured during agent invokation or execution.\nError: <{error}>")