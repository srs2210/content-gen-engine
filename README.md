# pru-market-gen

This project documents the migration of our application from **Cloud Run** to **Google Kubernetes Engine (GKE)**. During this transition, several key changes were made to adapt the application for the new environment:

Firstly, the **`Dockerfile`** was updated. We incorporated a **CUDA-specific base image** that includes the necessary **CUDA toolkit**. This change is crucial for the application to properly utilize the **NVIDIA drivers** present on the GKE nodes. As part of this update, we also added lines directly into the **`Dockerfile`** to install specific, compatible versions of other essential packages, such as **PyTorch**.

Consequently, these packages (which are now handled by the Dockerfile) were removed from the **`requirements.txt`** file. This was done to prevent issues where default package manager behavior might pick incompatible versions.

Secondly, to manage the GKE workload, we introduced **Kubernetes manifest files** located in the **`k8s/`** folder. These files define how the application resources are deployed on GKE.

Finally, a **`cloudbuild.yaml`** file was added. As will be detailed in later sections, this file automates the process of building the Docker image (using the updated **`Dockerfile`**) and subsequently deploying the application to GKE.

# CUDA Application Deployment to GKE via Cloud Build

This repository contains the setup for building a Dockerized CUDA application and deploying it to a Google Kubernetes Engine (GKE) cluster using Google Cloud Build for CI/CD.

## Overview

The process automates the following:
1.  Building a Docker image from the provided `Dockerfile`.
2.  Pushing the image to Google Artifact Registry.
3.  Updating Kubernetes deployment manifests with the new image URI.
4.  Applying the manifests to a GKE cluster to deploy or update the application.
5.  Verifying the deployment rollout.

This is achieved using a combination of a shell script (`scripts/deploy.sh`) to trigger the pipeline and a `cloudbuild.yaml` file to define the build and deployment steps.

## Prerequisites

Before you begin, ensure you have the following:

1.  **Google Cloud SDK (`gcloud`):** Installed and authenticated. Configure your default project (`gcloud config set project YOUR_PROJECT_ID`).
2.  **Docker:** Installed locally (primarily for understanding image building, though Cloud Build handles it in the cloud).
3.  **`kubectl`:** Installed (for interacting with your GKE cluster post-deployment).
4.  **GCP Project:**
    * A Google Cloud Platform project with billing enabled.
    * Required APIs enabled:
        * Cloud Build API
        * Artifact Registry API
        * Kubernetes Engine API
5.  **Artifact Registry:** A Docker repository created in Artifact Registry in your desired region.
6.  **GKE Cluster:**
    * An existing GKE cluster.
    * A node pool with GPUs (e.g., NVIDIA L4, T4, A100) attached.
    * NVIDIA drivers installed on the GPU nodes (GKE typically automates this for GPU node pools).
    * Workload Identity configured if your application needs to securely access other Google Cloud services.
7.  **Kubernetes Service Account (KSA):** If using Workload Identity, a KSA (e.g., `pru-market-gen-ksa` as per your `deployment.yaml`) should exist in your target namespace and be annotated to impersonate a GCP service account.
8.  **Project Files:**
    * `Dockerfile`: Located in the project root, defining how to build your application's Docker image.
    * `cloudbuild.yaml`: Located in the project root, defining the CI/CD pipeline steps.
    * `scripts/deploy.sh`: The script to trigger the Cloud Build pipeline.
    * `k8s/`: A directory containing your Kubernetes manifest files:
        * `deployment.yaml`: Defines the application deployment. Must contain an `image:` field with a placeholder (e.g., `__IMAGE_PLACEHOLDER__`) that Cloud Build will update.
        * `service.yaml` (Recommended): Defines how to expose your application.
        * `hpa.yaml` (Optional): Defines Horizontal Pod Autoscaler settings.
        * Other manifests (e.g., `configmap.yaml`, `secret.yaml` if needed).


## Configuration

