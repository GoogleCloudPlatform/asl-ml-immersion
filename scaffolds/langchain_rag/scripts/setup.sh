#!/bin/bash

. $(cd $(dirname $BASH_SOURCE) && pwd)/config.sh


gcloud services --project=$PROJECT enable \
  aiplatform.googleapis.com \
  bigquery.googleapis.com \
  dataflow.googleapis.com

# App Engine
gcloud projects add-iam-policy-binding $PROJECT \
    --member="serviceAccount:$PROJECT@appspot.gserviceaccount.com" \
    --role="roles/aiplatform.admin" \
    --role="roles/storage.admin" \
    --role="roles/storage.objectViewer"

# Compute Engine
gcloud projects add-iam-policy-binding $PROJECT \
    --member="serviceAccount:$PROJECT_ID-compute@developer.gserviceaccount.com" \
    --role="roles/source.admin" \
    --role="roles/aiplatform.admin" \
    --role="roles/storage.admin"
