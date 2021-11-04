TF_VERSION=2-6
LOCATION=us-central1
MASTER_TYPE=n1-standard-4
INPUT_NOTEBOOK_FILE=gs://dsparing-sandbox/Untitled.ipynb
#CONTAINER_IMAGE_URI=gcr.io/deeplearning-platform-release/tf2-cpu.$TF_VERSION
CONTAINER_IMAGE_URI=gcr.io/deeplearning-platform-release/base-cpu
OUTPUT_NOTEBOOK_FOLDER=gs://dsparing-sandbox/broaf
EXECUTION_ID=execution_$(date +%Y-%m-%dT%H%M%S)

echo > request.json "{
  \"executionTemplate\": {
      \"masterType\": \"$MASTER_TYPE\",
      \"inputNotebookFile\": \"$INPUT_NOTEBOOK_FILE\",
      \"containerImageUri\": \"$CONTAINER_IMAGE_URI\",
      \"outputNotebookFolder\": \"$OUTPUT_NOTEBOOK_FOLDER\",
  },
}"

PROJECT_ID=$(gcloud config get-value project)
PROJECT_NUMBER=$(gcloud projects list --filter="name=$PROJECT_ID" --format="value(PROJECT_NUMBER)")
LOCATION=$LOCATION
PARENT=projects/$PROJECT_NUMBER/locations/$LOCATION

echo $PARENT

curl -X POST \
-H "Authorization: Bearer "$(gcloud auth application-default print-access-token) \
-H "Content-Type: application/json; charset=utf-8" \
-d @request.json \
"https://notebooks.googleapis.com/v1/$PARENT/executions?executionId=$EXECUTION_ID"
