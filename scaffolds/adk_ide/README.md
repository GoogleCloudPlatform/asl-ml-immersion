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
