#!/bin/bash
# Go to root dir of the project
cd $(dirname $0)/..

# Source common variables if needed (ensure PROJECT_ID is set)
# . ./scripts/init.sh # Adapt this if it sets necessary vars like PROJECT_ID

# --- Configuration ---
# Ensure these match your environment and cloudbuild.yaml substitutions
export PROJECT_ID="${PROJECT_ID:-$(gcloud config get-value project)}" # Get project ID if not set
export AR_REGION="asia-southeast1"
export AR_REPO_NAME="pru-marketing-gen"
export APP_NAME="pru-market-gen"
export GKE_CLUSTER_NAME="pru-marketing-cluster"
export GKE_CLUSTER_ZONE="asia-southeast1-c"
export K8S_NAMESPACE="pru-market-gen-ns"
# NOTE: K8S_MANIFEST_DIR is passed to Cloud Build. Its interpretation ('../k8s')
# depends on how steps in cloudbuild.yaml use it relative to the build workspace root.
# If k8s manifests are inside the project root, consider using 'k8s' or './k8s'.
export K8S_MANIFEST_DIR="k8s"
export K8S_DEPLOYMENT_NAME="pru-market-gen-deployment"
# --- End Configuration ---

# Ensure Project ID is set
if [ -z "$PROJECT_ID" ]; then
  echo "ERROR: PROJECT_ID environment variable is not set or 'gcloud config get-value project' failed."
  exit 1
fi

echo "INFO: Triggering Cloud Build for application ${APP_NAME}..."
echo "  Project:       ${PROJECT_ID}"
echo "  Cluster:       ${GKE_CLUSTER_NAME} (${GKE_CLUSTER_ZONE})"
echo "  Namespace:     ${K8S_NAMESPACE}"
# Consider updating this echo if the actual image pushed follows a different pattern
# e.g., echo "  Artifact Repo: ${AR_REGION}-docker.pkg.dev/${PROJECT_ID}/${AR_REPO_NAME}/..."
echo "  Artifact Repo Info (Example): ${AR_REGION}-docker.pkg.dev/${PROJECT_ID}/${AR_REPO_NAME}/<image>"

# Submit build to Cloud Build, passing required variables as substitutions
# The syntax here appears correct. Ensure cloudbuild.yaml exists and uses these substitutions.
gcloud builds submit . \
  --config=cloudbuild.yaml \
  --project="${PROJECT_ID}" \
  --substitutions=\
_AR_REGION="${AR_REGION}",\
_AR_REPO_NAME="${AR_REPO_NAME}",\
_APP_NAME="${APP_NAME}",\
_GKE_CLUSTER_NAME="${GKE_CLUSTER_NAME}",\
_GKE_CLUSTER_ZONE="${GKE_CLUSTER_ZONE}",\
_K8S_NAMESPACE="${K8S_NAMESPACE}",\
_K8S_MANIFEST_DIR="${K8S_MANIFEST_DIR}",\
_K8S_DEPLOYMENT_NAME="${K8S_DEPLOYMENT_NAME}" # Last item correctly has no trailing comma

BUILD_STATUS=$?

if [ $BUILD_STATUS -ne 0 ]; then
  echo "ERROR: Cloud Build submission failed or build execution failed (Exit Code: ${BUILD_STATUS})."
  echo "Check build logs for details: https://console.cloud.google.com/cloud-build/builds?project=${PROJECT_ID}"
  exit 1
fi

echo "SUCCESS: Cloud Build triggered. Deployment handled within the build pipeline."
echo "Monitor build progress: https://console.cloud.google.com/cloud-build/builds?project=${PROJECT_ID}"

exit 0 # Explicitly exit with success
