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

import Alert from "@mui/material/Alert";
import Snackbar from "@mui/material/Snackbar";
import { AxiosError } from "axios";
import React, { useState } from "react";
import ConfigurePostForm from "../components/ConfigurePostForm";
import ViewGeneratedPosts from "../components/ViewGeneratedPosts";
import { useSnackbar } from "../contexts/SnackBarContext";
import useSimpleAuth from "../hooks/useSimpleAuth";
import { apiService } from "../services/api";
import { AspectRatio, GeneratePostForm, WorkflowStage } from "../types";
import { generateRequestConfig, getErrorMessage } from "../utils";
import GeneratePostHeader from "./GeneratePostHeader";

const GeneratePost: React.FC = () => {
  const { user } = useSimpleAuth();
  const [formData, setFormData] = useState<GeneratePostForm>({
    requestTitle: "",
    postDescription: "",
    aspectRatio: AspectRatio.FULL_IMAGE,
    artStyle: "Photorealistic",
    subject: "",
    signOff: user.signOff || "",
    isRecruitmentRelated: false,
    isCharityRelated: false,
    postCount: 3,
    socialMediaPlatform: "instagram",
  });
  const [isFormSubmitted, setIsFormSubmitted] = useState<boolean>(false);
  const [rememberSignOff, setRememberSignOff] = useState<boolean>(user.signOff ? true : false);
  const [requestId, setRequestId] = useState<string>("");
  const [workflowStage, setWorkflowStage] = useState<WorkflowStage>(WorkflowStage.CONFIGURE_POST);
  const { showSnackbar, closeSnackbar, openSnackbar, snackbarMessage, snackbarSeverity } = useSnackbar();
  const [isRequestCompleted, setIsRequestCompleted] = useState<boolean>(false);

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>) => {
    const { name, value, type, checked } = e.target as HTMLInputElement;
    setFormData((prevData) => ({
      ...prevData,
      [name]: type === "checkbox" ? checked : value,
    }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    setIsFormSubmitted(true);
    setIsRequestCompleted(false);
    e.preventDefault();

    if (formData.requestTitle.length < 3) {
      showSnackbar("Title must be at least 3 characters long.", "error");
      return;
    }
    if (formData.postDescription.length < 3) {
      showSnackbar("Description must be at least 3 characters long.", "error");
      return;
    }
    if (formData.subject.length < 3) {
      showSnackbar("Subject must be at least 3 characters long.", "error");
      return;
    }

    setWorkflowStage(WorkflowStage.VIEW_GENERATED_POSTS);

    try {
      const requestId = await apiService.generatePosts(user.uid, generateRequestConfig(formData));
      setRequestId(requestId);
    } catch (error) {
      const status = (error as AxiosError).response?.status; // Assuming error has a response with a status
      const errorMessage = getErrorMessage(status);
      showSnackbar(errorMessage);
      setWorkflowStage(WorkflowStage.CONFIGURE_POST);
    }

    try {
      if (rememberSignOff) {
        await apiService.updateUserSignOff(user.uid, formData.signOff, rememberSignOff);
        const expiryDate = new Date();
        expiryDate.setMonth(expiryDate.getMonth() + 1);
        document.cookie = `userSignOff=${encodeURIComponent(formData.signOff)}; path=/; expires=${expiryDate.toUTCString()};`;
      } else {
        await apiService.updateUserSignOff(user.uid, formData.signOff, rememberSignOff);
        document.cookie = `userSignOff=; path=/; expires=Thu, 01 Jan 1970 00:00:00 GMT;`;
      }
    } catch (error) {
      const status = (error as AxiosError).response?.status; // Assuming error has a response with a status
      const errorMessage = getErrorMessage(status);
      showSnackbar(errorMessage);
    }
  };

  const handleRememberSignOffChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setRememberSignOff(e.target.checked);
  };

  return (
    <div className="flex w-full h-fit bg-white">
      <main className="flex flex-col w-full p-8">
        {/* Main Content Area */}
        <GeneratePostHeader
          setRequestId={setRequestId}
          isRequestCompleted={isRequestCompleted}
          workflowStage={workflowStage}
          setWorkflowStage={setWorkflowStage}
          requestId={requestId}
        />
        <div className="bg-zinc-100 max-w-5xl rounded-lg shadow-md p-6 overflow-y-auto">
          {workflowStage === WorkflowStage.CONFIGURE_POST && (
            <ConfigurePostForm
              formData={formData}
              handleInputChange={handleInputChange}
              handleSubmit={handleSubmit}
              isFormSubmitted={isFormSubmitted}
              rememberSignOff={rememberSignOff}
              handleRememberSignOffChange={handleRememberSignOffChange}
              isDisabled={!!requestId}
              isRequestCompleted={isRequestCompleted}
            />
          )}
          {workflowStage === WorkflowStage.VIEW_GENERATED_POSTS && (
            <ViewGeneratedPosts
              setIsRequestCompleted={setIsRequestCompleted}
              requestId={requestId}
              requestConfig={formData}
              isRequestCompleted={isRequestCompleted}
            />
          )}
        </div>
      </main>
      <Snackbar open={openSnackbar} onClose={closeSnackbar} autoHideDuration={6000}>
        <Alert onClose={closeSnackbar} severity={snackbarSeverity} sx={{ width: "100%" }}>
          {snackbarMessage}
        </Alert>
      </Snackbar>
    </div>
  );
};

export default GeneratePost;
