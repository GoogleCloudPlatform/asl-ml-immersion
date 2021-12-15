#!/bin/bash

. $(cd $(dirname $BASH_SOURCE) && pwd)/env.sh


CLOUD_BUILD_SERVICE_ACCOUNT="$PROJECT_NUMBER@cloudbuild.gserviceaccount.com"

gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member serviceAccount:$CLOUD_BUILD_SERVICE_ACCOUNT \
  --role roles/editor