1.  **`scripts/deploy.sh`:**
    Open `scripts/deploy.sh` and configure the environment variables at the top of the file to match your GCP project, Artifact Registry, GKE cluster, and Kubernetes resource names. Key variables include:
    * `PROJECT_ID` (can be auto-detected if `gcloud` is configured)
    * `AR_REGION` (e.g., `asia-southeast1`)
    * `AR_REPO_NAME` (your Artifact Registry repository name)
    * `APP_NAME` (your application/image name)
    * `GKE_CLUSTER_NAME`
    * `GKE_CLUSTER_ZONE` (or `GKE_CLUSTER_REGION` if using a regional cluster)
    * `K8S_NAMESPACE` (target Kubernetes namespace)
    * `K8S_MANIFEST_DIR` (path to your Kubernetes manifests directory, e.g., `k8s`. Ensure this path is correct relative to the project root as used by Cloud Build substitutions)
    * `K8S_DEPLOYMENT_NAME` (name of your deployment resource in `deployment.yaml`)

2.  **`k8s/deployment.yaml`:**
    Ensure the `image:` field for your container in `k8s/deployment.yaml` uses a recognizable placeholder that `cloudbuild.yaml` will replace. The provided `cloudbuild.yaml` expects `__IMAGE_PLACEHOLDER__`. Example:
    ```yaml
    # ... inside k8s/deployment.yaml
    spec:
      containers:
      - name: my-container
        image: __IMAGE_PLACEHOLDER__
    # ...
    ```

## Deployment Flow

The end-to-end deployment flow is as follows:

1.  **Initiation:**
    * The developer ensures all code changes are committed and the `Dockerfile` is up-to-date.
    * The developer runs the deployment script from the project root: `./scripts/deploy.sh`.

2.  **`deploy.sh` Script Actions:**
    * Sets necessary environment variables for the build.
    * Validates that `PROJECT_ID` is set.
    * Submits the current directory (build context) to Google Cloud Build using the `cloudbuild.yaml` configuration file.
    * Passes the shell environment variables as substitutions (prefixed with `_`) to the Cloud Build pipeline.
    * Streams the build logs directly to the developer's terminal.

3.  **Cloud Build Pipeline (`cloudbuild.yaml` steps):**
    Cloud Build executes the following steps sequentially:
    1.  **Build Docker Image:**
        * Uses the `gcr.io/cloud-builders/docker` builder.
        * Builds a Docker image based on the `Dockerfile` found in the root of your submitted code.
        * Tags the image with the format: `${_AR_REGION}-docker.pkg.dev/${PROJECT_ID}/${_AR_REPO_NAME}/${_APP_NAME}:latest` (and potentially other tags like the commit SHA).
    2.  **Push Docker Image:**
        * Uses the `gcr.io/cloud-builders/docker` builder.
        * Pushes the newly built and tagged image to your specified Google Artifact Registry repository.
    3.  **Setup Kubeconfig:**
        * Uses the `gcr.io/cloud-builders/gcloud` builder.
        * Configures `kubectl` within the Cloud Build environment to connect to your target GKE cluster (`_GKE_CLUSTER_NAME` in `_GKE_CLUSTER_ZONE`).
    4.  **Prepare Kubernetes Manifests (Image Substitution):**
        * Uses the `gcr.io/cloud-builders/gcloud` builder (which includes tools like `sed`).
        * Replaces the placeholder `__IMAGE_PLACEHOLDER__` within your `k8s/deployment.yaml` (or any file specified by `_K8S_MANIFEST_DIR`) with the actual URI of the image just pushed to Artifact Registry.
    5.  **Apply Kubernetes Manifests:**
        * Uses the `gcr.io/cloud-builders/gcloud` builder (which includes `kubectl`).
        * Executes `kubectl apply -f <resolved_K8S_MANIFEST_DIR>/ --namespace=${_K8S_NAMESPACE}`.
        * This applies all configurations (your updated `deployment.yaml`, `service.yaml`, `hpa.yaml`, etc.) to your GKE cluster within the specified namespace. Kubernetes then works to achieve this desired state.
    6.  **Verify Deployment Rollout:**
        * Uses the `gcr.io/cloud-builders/gcloud` builder (with `kubectl`).
        * Runs `kubectl rollout status deployment/${_K8S_DEPLOYMENT_NAME} --namespace=${_K8S_NAMESPACE}`.
        * This step waits for the deployment to successfully complete its rollout or times out if there's an issue.

4.  **Outcome:**
    * If all steps succeed, the `deploy.sh` script will report success.
    * The new version of your application, using the newly built Docker image, will be running on your GKE cluster.

