#!/bin/bash

export PROJECT_ID=$1
export ENDPOINT_ID=$2
export PORT=8080

test -z $PROJECT_ID && {
	echo "Usage: $0 <PROJECT_ID> <ENDPOINT_ID>"
	exit 1
}


flask --app app run -h localhost -p $PORT
