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

import ArrowBackIcon from "@mui/icons-material/ArrowBack";
import RefreshIcon from "@mui/icons-material/Refresh";
import Alert from "@mui/material/Alert";
import Snackbar from "@mui/material/Snackbar";
import { AxiosError } from "axios";
import React, { useEffect, useState } from "react";
import ViewGeneratedPosts from "../components/ViewGeneratedPosts";
import { useSnackbar } from "../contexts/SnackBarContext";
import useSimpleAuth from "../hooks/useSimpleAuth";
import { apiService } from "../services/api";
import { AllRequestsResponse, Request } from "../types";
import { generatePostFormFromRequestConfig, getErrorMessage } from "../utils";

const ViewAllPosts: React.FC = () => {
  const { user } = useSimpleAuth();
  const [postRequests, setPostRequests] = useState<AllRequestsResponse>({ requests: [] });
  const [selectedRequestId, setSelectedRequestId] = useState<string>("");
  const [, setIsRequestCompleted] = useState<boolean>(false);
  const { showSnackbar, closeSnackbar, openSnackbar, snackbarMessage, snackbarSeverity } = useSnackbar();
  const [isLoading, setIsLoading] = useState<boolean>(true);

  useEffect(() => {
    fetchPostRequests();
  }, [user.uid]);

  const fetchPostRequests = async () => {
    try {
      setIsLoading(true);
      const requests = await apiService.getPostRequests(user.uid);
      setPostRequests(requests);
    } catch (error) {
      const status = (error as AxiosError).response?.status;
      const errorMessage = getErrorMessage(status);
      showSnackbar(errorMessage);
    } finally {
      setIsLoading(false);
    }
  };

  const handleLoadRequest = (request: Request) => {
    if (request.status !== "error") {
      setSelectedRequestId(request.requestId);
    }
  };

  return (
    <div className="flex w-full h-fit bg-white">
      <main className="flex flex-col w-full p-8">
        <div className="flex justify-between items-center mb-6">
          <h1 className="text-2xl font-bold text-gray-800">Generated Posts History</h1>
          <button
            onClick={fetchPostRequests}
            className="flex gap-2 items-center px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
          >
            <RefreshIcon fontSize="small" />
            Refresh
          </button>
        </div>

        <div className="flex flex-col gap-6">
          {selectedRequestId && (
            <div
              onClick={() => setSelectedRequestId("")}
              className="px-4 py-2 bg-blue-600 w-fit text-white rounded-md hover:bg-blue-700 flex items-center gap-2 cursor-pointer"
            >
              <ArrowBackIcon fontSize="small" />
              Back to All Posts
            </div>
          )}
          {/* Requests List Panel */}
          {!selectedRequestId && (
            <div className="bg-zinc-100 rounded-lg shadow-md px-6 overflow-y-auto max-h-[50vh] relative">
              <h2 className="text-xl font-semibold sticky top-0 bg-zinc-100 h-10 py-4 h-fit">Recent Requests</h2>
              {isLoading ? (
                <div className="flex justify-center items-center h-32">
                  <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
                </div>
              ) : (
                <div className="space-y-4 mt-4 pb-4">
                  {postRequests.requests.map((request) => (
                    <div
                      key={request.requestId}
                      onClick={() => handleLoadRequest(request)}
                      className={`p-4 rounded-md cursor-pointer hover:bg-gray-50 ${
                        request.status === "error" ? "opacity-50 cursor-not-allowed" : ""
                      } transition-colors ${
                        selectedRequestId === request.requestId
                          ? "bg-blue-100 border-2 border-blue-500"
                          : "bg-white hover:bg-gray-50"
                      }`}
                    >
                      <div className="flex justify-between items-center">
                        <div>
                          <p className="font-medium">{request.requestConfig.requestTitle || "Untitled Request"}</p>
                          <p className="text-sm text-gray-500">
                            {new Date(
                              new Date(request.requestDate).getTime()
                            ).toLocaleString("en-SG", {
                              timeZone: "Asia/Singapore",
                              dateStyle: "medium",
                              timeStyle: "medium",
                            })}
                          </p>
                        </div>
                        <span
                          className={`px-2 py-1 rounded-full text-xs ${
                            request.status === "completed"
                              ? "bg-green-100 text-green-800"
                              : request.status === "error"
                              ? "bg-blue-100 text-blue-800"
                              : "bg-yellow-100 text-yellow-800"
                          }`}
                        >
                          {request.status}
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}

          {/* Selected Post Preview Panel */}
          <div className="flex flex-col gap-6 pb-12">
            <p className="text-lg font-semibold text-center">Selected Post Preview</p>
            <div className="bg-zinc-100 rounded-lg shadow-md p-6 overflow-y-auto max-h-[calc(100vh-12rem)]">
              {selectedRequestId && postRequests.requests.find((r) => r.requestId === selectedRequestId) ? (
                <ViewGeneratedPosts
                  setIsRequestCompleted={setIsRequestCompleted}
                  requestId={selectedRequestId}
                  requestConfig={generatePostFormFromRequestConfig(
                    postRequests.requests.find((r) => r.requestId === selectedRequestId)!.requestConfig
                  )}
                  isRequestCompleted={["error", "completed"].includes(
                    postRequests.requests.find((r) => r.requestId === selectedRequestId)?.status || ""
                  )}
                />
              ) : (
                <div className="flex justify-center items-center h-full text-gray-500">
                  Select a request to view its generated posts
                </div>
              )}
            </div>
          </div>
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

export default ViewAllPosts;
