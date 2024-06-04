PROJECT="<YOUR_PROJECT>"
LOCATION="us-central1"
BUCKET="<YOUR_BUCKET>"

# Compute various paths from the ROOT_DIR
ROOT_DIR="$(dirname $(cd $(dirname $BASH_SOURCE) && pwd))"
SCRIPTS_DIR="$ROOT_DIR/scripts"
APP_YAML="$ROOT_DIR/app.yaml"
VENV="$ROOT_DIR/venv"
