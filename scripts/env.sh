REPO_ROOT_DIR="$(dirname $(cd $(dirname $BASH_SOURCE) && pwd))"
SCRIPTS_DIR="$REPO_ROOT_DIR/scripts"

PROJECT_ID=$(gcloud config list project --format "value(core.project)")
PROJECT_NUMBER=$(gcloud projects describe $PROJECT_ID --format="value(projectNumber)")
