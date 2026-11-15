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
from .tools import explain_fraud_transaction
from google.adk.agents import Agent
import os

MODEL = "gemini-2.5-flash"

from google.adk.agents.llm_agent import LlmAgent
from google.adk.tools.api_registry import ApiRegistry
from datetime import datetime

PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT")

from typing import Dict
from pydantic import BaseModel, Field
from google.adk.agents import LlmAgent
from google.adk.tools import AgentTool

# ---------------------------------------------------------
# Define the Input Schema (The Request)
# ---------------------------------------------------------
class TransactionRequest(BaseModel):
    transaction_id: str = Field(
        ..., 
        description="The unique ID of the transaction to fetch features for."
    )
# ---------------------------------------------------------
# Define the Output Schema (The Response)
# ---------------------------------------------------------
# We define the inner dictionary first for clarity, then the main response.

class TransactionFeatures(BaseModel):
    tx_amount: float
    #Customer History Features
    customer_id_avg_amount_14day_window: float
    customer_id_avg_amount_15min_window: float
    customer_id_avg_amount_1day_window: float
    customer_id_avg_amount_30min_window: float
    customer_id_avg_amount_60min_window: float
    customer_id_avg_amount_7day_window: float
    customer_id_nb_tx_14day_window: float
    customer_id_nb_tx_15min_window: float
    customer_id_nb_tx_1day_window: float
    customer_id_nb_tx_30min_window: float
    customer_id_nb_tx_60min_window: float
    customer_id_nb_tx_7day_window: float
    
    # Terminal Features
    terminal_id_avg_amount_15min_window: float
    terminal_id_avg_amount_30min_window: float
    terminal_id_avg_amount_60min_window: float
    terminal_id_nb_tx_14day_window: float
    terminal_id_nb_tx_15min_window: float
    terminal_id_nb_tx_1day_window: float
    terminal_id_nb_tx_30min_window: float
    terminal_id_nb_tx_60min_window: float
    terminal_id_nb_tx_7day_window: float
    terminal_id_risk_14day_window: float
    terminal_id_risk_1day_window: float
    terminal_id_risk_7day_window: float
    

class FeatureResponse(BaseModel):
    transaction_features: TransactionFeatures = Field(
        ...,
        description="A dictionary containing calculated transaction features."
    )

from google.adk.agents import Agent
from toolbox_core import ToolboxSyncClient

toolbox = ToolboxSyncClient("http://127.0.0.1:5000")

# Load all the tools
tools = toolbox.load_toolset("fraudfinder_toolset")

bq_mcp_agent = Agent(
    name="transaction_info_agent",
    model="gemini-2.5-flash",
    description=("Agent to retrieve stored transaction feature."),
    instruction=(
        """
        You are a helpful agent who can answer user questions about
        about user transactions.
        Use the tools to answer the question
        """
    ),
    tools=tools,
    input_schema=TransactionRequest,
    output_schema=TransactionFeatures,
)

explanation_agent = Agent(
    model=MODEL,
    name="transaction_explanation_agent",
    description=(
        """Agent to retrieve transaction explanations"""
    ),
    instruction="Use explain_fraud_transaction tool to retrieves feature explanations",
    tools=[explain_fraud_transaction],
    input_schema=TransactionFeatures
)

root_agent = Agent(
    model=MODEL,
    name="fraud_analyst_agent",
    description=(
        """Agent to retrieve stored transaction features for a given transaction"""
    ),
    instruction="""
        You are an expert Data Scientist/Analyst in a bank's Fraud Analytics Department.
        Your primary goal is to analyze specific transactions to understand model behavior, 
        specifically focusing on identifying the root causes of false positive fraud alerts.

        You must follow this strict workflow:
        1. Data Retrieval: Use the 'transaction_info_tool' to fetch full details
        for the target transaction.
        2. Model Interpretation: Pass the transaction details to the 'explanation_agent' 
        to retrieve the feature importance and prediction rationale.
        3. Analysis: Synthesize the transaction data with the model explanation. 
        Look for discrepancies where legitimate behavior was incorrectly flagged as suspicious.
        4. Conclusion: Generate a final report summarizing the fraud status. 
        You must state whether the case is a False Positive or True Fraud and provide the evidence.
    """,
    tools=[AgentTool(agent=bq_mcp_agent), AgentTool(agent=explanation_agent)],
)