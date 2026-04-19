# Option1: Cloud Workstation Setup but using cloud_workstation_setup.sh

First, open [CloudShell](https://cloud.google.com/shell) and run the following instructions:
(If cloud workstation is already created, you can skip this step.)

```bash
git clone https://github.com/GoogleCloudPlatform/asl-ml-immersion.git
cd asl-ml-immersion
git checkout dev-adk-ide
export PATH=$PATH:~/.local/bin
./scripts/cloud_workstation_setup.sh
```
This will create a Cloud Workstation with the required permissions.
**This step will take a 20-30 minutes to complete.**
If your cloud shell times out, relogine and try running the script again,
it will continue from the point where it was interrupted.
After the setup is complete, you can open the Cloud Workstation 
in your browser using the following link: https://console.cloud.google.com/workstations

Click on the "Start" button to start the Cloud Workstation.
After the Cloud Workstation is started (you should see "Running" status), 
you can open it in your browser by clicking on the "Lunch" button.

In the Cloud Workstation, click "Clone Repository" button 
and add the repository URL:
https://github.com/GoogleCloudPlatform/asl-ml-immersion.git
Add destination folder, for example: /home/user/

After the repository is cloned, you can open it using "Open" button in IDE and explore the content.
Open IDE terminal window and move to /scaffolds/adk_ide folder and run **setup_adk_ide.sh** script :
```
cd scaffolds/adk_ide
sh setup_adk_ide.sh
```

You Should see installation messages similar to the following:
```
....
⚙️  Configuring IDE extensions...
✅ Found IDE binary at: /usr/local/bin/code-oss-cloud-workstations
✅ Configured IDE extensions.

To test ADK in Debug mode choose "Python Debugger: ADK Web"

# Option2: Cloud Workstation manual setup using Google Cloud Console

Here is the step-by-step guide to reproducing the exact setup 
from your bash script manually using the Google Cloud Console (the web user interface).

Before you begin, ensure you have selected your target project 
from the Project drop-down menu at the top-left of the Google Cloud Console.

Step 1: Enable the Cloud Workstations API
In the top search bar of the Google Cloud Console, type Cloud Workstations API.
Select the API from the search results.
Click the blue Enable button. (If you see "Manage" instead of "Enable", the API is already enabled).

Step 2: Identify the Default Compute Service Account
Note: You don't usually need to memorize this for the UI, 
as it appears in a drop-down later, but here is how to find it to verify.

Open the Navigation Menu (hamburger icon) and go to IAM & Admin > Service Accounts.
Look for the service account named Compute Engine default service account. 
It will have an email format like <PROJECT_NUMBER>-compute@developer.gserviceaccount.com.

Step 3: Create the Workstation Cluster
Open the Navigation Menu and go to Cloud Workstations > Cluster management.

Click + Create Cluster at the top.

Name: Enter asl-lab-cluster.

Region: Select us-central1.

Network settings:

Network: Select default.

Subnetwork: Select default.

(Note: Ensure Private Google Access is enabled on this subnet, just as your script requires).

Click Create.

Important: Creating the cluster provisions the underlying infrastructure (like an internal VPC). 
Just like the script warns, this takes approximately 20 minutes. 
You must wait for its status to turn green (Ready) before moving to the next step.

Step 4: Create the Workstation Configuration
In the Cloud Workstations menu, go to Workstation configurations 
(or stay in Cluster management and click into your newly created cluster).

Click + Create Configuration.

Basic Information:

Name: Enter asl-lab-code-oss-config.

Cluster: Select asl-lab-cluster.

Machine Configuration:

Machine type: Select e2-standard-4 (under the General Purpose tab).

Environment:

Select Code OSS from the base images 
(this maps directly to the predefined image URI used in your script: us-central1-docker.pkg.dev/cloud-workstations-images/predefined/code-oss:latest).

Advanced Settings (IAM & Scopes):

Expand the advanced settings or look for the Service Account section.

Service account: Select the Compute Engine default service account from Step 2.

Access scopes: Select Allow full access to all Cloud APIs. 
(This precisely matches the [https://www.googleapis.com/auth/cloud-platform](https://www.googleapis.com/auth/cloud-platform) scope from your script).

Click Create.

Step 5: Create the Workstation Instance
In the Cloud Workstations menu, go to Workstations.

Click + Create Workstation.

Name: Enter asl-lab-workstation.

Configuration: Select the asl-lab-code-oss-config you just made.

Click Create.

Step 6: Start and Connect to the Workstation
In the Workstations list, you will see asl-lab-workstation with a "Stopped" status.

Click the Start button next to it. It will take a minute or two to spin up.

Once the status says "Running," a Launch button will appear.

Click Launch to open the Code OSS IDE directly in a new browser tab.

(Note: The gcloud workstations start-tcp-tunnel commands printed at the end of your script are strictly command-line functions for connecting a local IDE like VS Code or terminal via SSH. If you want to connect a local IDE instead of using the browser tab, you will still need to run those specific gcloud commands in your local terminal).


# Option3: Local Development Environment Setup (VS Code or Antigravity)
This option can be used to setup development environment on your local machine (MacOS, Linux) 
with your local IDE (VS Code or Antigravity) and doesnt required Cloud Workstation.
First you need to clone repository to your local env and switch to dev-adk-ide brunch:

```bash
git clone https://github.com/GoogleCloudPlatform/asl-ml-immersion.git
cd asl-ml-immersion
git checkout dev-adk-ide
```
After the repository is cloned, move to /scaffolds/adk_ide folder and run **setup_adk_ide.sh** script:
```
cd scaffolds/adk_ide
sh setup_adk_ide.sh
```

You Should see installation messages similar to the following:
```
....
⚙️  Configuring IDE extensions...
✅ Found IDE binary at: /usr/local/bin/code-oss-cloud-workstations
✅ Configured IDE extensions.
```



# Testing API Server with curl

## Create a session

```bash
SESSION_ID=$(curl -X POST http://localhost:8502/apps/agent_01_tool_func/users/u_123/sessions/s_123 \
  -H "Content-Type: application/json" \
  -d '{"key1": "value1", "key2": 42}' \
  | jq -r '.id')
```
## Print the session ID

```bash
echo "Session ID: $SESSION_ID"
```

# Execute a query with curl

```bash
curl -X POST http://localhost:8502/run \
-H "Content-Type: application/json" \
-d '{
"appName": "agent_01_tool_func",
"userId": "u_123",
"sessionId": "s_123",
"newMessage": {
    "role": "user",
    "parts": [{
    "text": "Hey whats the weather in new york today"
    }]
}
}'
```

For full command options and usage, refer to the [Makefile](Makefile).

# ADK Agents Overview

This section provides a quick description, main learning ADK learning objectives, and expected results for each agent folder in this directory.

### [agent_01_tool_func](file:///asl-ml-immersion/scaffolds/adk_ide/agent_01_tool_func)
- **Description**: A simple agent that uses a single tool function (e.g., weather).
- **Learning Objectives**: Understand how to define an agent and register a Python function as a tool.
- **Expected Results**: The agent correctly identifies when to use the tool and returns the tool's output to the user.

### [agent_02_multi_tools](file:///asl-ml-immersion/scaffolds/adk_ide/agent_02_multi_tools)
- **Description**: An agent equipped with multiple tools.
- **Learning Objectives**: Learn how to handle multiple tools and how the model selects the appropriate tool.
- **Expected Results**: The agent selects the correct tool based on the user query and can use multiple tools in a conversation.

### [agent_03_tool_func_long_running](file:///asl-ml-immersion/scaffolds/adk_ide/agent_03_tool_func_long_running)
- **Description**: Demonstrates handling of long-running tool executions.
- **Learning Objectives**: Learn best practices for managing timeouts and long-running processes in tools.
- **Expected Results**: The agent handles long-running tools without failing or blocking indefinitely.

### [agent_04_tool_func_parallel](file:///asl-ml-immersion/scaffolds/adk_ide/agent_04_tool_func_parallel)
- **Description**: Demonstrates parallel execution of tools.
- **Learning Objectives**: Understand how to enable and manage parallel tool calling.
- **Expected Results**: The agent can invoke multiple tools simultaneously when appropriate.

### [agent_05_sub_agent](file:///asl-ml-immersion/scaffolds/adk_ide/agent_05_sub_agent)
- **Description**: Demonstrates the use of a sub-agent.
- **Learning Objectives**: Learn how to delegate tasks from a main agent to a specialized sub-agent.
- **Expected Results**: The main agent successfully delegates tasks to the sub-agent and incorporates the results.

### [agent_06_agent_tool](file:///asl-ml-immersion/scaffolds/adk_ide/agent_06_agent_tool)
- **Description**: Demonstrates wrapping an agent as a tool for another agent.
- **Learning Objectives**: Understand the `AgentTool` concept and how to nest agents.
- **Expected Results**: The parent agent uses the child agent as a tool to solve complex tasks.

### [agent_07_callback](file:///asl-ml-immersion/scaffolds/adk_ide/agent_07_callback)
- **Description**: Demonstrates the use of callbacks in the agent lifecycle.
- **Learning Objectives**: Learn how to hook into agent events (e.g., before/after tool call, on message).
- **Expected Results**: Callbacks are triggered correctly during agent execution.

### [agent_08_artifacts](file:///asl-ml-immersion/scaffolds/adk_ide/agent_08_artifacts)
- **Description**: Demonstrates generation and handling of artifacts by the agent.
- **Learning Objectives**: Learn how to produce and manage structured output files (artifacts).
- **Expected Results**: The agent creates artifacts as requested by the user.

### [agent_09_stateful_agent](file:///asl-ml-immersion/scaffolds/adk_ide/agent_09_stateful_agent)
- **Description**: An agent that maintains state across turns.
- **Learning Objectives**: Understand state management in ADK agents.
- **Expected Results**: The agent remembers context from previous turns in the session.

### [agent_10_local_sub_agents_seq](file:///asl-ml-immersion/scaffolds/adk_ide/agent_10_local_sub_agents_seq)
- **Description**: Local execution of sub-agents in a sequential workflow.
- **Learning Objectives**: Learn to chain multiple agents sequentially.
- **Expected Results**: Task is passed from one agent to the next in sequence.

### [agent_11_local_parallel_agents](file:///asl-ml-immersion/scaffolds/adk_ide/agent_11_local_parallel_agents)
- **Description**: Local execution of sub-agents in parallel.
- **Learning Objectives**: Learn to run multiple agents concurrently and aggregate results.
- **Expected Results**: Multiple agents work on tasks simultaneously, and results are synthesized.

### [agent_12_local_custom_agents](file:///asl-ml-immersion/scaffolds/adk_ide/agent_12_local_custom_agents)
- **Description**: Implementation of custom agent logic locally.
- **Learning Objectives**: Learn how to extend base agent classes for custom behavior.
- **Expected Results**: Custom agent behavior is executed as defined.

### [agent_13_workshop_prep_flow](file:///asl-ml-immersion/scaffolds/adk_ide/agent_13_workshop_prep_flow)
- **Description**: A complex workflow for preparing workshop materials.
- **Learning Objectives**: Apply multiple agent concepts to a real-world complex workflow.
- **Expected Results**: The system generates workshop plans, content, and reviews.

### [agent_14_human_tool_confirmation](file:///asl-ml-immersion/scaffolds/adk_ide/agent_14_human_tool_confirmation)
- **Description**: Demonstrates human-in-the-loop confirmation for tool execution.
- **Learning Objectives**: Learn how to pause execution and request user approval for sensitive tools.
- **Expected Results**: The agent asks for confirmation before executing specific tools.

### [agent_15_big_query_tool](file:///asl-ml-immersion/scaffolds/adk_ide/agent_15_big_query_tool)
- **Description**: An agent that uses BigQuery as a tool to query data.
- **Learning Objectives**: Learn to integrate BigQuery with ADK agents.
- **Expected Results**: Agent successfully queries BigQuery and returns results.

### [agent_16_geocoding](file:///asl-ml-immersion/scaffolds/adk_ide/agent_16_geocoding)
- **Description**: Demonstrates geocoding capabilities in a tool.
- **Learning Objectives**: Learn to use geocoding APIs within agent tools.
- **Expected Results**: Agent can convert addresses to coordinates and vice versa.

### [agent_16_openapi](file:///asl-ml-immersion/scaffolds/adk_ide/agent_16_openapi)
- **Description**: Demonstrates generating tools from an OpenAPI specification.
- **Learning Objectives**: Learn how to automatically create tools from API definitions.
- **Expected Results**: Agent uses tools generated from the OpenAPI spec to interact with the API.

### [agent_17_1_code_exec_builtin](file:///asl-ml-immersion/scaffolds/adk_ide/agent_17_1_code_exec_builtin)
- **Description**: Demonstrates built-in code execution capabilities.
- **Learning Objectives**: Learn how to use safe, built-in code execution environments.
- **Expected Results**: Agent can write and execute code within the safe environment.

### [agent_17_2_code_exec_unsafe](file:///asl-ml-immersion/scaffolds/adk_ide/agent_17_2_code_exec_unsafe)
- **Description**: Demonstrates local (unsafe) code execution.
- **Learning Objectives**: Understand the risks and implementation of local code execution.
- **Expected Results**: Agent can execute code on the local system (use with caution).

### [agent_17_3_code_exec_vertex](file:///asl-ml-immersion/scaffolds/adk_ide/agent_17_3_code_exec_vertex)
- **Description**: Demonstrates code execution using Vertex AI.
- **Learning Objectives**: Learn to use Vertex AI's managed code execution environment.
- **Expected Results**: Agent executes code in the Vertex AI environment.

### [agent_18_explainable_ai](file:///asl-ml-immersion/scaffolds/adk_ide/agent_18_explainable_ai)
- **Description**: Focuses on explainability of agent decisions or data.
- **Learning Objectives**: Learn how to make agent reasoning or data insights transparent.
- **Expected Results**: Agent provides explanations along with its answers.

### [agent_20_remote_sub_agent_a2a](file:///asl-ml-immersion/scaffolds/adk_ide/agent_20_remote_sub_agent_a2a)
- **Description**: Demonstrates calling a remote sub-agent via A2A protocol.
- **Learning Objectives**: Learn the basics of Agent-to-Agent (A2A) communication.
- **Expected Results**: The local agent successfully communicates with and delegatess to a remote agent.

### [agent_21_remote_a2a_custom_server_adk](file:///asl-ml-immersion/scaffolds/adk_ide/agent_21_remote_a2a_custom_server_adk)
- **Description**: Implementation of a custom A2A server using ADK.
- **Learning Objectives**: Learn how to host an ADK agent as an A2A server.
- **Expected Results**: The server accepts and processes A2A requests correctly.

### [agent_22_remote_a2a_executor_impl](file:///asl-ml-immersion/scaffolds/adk_ide/agent_22_remote_a2a_executor_impl)
- **Description**: Custom executor implementation for A2A.
- **Learning Objectives**: Learn how to customize the execution logic for remote agents.
- **Expected Results**: The custom executor manages agent execution as defined.

### [agent_23_remote_a2a_langgraph](file:///asl-ml-immersion/scaffolds/adk_ide/agent_23_remote_a2a_langgraph)
- **Description**: Integration of LangGraph agents with A2A.
- **Learning Objectives**: Learn how to make non-ADK agents (LangGraph) compatible with A2A.
- **Expected Results**: A LangGraph agent can participate in the A2A network.

### [agent_24_remote_sub_agents](file:///asl-ml-immersion/scaffolds/adk_ide/agent_24_remote_sub_agents)
- **Description**: Managing multiple remote sub-agents.
- **Learning Objectives**: Scale A2A patterns to handle multiple remote agents.
- **Expected Results**: Coordination across multiple remote agents works seamlessly.

### [agent_26_mcp_tool_agent](file:///asl-ml-immersion/scaffolds/adk_ide/agent_26_mcp_tool_agent)
- **Description**: Demonstrates usage of Model Context Protocol (MCP) tools.
- **Learning Objectives**: Understand how to integrate MCP servers and tools with ADK.
- **Expected Results**: Agent can use tools provided by an MCP server.

### [agent_27_mcp_bigquery](file:///asl-ml-immersion/scaffolds/adk_ide/agent_27_mcp_bigquery)
- **Description**: Using MCP to interact with BigQuery.
- **Learning Objectives**: Learn to use MCP patterns for data access.
- **Expected Results**: Agent accesses BigQuery data via MCP.

### [agent_28_vertex_ai_search_tool](file:///asl-ml-immersion/scaffolds/adk_ide/agent_28_vertex_ai_search_tool)
- **Description**: Integrates Vertex AI Search as a tool.
- **Learning Objectives**: Learn to use Vertex AI Search for RAG or information retrieval.
- **Expected Results**: Agent retrieves relevant information from Vertex AI Search.

### [agent_29_search_tool](file:///asl-ml-immersion/scaffolds/adk_ide/agent_29_search_tool)
- **Description**: Demonstrates usage of a generic search tool.
- **Learning Objectives**: Learn to integrate standard search APIs.
- **Expected Results**: Agent can perform web or file searches.

### [agent_30_deploy_agent_engine](file:///asl-ml-immersion/scaffolds/adk_ide/agent_30_deploy_agent_engine)
- **Description**: Deployment of an agent to Vertex AI Agent Engine.
- **Learning Objectives**: Learn the deployment flow for Agent Engine.
- **Expected Results**: Agent is deployed and accessible in Agent Engine.

### [agent_31_deploy_cloud_run](file:///asl-ml-immersion/scaffolds/adk_ide/agent_31_deploy_cloud_run)
- **Description**: Deployment of an agent to Google Cloud Run.
- **Learning Objectives**: Learn how to containerize and deploy an agent to Cloud Run.
- **Expected Results**: Agent is accessible as a Cloud Run service.

### [agent_32_pdf](file:///asl-ml-immersion/scaffolds/adk_ide/agent_32_pdf)
- **Description**: Demonstrates handling and processing of PDF files.
- **Learning Objectives**: Learn how to extract information from PDFs using tools or model capabilities.
- **Expected Results**: Agent can answer questions about content in uploaded PDFs.

### [agent_33_gemini_config](file:///asl-ml-immersion/scaffolds/adk_ide/agent_33_gemini_config)
- **Description**: Demonstrates advanced configuration of Gemini models.
- **Learning Objectives**: Learn how to adjust safety settings, system instructions, and other parameters.
- **Expected Results**: Agent behaves according to the specific configuration applied.

