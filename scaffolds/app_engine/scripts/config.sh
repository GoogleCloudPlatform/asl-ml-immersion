PROJECT=$(gcloud config get-value project)
LOCATION=$(gcloud config get-value compute/zone)
BUCKET=$PROJECT
PROJECT_ID=$(\
gcloud projects list \
--filter=$PROJECT \
--format="value(PROJECT_NUMBER)")

# Compute various paths from the ROOT_DIR
ROOT_DIR="$(dirname $(cd $(dirname $BASH_SOURCE) && pwd))"
SCRIPTS_DIR="$ROOT_DIR/scripts"
APP_YAML="$ROOT_DIR/app.yaml"
VENV="$ROOT_DIR/venv"
DATA_CSV="$ROOT_DIR/data/data.csv"

