#!/bin/bash

. $(cd $(dirname $BASH_SOURCE) && pwd)/config.sh

gsutil cp $DATA_CSV gs://$BUCKET 
