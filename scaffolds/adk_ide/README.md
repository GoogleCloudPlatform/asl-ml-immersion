# Option1: Cloud Workstation Setup

First, open [CloudShell](https://cloud.google.com/shell) and run the following instructions:
(If cloud workstation is already created, you can skip this step.)

```bash
git clone https://github.com/GoogleCloudPlatform/asl-ml-immersion.git
cd asl-ml-immersion
(use git checkout <branch_name> if you need to switch to a specific Git brunch)
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
✅ ADK IDE configured successfully.
```

To test ADK in Debug mode choose "Python Debugger: ADK Web"


# Option2: Local Development Environment Setup
WIP
TODO: add installation process for VSCode local setup

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
