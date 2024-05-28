#!/bin/bash

. $(cd $(dirname $BASH_SOURCE) && pwd)/config.sh


export BUCKET=$BUCKET
export LOCATION=$LOCATION
export PROJECT=$PROJECT

gcloud config set project $PROJECT
. $VENV/bin/activate && pytest "$ROOT_DIR/tests"
