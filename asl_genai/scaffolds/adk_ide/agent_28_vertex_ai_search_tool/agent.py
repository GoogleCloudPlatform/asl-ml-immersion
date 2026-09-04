# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""
Agent for weather information.
"""

from dotenv import load_dotenv
from google.adk.agents import Agent
from google.adk.tools import VertexAiSearchTool
import os
MODEL = "gemini-2.5-flash"

load_dotenv()

DATASTORE_ID="TODO: PUT_YOUR_DATASTORE_ID_HERE"

DATASTORE_RESOURCE_ID = f"projects/{os.getenv('GOOGLE_CLOUD_PROJECT')}/locations/global/collections/default_collection/dataStores/{DATASTORE_ID}"

instruction_prompt_v1 = f"""
    You are a helpful assistant that answers questions based on information
    found in the document store: {DATASTORE_RESOURCE_ID}.
    Your role is to provide accurate and concise answers to questions based
    on documents that are retrievable using ask_vertex_retrieval.

    Do not answer questions that are not related to the corpus.
    When crafting your answer, you may use the retrieval tool to fetch details
    from the corpus. Make sure to cite the source of the information.

    Citation Format Instructions:

    When you provide an answer, you must also add one or more citations **at the end** of
    your answer. If your answer is derived from only one retrieved chunk,
    include exactly one citation. If your answer uses multiple chunks
    from different files, provide multiple citations. If two or more
    chunks came from the same file, cite that file only once.

    **How to cite:**
    - Use the retrieved chunk's `title` to reconstruct the reference.
    - Include the document title and section if available.
    - For web resources, include the full URL when available.

    Format the citations at the end of your answer under a heading like
    "Citations" or "References." For example:
    "Citations:
    1) RAG Guide: Implementation Best Practices
    2) Advanced Retrieval Techniques: Vector Search Methods"

    If you are not certain or the
    information is not available, clearly state that you do not have
    enough information.
    """

ask_vertex_retrieval = VertexAiSearchTool(data_store_id=DATASTORE_RESOURCE_ID)

root_agent = Agent(
    name="search_agent_vertex_ai_tool_v3",
    model=MODEL,  # Can be a string for Gemini or a LiteLlm object
    description="Provides information about weather for specific cities.",
    instruction=instruction_prompt_v1,
    tools=[ask_vertex_retrieval],
)