## Key Files Explained

* **`scripts/deploy.sh`:**
    * **Role:** User-facing script to initiate the entire CI/CD process.
    * **Key Actions:** Sets configurations, triggers Cloud Build, streams logs.
* **`cloudbuild.yaml`:**
    * **Role:** Defines the automated build, test (optional, not explicitly detailed but can be added), and deployment pipeline executed by Google Cloud Build.
    * **Key Actions:** Builds image, pushes to Artifact Registry, updates Kubernetes manifests, applies manifests to GKE, verifies deployment.
* **`k8s/deployment.yaml`:**
    * **Role:** Kubernetes manifest declaring the desired state for your application's deployment (pods, replicas, image version, resources, etc.).
    * **Key Feature for CI/CD:** Contains an `image` placeholder that is dynamically updated by the Cloud Build pipeline.
* **`k8s/service.yaml` (Example):**
    * **Role:** Kubernetes manifest to expose your application (e.g., via a LoadBalancer or ClusterIP). Applied along with `deployment.yaml`.
* **`k8s/hpa.yaml` (Example):**
    * **Role:** Kubernetes manifest to automatically scale your deployment based on metrics like CPU or memory utilization. Applied along with `deployment.yaml`.
* **`Dockerfile`:**
    * **Role:** Instructions to build your application's runnable Docker image, including all dependencies and runtime configurations.

## How to Run

1.  **Navigate to the project root directory** in your terminal.
2.  **Ensure `scripts/deploy.sh` is executable:**
    ```bash
    chmod +x scripts/deploy.sh
    ```
3.  **Configure variables:** Open `scripts/deploy.sh` and ensure all environment variables under the "Configuration" section are correctly set for your environment.
4.  **Run the script:**
    ```bash
    ./scripts/deploy.sh
    ```
5.  Monitor the output in your terminal as Cloud Build streams the logs.

## Post-Deployment Checks

Once the script reports success, you can check your GKE deployment using `kubectl`:

* **Check deployment status:**
    ```bash
    kubectl get deployments -n YOUR_K8S_NAMESPACE
    ```
* **Check running pods:**
    ```bash
    kubectl get pods -n YOUR_K8S_NAMESPACE -l app=YOUR_APP_LABEL # (e.g., app=pru-market-gen)
    ```
* **View logs for a specific pod:**
    ```bash
    kubectl logs <your-pod-name> -n YOUR_K8S_NAMESPACE -c YOUR_CONTAINER_NAME
    ```
* **Check service and get external IP (if using LoadBalancer):**
    ```bash
    kubectl get services -n YOUR_K8S_NAMESPACE
    ```
* **Check HPA status (if applicable):**
    ```bash
    kubectl get hpa -n YOUR_K8S_NAMESPACE
    ```

## Troubleshooting

* **Cloud Build Failures:** Check the detailed Cloud Build logs in the Google Cloud Console (Cloud Build > History).
* **Pod Errors (CrashLoopBackOff, ImagePullBackOff, Pending):**
    * Use `kubectl describe pod <pod-name> -n YOUR_K8S_NAMESPACE` to get detailed events and reasons for failure.
    * Check container logs using `kubectl logs <pod-name> -n YOUR_K8S_NAMESPACE`.
    * Ensure the image specified in `deployment.yaml` (after substitution) exists in Artifact Registry and GKE nodes have permission to pull it.
    * Verify resource requests/limits and GPU availability on nodes.
* **Deployment Rollout Stuck:** Use `kubectl rollout history deployment/YOUR_DEPLOYMENT_NAME -n YOUR_K8S_NAMESPACE` and `kubectl describe deployment YOUR_DEPLOYMENT_NAME -n YOUR_K8S_NAMESPACE`.

## Code changes

### Changes in `fastapi-backend`:
1) `fastapi-backend/main.py`:
   - Lines 18-34
   - Lines 50-106

2) `fastapi-backend/middlewares/user_validation.py`:
   - Lines 33-35

3) `fastapi-backend/utils/commons.py`:
   - Lines 18-24
   - Lines 39-46

4) `fastapi-backend/utils/constants.py`:
   - Line 40

5) `fastapi-backend/utils/validator.py`:
   - Lines 18-23
   - Lines 33-51
