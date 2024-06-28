#!/bin/bash

. $(cd $(dirname $BASH_SOURCE) && pwd)/config.sh


export BUCKET=$BUCKET
export LOCATION=$LOCATION
export PROJECT=$PROJECT


. $VENV/bin/activate &&
python $SCRIPTS_DIR/generate_embeddings.py
