STREAMLIT_ARTIFACT_REG_REPO=flower-classification-app
PROJECT_ID=<YOUR PROJECT ID>
REGION=us-central1
CONTAINER_PATH=us-central1-docker.pkg.dev/$PROJECT/$STREAMLIT_ARTIFACT_REG_REPO/app
APP_NAME=flower-classification

echo "Copying the model file..."
mkdir export
gsutil cp -r gs://asl-public/models/flowers_model export/

echo "Building the application image..."
if ! gcloud artifacts repositories describe $STREAMLIT_ARTIFACT_REG_REPO \
       --location=$REGION > /dev/null 2>&1; then
    gcloud artifacts repositories create $STREAMLIT_ARTIFACT_REG_REPO \
        --project=$PROJECT --location=$REGION --repository-format=docker
fi

echo $_CONTAINER_PATH
gcloud builds submit --config cloudbuild.yaml --region $REGION . --substitutions _CONTAINER_PATH=$CONTAINER_PATH

echo 'Deploying the application to Cloud Run...'
gcloud run deploy $APP_NAME \
  --image $CONTAINER_PATH:latest --min-instances 1 --max-instances 1 --cpu 1 \
  --memory 4Gi --region us-central1 > /dev/null 2>&1 && \
echo 'Deployment Done.'

echo "Follow these steps to open the app from Cloud Shell.
1. Open Cloud Shell from the Google Cloud Console.
2. Run 'gcloud run services proxy $APP_NAME --project $PROJECT --region $REGION'.
2. In Cloud Shell, click the 'Web Preview' button on the toolbar.
3. Select 'Preview on port 8080'
4. A new browser tab or window will open, displaying your Streamlit app.
"
