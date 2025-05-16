

PROJECT_DIR=$(cd . && pwd)
ARTIFACT_REGISTRY_DIR=asl-artifact-repo
IMAGE_NAME=taxifare_training_container
DOCKERFILE=$PROJECT_DIR/Dockerfile
IMAGE_URI=us-docker.pkg.dev/$PROJECT/$ARTIFACT_REGISTRY_DIR/$IMAGE_NAME:latest

# Authorize Artifact Registry
gcloud auth print-access-token | docker login -u oauth2accesstoken --password-stdin https://us-docker.pkg.dev

docker build $PROJECT_DIR -f $DOCKERFILE -t $IMAGE_URI

docker push $IMAGE_URI