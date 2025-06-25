#!/bin/bash

# Copyright 2024 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Go to root dir
cd $(dirname $0)/..

# Variables
export PROJECT_ID=pso-hackathon-demo
export CLOUDRUN_SERVICE_NAME=content-generator-frontend
export CLOUDRUN_SERVICE_IMAGE_NAME=gcr.io/$PROJECT_ID/$CLOUDRUN_SERVICE_NAME

# Setup
gcloud config set project $PROJECT_ID
gcloud auth application-default set-quota-project $PROJECT_ID

# Build image
export REPO_FULL_NAME=$CLOUDRUN_SERVICE_IMAGE_NAME
gcloud builds submit \
  --config cloudbuild.yaml \
  --substitutions=REPO_FULL_NAME=$REPO_FULL_NAME .

# Deploy image
gcloud run deploy $CLOUDRUN_SERVICE_NAME \
    --image $CLOUDRUN_SERVICE_IMAGE_NAME \
    --region us-central1 \
    --port 3000 --allow-unauthenticated