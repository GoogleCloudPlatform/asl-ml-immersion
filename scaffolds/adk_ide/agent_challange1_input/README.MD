# Functional Application Specification: Weather Disaster-Response Orchestrator ("God Agent")

This document details the functional and operational requirements for the **Weather Disaster-Response Orchestrator** (internally designated as `weather_agent`). The system acts as an automated triage, verification, and alert-dispatch mechanism during severe weather events.

⚠️ **Architectural Disclaimer**: The provided implementation represents a classic monolithic **"God Agent" anti-pattern**. All business logic, routing, approval gating, and error handling are handled via unstructured natural language instructions within a single agent prompt, rather than decoupled state machines or micro-agents.

---

## ⚙️ 1. System Architecture & Components

The application is built using the `google.adk.agents` framework, running on a highly capable Large Language Model (LLM) to parse intent, evaluate variables, and trigger external APIs.

### Agent Configuration

| Parameter | Configuration Value | Operational Purpose |
| :--- | :--- | :--- |
| **Agent Name** | `weather_agent` | Unique identifier for routing and orchestration. |
| **Underlying Model** | `gemini-2.5-flash` | Selected LLM for natural language processing and tool calling. |
| **Primary Role** | Disaster-Response Coordinator | Multi-functional orchestrator of weather alerts and error logging. |

### Tool Registry & Integration Specifications

| Tool Name | Python Signature | Inputs | Outputs | Description |
| :--- | :--- | :--- | :--- | :--- |
| `get_weather` | `get_weather(city: str) -> dict` | `city` *(string)* | `dict` containing `city`, `wind_speed`, `status` | Fetches current weather status and wind metrics. Simulates high-risk wind speed (65mph) and "Severe Storm" status if input is "Miami". |
| `send_alert_email` | `send_alert_email(recipient: str, subject: str, body: str) -> str` | `recipient` *(string)*, `subject` *(string)*, `body` *(string)* | `"SUCCESS"` or error indicator | Dispatches a high-priority weather alert to subscribers. Prints dispatch logs to output stream. |
| `log_incident_in_crm` | `log_incident_in_crm(system: str, details: str) -> str` | `system` *(string)*, `details` *(string)* | `"INCIDENT_LOGGED"` | Registers runtime errors, tool failures, or exceptions in the CRM database. |

---

## 🔄 2. Functional Orchestration & Workflow

The agent uses semantic classification to handle incoming requests and executes a 7-step sequential workflow.

### Workflow Phase Matrix

| Phase | Stage Name | Technical Action | Expected Outcome |
| :--- | :--- | :--- | :--- |
| **1** | **Classify** | Evaluates if the incoming prompt is a weather query or a system-related error. | Routes to Phase 2 (for weather) or Phase 7 (for errors). |
| **2** | **Retrieve** | Invokes `get_weather` with the requested location. | Returns JSON weather payload. |
| **3** | **Evaluate Risk** | Analyzes payload. **HIGH RISK** if `wind_speed` > 50mph or `status` == "Severe Storm". Otherwise, **LOW RISK**. | Determines the logical gate for dispatch approval. |
| **4** | **Ask Approval** | If **HIGH RISK**, prompts user: *"Should I send the email alert?"* and halts. | Pauses workflow; awaits explicit affirmative input. |
| **5** | **Act** | If **LOW RISK**, triggers `send_alert_email` immediately. If **HIGH RISK**, triggers it *only* after approval. | Dispatches alert; prints execution status. |

### Decision Framework: Risk Evaluation

| Metric / Criteria | Threshold / Condition | Resulting State | System Action Required |
| :--- | :--- | :--- | :--- |
| **Wind Speed** | `> 50 mph` | 🔴 **HIGH RISK** | Halt execution. Request explicit user approval. |
| **Status Field** | `"Severe Storm"` | 🔴 **HIGH RISK** | Halt execution. Request explicit user approval. |
| **All Other States** | Wind `≤ 50 mph` & status `"Sunny"` / normal | 🟢 **LOW RISK** | Automatic dispatch. Trigger `send_alert_email` immediately. |

---

## 🛠️ 3. Error Handling & Resiliency Policies

The application embeds retry behaviors and database logging policies directly within the agent's instructions to safeguard execution reliability.

### Fault Tolerance & Retry Matrix

| Trigger / Event | Target Component | Policy Action | Operational Constraint |
| :--- | :--- | :--- | :--- |
| **Failure of `get_weather`** | Weather API Tool | **Automatic Retry** | Retry up to exactly **2 times** before escalating. |
| **Failure of `send_alert_email`** | Email Dispatch Tool | **Immediate Halt** | **Strictly 0 retries** to prevent double-billing, spam, or duplicate alerts. |
| **Unresolved Critical Failure** | Any system component | **Log Incident** | Invoke `log_incident_in_crm` with error details and system metadata. |

---

## ⚠️ 4. Architectural Critique: The "God Agent" Anti-Pattern

While this architecture is functional for simple scripts, combining routing, logic, and tool execution into a single prompt presents major production risks.

### Monolithic Risks vs. Production-Grade Alternatives

| Monolithic Risk | Technical Impact | Production-Grade Alternative |
| :--- | :--- | :--- |
| **Implicit State Management** | The model must track state transitions, retry loops, and approvals purely in prompt memory. | Use an explicit orchestration state machine (e.g., LangGraph, temporal workflows) to enforce transitions. |
| **Prompt Bloat & Hallucination** | Packing multi-step instructions into one string increases the risk that the model bypasses approvals or skips steps. | Break down tasks into single-responsibility micro-agents (e.g., `ClassifierAgent`, `TriageAgent`, `AlertAgent`). |
| **Hardcoded Retries in Prompt** | Retry counters handled by LLM tokens are unreliable. | Implement retry mechanisms at the code/SDK level (e.g., using python loop wrappers or decorators). |
| **Loose Approval Verification** | "Explicit permission" is semantic. A user typing *"No, don't wait"* might accidentally trigger the mail. | Implement hard-coded human-in-the-loop (HITL) middleware checkpoints in the execution wrapper. |
