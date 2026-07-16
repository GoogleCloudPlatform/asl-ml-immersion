# Option1: Cloud Workstation Setup but using cloud_workstation_setup.sh

First, open [CloudShell](https://cloud.google.com/shell) and run the following instructions:
(If cloud workstation is already created, you can skip this step.)

```bash
git clone https://github.com/GoogleCloudPlatform/asl-ml-immersion.git
cd asl-ml-immersion
git checkout dev-adk2-workflows
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
cd scaffolds/adk2_workflows
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
First you need to clone repository to your local env and switch to dev-adk2-workflows brunch:

```bash
git clone https://github.com/GoogleCloudPlatform/asl-ml-immersion.git
cd asl-ml-immersion
git checkout dev-adk2-workflows
```
After the repository is cloned, move to /scaffolds/adk2_workflows folder and run **setup_adk_ide.sh** script:
```
cd scaffolds/adk2_workflows
sh setup_adk_ide.sh
```

You Should see installation messages similar to the following:
```
....
⚙️  Configuring IDE extensions...
✅ Found IDE binary at: /usr/local/bin/code-oss-cloud-workstations
✅ Configured IDE extensions.
```

# ADK Agents Overview

This section provides a quick description, main learning ADK learning objectives, and expected results for each agent folder in this directory.

### [agent_01_antipattern](file:///Users/osaienko/development/asl2026/mlops/asl-ml-immersion/scaffolds/adk2_workflows/agent_01_antipattern)
- **Description**: Demonstrates the monolithic "God Agent" anti-pattern, where a single agent tries to orchestrate a complex operational workflow (classification, retrieval, evaluation, human confirmation, retry policy, and error logging) entirely through its unstructured natural language instruction and a flat list of tools.
- **Learning Objectives**: Understand why relying solely on natural language agent instructions for multi-step state transitions, error handling, retries, and human-in-the-loop triggers is fragile, hard to test, and prone to instruction-following failures or hallucinations.
- **Expected Results**: Recognize the limitations of a monolithic agent when trying to execute sequenced, conditional workflows, highlighting the need for structured graphs/workflows.

### [agent_adk2_01_graph_router](file:///Users/osaienko/development/asl2026/mlops/asl-ml-immersion/scaffolds/adk2_workflows/agent_adk2_01_graph_router)
- **Description**: A basic workflow routing system using ADK2's `Workflow` class. It classifies a message (using the `process_message` agent) and then uses a Python router function (`router`) to dynamically route to one or more execution nodes (`response_1_bug`, `response_2_support`, `response_3_logistics`) based on the returned route event keys.
- **Learning Objectives**:
  - Understand how to structure a multi-node workflow using the `Workflow` class.
  - Learn how to define edges, nodes, and routing conditions.
  - See how to use structured outputs in conjunction with programmatic routers (`Event(route=[...])`).
- **Expected Results**: The workflow starts, passes the user's message to the classification agent. Based on the classification, the router returns a route event that triggers the correct response node (e.g., if the category is "BUG", it runs `response_1_bug` and returns "Handling bug...").

### [agent_adk2_02_graph_loop](file:///Users/osaienko/development/asl2026/mlops/asl-ml-immersion/scaffolds/adk2_workflows/agent_adk2_02_graph_loop)
- **Description**: Demonstrates an evaluation loop (cycle/feedback loop) using ADK2. An agent `generate_headline` generates a headline for a given topic. An evaluator agent `evaluate_headline` scores the headline using a Pydantic schema (`Feedback`) indicating whether it's related to technology or software engineering. If not (`unrelated`), the workflow routes back to `generate_headline` with the evaluator's feedback until a satisfying headline is generated.
- **Learning Objectives**:
  - Understand how to structure iterative refinement loops in ADK2 workflows.
  - Learn to pass feedback/state back to earlier steps in a workflow (via `{feedback?}` or state mapping).
  - Use structured outputs (`BaseModel` / `Feedback`) to control execution routing.
- **Expected Results**: Given a topic (e.g. "cooking"), the generator produces a headline, the evaluator flags it as "unrelated", providing feedback to make it tech-focused. The workflow routes back to the generator, which reads the feedback and regenerates a tech-related headline. The evaluator then grades it as "tech-related", and the workflow completes successfully.

### [agent_adk2_03_graph_hitl](file:///Users/osaienko/development/asl2026/mlops/asl-ml-immersion/scaffolds/adk2_workflows/agent_adk2_03_graph_hitl)
- **Description**: Demonstrates a Human-in-the-Loop (HITL) pattern using ADK2's `RequestInput` class. The workflow drafts an email response to a customer complaint using the `draft_email` agent. It then pauses execution using `RequestInput` to solicit feedback or approval from a human reviewer. Based on the human input ("approve", "reject", or revisions/feedback), the workflow either sends the email, rejects it, or routes back to `draft_email` with the feedback to draft a revision.
- **Learning Objectives**:
  - Understand how to pause workflow execution and request external input/interaction from a human using `RequestInput`.
  - Handle human input programmatically (`handle_human_review`) to transition states or route execution (e.g., revise, approve, reject).
  - Manage state updates (`feedback`) during human-in-the-loop interactions.
- **Expected Results**: The workflow starts, drafts an email response, and stops at `request_human_review`, returning a request for input containing the draft. When the user sends "approve", the workflow proceeds to `send_email` and finishes. When the user sends feedback, it routes back to `draft_email`, regenerates the draft, and requests review again.

### [agent_adk2_04_dynamic_workflow](file:///Users/osaienko/development/asl2026/mlops/asl-ml-immersion/scaffolds/adk2_workflows/agent_adk2_04_dynamic_workflow)
- **Description**: Demonstrates dynamic workflows using programmatic orchestrator nodes in ADK2. Instead of defining static transitions (edges) upfront, a custom `@node` function orchestrates the flow dynamically in standard Python code using `ctx.run_node` inside loops, conditionals, etc.
- **Learning Objectives**:
  - Understand the difference between static workflows and dynamic workflows in ADK2.
  - Learn to use `Context` to programmatically run nodes (`await ctx.run_node`) from within another node.
  - Understand the role of `@node(rerun_on_resume=True)` when implementing stateful loops.
- **Expected Results**: The workflow runs the `orchestrate` node, which sequentially triggers `generate_headline` and `evaluate_headline` inside a Python `while` loop until a "tech-related" grade is returned. The workflow is highly dynamic and flexible, using standard Python control structures rather than static configuration.

### [agent_adk2_05_task_mode](file:///Users/osaienko/development/asl2026/mlops/asl-ml-immersion/scaffolds/adk2_workflows/agent_adk2_05_task_mode)
- **Description**: Demonstrates how to use different execution modes (`mode="single_turn"` vs. `mode="task"`) in ADK2 sub-agents, coordinated by a root/coordinator agent. The root coordinator `travel_planner` delegates to `weather_checker` (running in `single_turn` mode, which runs as a fire-and-forget autonomous task) and `flight_booker` (running in `task` mode, which runs interactively and can ask the user clarifying questions or interact).
- **Learning Objectives**:
  - Understand different agent execution modes: `single_turn` (default, autonomous execution without user interaction) and `task` (interactive session where the agent can interact back-and-forth with the user to accomplish a goal).
  - Understand how a coordinator agent can delegate sub-tasks using auto-generated tools (e.g., `request_task_<sub_agent_name>`).
  - Learn to specify `input_schema` and `output_schema` on sub-agents to enforce structured context passing and tool definitions.
- **Expected Results**: The root agent coordinates the travel plan. It first invokes the `weather_checker` sub-agent autonomously. Then, it invokes `flight_booker` in `task` mode. The `flight_booker` can prompt the user for input/confirmation before executing the final `book_flight` action, and returns a structured `FlightResult`.

