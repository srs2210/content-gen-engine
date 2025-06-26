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

import axios from "axios";
import { AllRequestsResponse, EvaluatePostResponse, GeneratedResultsResponse, LoginResponse, PostVote, RequestConfig } from "../types";

export class ApiService {
  backendUrl: string;

  constructor() {
    this.backendUrl = "http://localhost:3001";
    // this.backendUrl = "https://my-vertexai-project-id-backend-1003801603843.us-central1.run.app";
    if (process.env.NODE_ENV === "production") {
      /** Change the backend URL to deployed backend URL */
      this.backendUrl = "https://content-generation-service-backend-164067361539.asia-southeast1.run.app";
    }
  }

  async login(email: string, pin: string): Promise<LoginResponse> {
    try {
      const response = await axios.post(`${this.backendUrl}/v1/login`, {
        email,
        pin,
      });
      return response.data;
    } catch (error) {
      console.error("Error occurred while logging in:", error);
      throw error;
    }
  }

  async updateUserSignOff(userId: string, signOff: string, isSignOffRemembered: boolean): Promise<boolean> {
    try {
      const response = await axios.post(`${this.backendUrl}/v1/update-user-sign-off`, { userId, signOff, isSignOffRemembered });
      return response.data.success;
    } catch (error) {
      console.error("Error occurred while updating user sign-off:", error);
      throw error;
    }
  }

  async getGeneratedPosts(userId: string, requestId: string): Promise<GeneratedResultsResponse> {
    try {
      const response = await axios.post(`${this.backendUrl}/v2/generated-results`, { userId, requestId });
      return response.data;
    } catch (error) {
      console.error("Error occurred while getting generated posts:", error);
      throw error;
    }
  }

  async updatePostVote(userId: string, postId: string, vote: PostVote): Promise<boolean> {
    try {
      const response = await axios.post(`${this.backendUrl}/v1/update-post-vote`, { userId, postId, vote });
      return response.data.success;
    } catch (error) {
      console.error("Error occurred while updating post vote:", error);
      throw error;
    }
  }

  async generatePosts(userId: string, requestConfig: RequestConfig): Promise<string> {
    console.log("running generate posts in api service")
    try {
      const response = await axios.post(`${this.backendUrl}/v1/generate-post`, { userId, requestConfig });
      return response.data.requestId;
    } catch (error) {
      console.error("Error occurred while generating posts:", error);
      throw error;
    }
  }

  async getPostRequests(userId: string): Promise<AllRequestsResponse> {
    try {
      const response = await axios.post(`${this.backendUrl}/v1/requests-by-user-id`, { userId });
      return response.data;
    } catch (error) {
      console.error("Error occurred while getting post requests:", error);
      throw error;
    }
  }

  async downloadImage(userId: string, postId: string): Promise<Blob> {
    try {
      const response = await axios.post(
        `${this.backendUrl}/v1/download-image`, 
        { userId, postId },
        { 
          responseType: 'blob'
        }
      );
      return response.data;
    } catch (error) {
      console.error("Error occurred while downloading image:", error);
      throw error;
    }
  }

  async updateRequestStatus(userId: string, requestId: string, status: string): Promise<boolean> {
    try {
      const response = await axios.post(`${this.backendUrl}/v1/update-request-status`, { userId, requestId, status });
      return response.data.success;
    } catch (error) {
      console.error("Error occurred while updating request status:", error);
      throw error;
    }
  }

  async evaluatePost(formData: FormData): Promise<EvaluatePostResponse> {
    try {
      const response = await axios.post(`${this.backendUrl}/v1/evaluate-post`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      });
      return response.data;
    } catch (error) {
      console.error("Error occurred while evaluating post:", error);
      throw error;
    }
  }
}

export const apiService = new ApiService();
