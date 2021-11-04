TF_VERSION=2-6
LOCATION=us-central1
MASTER_TYPE=n1-standard-4
TIMESTAMP=$(date +%Y-%m-%dT%H%M%S)
STAGING_BUCKET_NAME=asl_cloudbuild_$TIMESTAMP
CONTAINER_IMAGE_URI=gcr.io/deeplearning-platform-release/tf2-cpu.$TF_VERSION
EXECUTION_ID=execution_$TIMESTAMP
GIT_ORG=https://github.com/GoogleCloudPlatform
GIT_REPO_NAME=asl-ml-immersion
NOTEBOOK_TEST_ALLOWLIST="$GIT_REPO_NAME/notebooks/introduction_to_tensorflow/solutions/1_core_tensorflow.ipynb
$GIT_REPO_NAME/notebooks/introduction_to_tensorflow/solutions/4_keras_functional_api.ipynb
"

git clone $GIT_ORG/$GIT_REPO_NAME

gsutil mb -l $LOCATION gs://$STAGING_BUCKET_NAME

for NOTEBOOK in $NOTEBOOK_TEST_ALLOWLIST ; do

    INPUT_NOTEBOOK_FILE=gs://$STAGING_BUCKET_NAME/$NOTEBOOK
    OUTPUT_NOTEBOOK_FOLDER=gs://$STAGING_BUCKET_NAME/$NOTEBOOK/output
    
    gsutil cp $NOTEBOOK $INPUT_NOTEBOOK_FILE

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

done
