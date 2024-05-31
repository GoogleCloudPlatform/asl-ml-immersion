#!/bin/bash

. $(cd $(dirname $BASH_SOURCE) && pwd)/config.sh

echo gcloud services --project=$PROJECT enable \
  aiplatform.googleapis.com \
  bigquery.googleapis.com \
  dataflow.googleapis.com

# App Engine
echo gcloud projects add-iam-policy-binding $PROJECT \
    --member="serviceAccount:$PROJECT.google.com@appspot.gserviceaccount.com" \
    --role="roles/aiplatform.admin" \
    --role="roles/storage.admin" \
    --role="roles/storage.objectViewer"

# Compute Engine
echo gcloud projects add-iam-policy-binding $PROJECT \
    --member="serviceAccount:191470275149-compute@developer.gserviceaccount.com" \
    --role="roles/source.admin" \
    --role="roles/aiplatform.admin" \
    --role="roles/storage.admin"
