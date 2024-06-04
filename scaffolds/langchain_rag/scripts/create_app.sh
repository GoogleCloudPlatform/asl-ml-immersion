#!/bin/bash

. $(cd $(dirname $BASH_SOURCE) && pwd)/config.sh

gcloud app describe --project=$PROJECT 2> /dev/null || {
  echo "No App on AppEngine existing. Creating one."
  gcloud app create --region=$LOCATION --project=$PROJECT
}
