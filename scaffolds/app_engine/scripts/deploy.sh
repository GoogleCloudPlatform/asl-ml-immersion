#!/bin/bash

. $(cd $(dirname $BASH_SOURCE) && pwd)/config.sh

gcloud app deploy $APP_YAML --project=$PROJECT
gcloud app browse --project=$PROJECT
