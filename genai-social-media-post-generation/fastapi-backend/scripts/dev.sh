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

cd $(dirname $0)/..

# Load all necessary variables
. ./scripts/init.sh
gcloud config set project $PROJECT_ID
gcloud auth application-default set-quota-project $PROJECT_ID

uvicorn main:app --reload --port 3001
# uvicorn main:app --port 3001 --workers 2