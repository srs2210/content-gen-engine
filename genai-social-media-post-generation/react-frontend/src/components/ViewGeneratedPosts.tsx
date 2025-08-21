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

import { Alert, CircularProgress, Snackbar } from "@mui/material";
import { AxiosError } from "axios";
import { useEffect, useState } from "react";
import { useSnackbar } from "../contexts/SnackBarContext";
import useSimpleAuth from "../hooks/useSimpleAuth";
import { apiService } from "../services/api";
import { GeneratePostForm, Post, RequestStatus } from "../types";
import { getErrorMessage } from "../utils";
import GeneratedPost from "./GeneratedPost";
import SkeletonGeneratedPost from "./SkeletonGeneratedPost";

interface ViewGeneratedPostsProps {
  requestId: string;
  requestConfig: GeneratePostForm;
  setIsRequestCompleted: React.Dispatch<React.SetStateAction<boolean>>;
  isRequestCompleted: boolean;
  isEvaluationMode?: boolean;
}

const ViewGeneratedPosts = ({
  requestId,
  requestConfig,
  setIsRequestCompleted,
  isRequestCompleted,
  isEvaluationMode = false,
}: ViewGeneratedPostsProps) => {
  const [requestStatus, setRequestStatus] = useState<RequestStatus>("pending");
  const [posts, setPosts] = useState<Post[]>([]);
  const { user } = useSimpleAuth();
  const [isLoading, setIsLoading] = useState(true);
  const { showSnackbar, closeSnackbar, openSnackbar, snackbarMessage, snackbarSeverity } = useSnackbar();

  useEffect(() => {
    if (!isRequestCompleted) {
      const startTime = Date.now();
      setIsLoading(true);
      const interval = setInterval(async () => {
        try {
          const response = await apiService.getGeneratedPosts(user.uid, requestId);
          setRequestStatus(response.requestStatus);
          setPosts(response.posts.filter((post) => post.evaluationStatus !== "error"));

          // Check if the request is completed or if 10 minutes have passed
          const currentTime = Date.now();
          if (response.requestStatus === "completed" || response.requestStatus === "error" || currentTime - startTime >= 10 * 60 * 1000) {
            clearInterval(interval);
            setIsLoading(false);
            setIsRequestCompleted(true);
            if (currentTime - startTime >= 10 * 60 * 1000 || response.posts.length === 0) {
              await apiService.updateRequestStatus(user.uid, requestId, "error"); // If the request is not completed after 10 minutes or no posts were generated, set it to error
              const errorMessage = `Sorry, something went wrong while ${isEvaluationMode ? "evaluating" : "generating"} posts. Please try again.`;
              showSnackbar(errorMessage);
              setRequestStatus("error");
              setIsLoading(false);
            }
          }
        } catch (error) {
          const status = (error as AxiosError).response?.status; // Assuming error has a response with a status
          const errorMessage = getErrorMessage(status);
          showSnackbar(errorMessage);
          clearInterval(interval);
          setRequestStatus("error");
          setIsRequestCompleted(true);
        }
      }, 5000); // Call every 5 seconds

      return () => clearInterval(interval); // Cleanup on component unmount
    } else {
      setIsLoading(true);
      try {
        apiService.getGeneratedPosts(user.uid, requestId).then((response) => {
          setRequestStatus(response.requestStatus);
          setPosts(response.posts.filter((post) => post.evaluationStatus !== "error"));
        });
        setIsLoading(false);
      } catch (error) {
        const status = (error as AxiosError).response?.status; // Assuming error has a response with a status
        const errorMessage = getErrorMessage(status);
        showSnackbar(errorMessage);
        setRequestStatus("error");
        setIsLoading(false);
      }
    }
  }, [requestId]);

  return (
    <div className="flex flex-col gap-4 max-h-[60vh] overflow-y-auto">
      <div className="flex justify-between sticky top-0 bg-gray-100 z-10 py-2">
        <h1 className="text-xl font-medium">{requestConfig.requestTitle}</h1>
        {(requestStatus === "pending" || requestStatus === "evaluating") && (
          <div className="flex items-center bg-blue-300 px-4 py-2 rounded-md">
            <CircularProgress size={24} style={{ color: "black" }} className="mr-2" />
            {requestStatus === "pending" && !isRequestCompleted ? `${isEvaluationMode ? "Evaluating" : "Generating"} Posts...` : "Fetching Posts..."}
          </div>
        )}
      </div>
      {posts.map((post, idx) => (
        <GeneratedPost key={post.postId} post={post} evaluationOutcome={post.evaluationOutcome} postNumber={idx + 1} />
      ))}
      {isLoading &&
        requestStatus !== "error" &&
        Array.from({ length: requestConfig.postCount - posts.length }, (_, idx) => (
          <SkeletonGeneratedPost key={idx} postNumber={idx + 1 + posts.length} />
        ))}
      {requestStatus === "error" && (
        <div className="flex justify-center items-center">
          <h1 className="text-blue-500 font-bold">
            Sorry, something went wrong while {isEvaluationMode ? "evaluating" : "generating"} posts. Please update your inputs and try again.
          </h1>
          <p className="text-gray-700">This may happen if your request contains:</p>
          <ul className="list-disc text-gray-700 text-left pl-8">
            <li>References to celebrities or popular figures</li>
            <li>Content involving minors</li>
            <li>Sexual, explicit, violent, or inappropriate content</li>
          </ul>
        </div>
      )}
      {!isLoading && posts.length === 0 && requestStatus !== "error" && (
        <div className="flex flex-col justify-center items-center text-center">
          <h1 className="text-blue-500 font-bold mb-2">
            No posts were generated. Please update your inputs and try again.
          </h1>
          <p className="text-gray-700">This may happen if your request contains:</p>
          <ul className="list-disc text-gray-700 text-left pl-8">
            <li>References to celebrities or popular figures</li>
            <li>Content involving minors</li>
            <li>Sexual, explicit, violent, or inappropriate content</li>
          </ul>
        </div>
      )}
      <Snackbar open={openSnackbar} onClose={closeSnackbar}>
        <Alert onClose={closeSnackbar} severity={snackbarSeverity} sx={{ width: "100%" }}>
          {snackbarMessage}
        </Alert>
      </Snackbar>
    </div>
  );
};

export default ViewGeneratedPosts;
