/*
 Copyright 2024 Google LLC

 Licensed under the Apache License, Version 2.0 (the "License");
 you may not use this file except in compliance with the License.
 You may obtain a copy of the License at

      https://www.apache.org/licenses/LICENSE-2.0

 Unless required by applicable law or agreed to in writing, software
 distributed under the License is distributed on an "AS IS" BASIS,
 WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 See the License for the specific language governing permissions and
 limitations under the License.
 */

import { Snackbar } from "@mui/material";
import Alert from "@mui/material/Alert";
import { AxiosError } from "axios";
import React, { useState } from "react";
import UploadEvaluationContent from "../components/UploadEvaluationContent";
import ViewGeneratedPosts from "../components/ViewGeneratedPosts";
import { useSnackbar } from "../contexts/SnackBarContext";
import useSimpleAuth from "../hooks/useSimpleAuth";
import { apiService } from "../services/api";
import { EvaluationWorkflowStage, GeneratePostForm } from "../types"; // Import WorkflowStage
import { getErrorMessage } from "../utils"; // Assuming utility exists
import EvaluatePostHeader from "./EvaluatePostHeader";

const mockRequestConfig: Partial<GeneratePostForm> = {
  requestTitle: "Evaluation Request",
};

const EvaluatePostPage: React.FC = () => {
  const [caption, setCaption] = useState("");
  const [imageFile, setImageFile] = useState<File | null>(null);
  const [imagePreview, setImagePreview] = useState<string | null>(null);
  const [requestId, setRequestId] = useState<string>("");
  const [workflowStage, setWorkflowStage] = useState<EvaluationWorkflowStage>(
    EvaluationWorkflowStage.UPLOAD_EVALUATION_CONTENT
  );
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isRequestCompleted, setIsRequestCompleted] = useState<boolean>(false); // For ViewGeneratedPosts
  const { user } = useSimpleAuth();

  const { showSnackbar, closeSnackbar, openSnackbar, snackbarMessage, snackbarSeverity } = useSnackbar();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault(); // Prevent default form submission
    if (!imageFile || !caption || isSubmitting) {
      console.error("Image and caption are required, or already submitting.");
      return;
    }

    setIsSubmitting(true);
    setRequestId("");
    setIsRequestCompleted(false);

    console.log("Submitting for evaluation:", { image: imageFile.name, caption });

    try {
      const formData = new FormData();
      formData.append("file", imageFile);
      formData.append("caption", caption);
      formData.append("userId", user.uid);

      const response = await apiService.evaluatePost(formData);

      setRequestId(response.requestId);
      setWorkflowStage(EvaluationWorkflowStage.VIEW_EVALUATION_RESULTS);
    } catch (error) {
      console.error("Submission error:", error);
      const status = (error as AxiosError).response?.status;
      const errorMessage = getErrorMessage(status); // Use utility if available
      showSnackbar(errorMessage || "Error occurred while submitting post for evaluation", "error");
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="flex w-full h-fit bg-white">
      <main className="flex flex-col w-full p-8">
        <EvaluatePostHeader
          workflowStage={workflowStage}
          setWorkflowStage={setWorkflowStage}
          requestId={requestId}
          isRequestCompleted={isRequestCompleted}
          setRequestId={setRequestId}
        />
        <div className="bg-zinc-100 max-w-5xl rounded-lg shadow-md p-6 overflow-y-auto">
          {workflowStage === EvaluationWorkflowStage.UPLOAD_EVALUATION_CONTENT && (
            <UploadEvaluationContent
              caption={caption}
              setCaption={setCaption}
              imageFile={imageFile}
              setImageFile={setImageFile}
              imagePreview={imagePreview}
              setImagePreview={setImagePreview}
              handleSubmit={handleSubmit}
              isDisabled={isSubmitting}
            />
          )}
          {workflowStage === EvaluationWorkflowStage.VIEW_EVALUATION_RESULTS && requestId && (
            <ViewGeneratedPosts
              setIsRequestCompleted={setIsRequestCompleted}
              requestId={requestId}
              requestConfig={mockRequestConfig as GeneratePostForm}
              isRequestCompleted={isRequestCompleted}
              isEvaluationMode={true}
            />
          )}
        </div>
        <Snackbar open={openSnackbar} onClose={closeSnackbar}>
          <Alert onClose={closeSnackbar} severity={snackbarSeverity} sx={{ width: "100%" }}>
            {snackbarMessage}
          </Alert>
        </Snackbar>
      </main>
    </div>
  );
};

export default EvaluatePostPage;
