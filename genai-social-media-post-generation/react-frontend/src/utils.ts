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

import {
  BACKEND_ASPECT_RATIO_TO_FRONTEND_ASPECT_RATIO,
  FRONTEND_ASPECT_RATIO_TO_BACKEND_ASPECT_RATIO,
} from "./constants";
import {
  ArtStyle,
  ContentAccuracyAndBalanceCheck,
  EvaluationCheck,
  FormattedCheck,
  GeneratePostForm,
  HighLevelChecks,
  ProhibitedContentCheck,
  RepresentativeSpecificProhibitedContentCheck,
  RequestConfig,
} from "./types";

export const consolidateContentAccuracyAndBalanceCheck = (evaluationCheck: ContentAccuracyAndBalanceCheck) => {
  const evaluationCheckKeys = Object.keys(evaluationCheck).filter((key) => {
    return key !== "description_of_post";
  });
  const allPass = evaluationCheckKeys.every(
    (key) =>
      (evaluationCheck[key as keyof ContentAccuracyAndBalanceCheck] as EvaluationCheck).outcome === "compliant" ||
      (evaluationCheck[key as keyof ContentAccuracyAndBalanceCheck] as EvaluationCheck).outcome === "not-applicable"
  );
  return allPass ? "pass" : "fail";
};

export const consolidateProhibitedContentCheck = (evaluationCheck: ProhibitedContentCheck) => {
  const evaluationCheckKeys = Object.keys(evaluationCheck).filter((key) => key !== "post_description");
  const allPass = evaluationCheckKeys.every(
  (key) =>
      (evaluationCheck[key as keyof ProhibitedContentCheck] as EvaluationCheck).outcome === "compliant" ||
      (evaluationCheck[key as keyof ProhibitedContentCheck] as EvaluationCheck).outcome === "not-applicable"
  );
  return allPass ? "pass" : "fail";
};

export const consolidateRepresentativeSpecificProhibitedContentCheck = (
  evaluationCheck: RepresentativeSpecificProhibitedContentCheck
) => {
  const evaluationCheckKeys = Object.keys(evaluationCheck).filter((key) => key !== "post_description");
  const allPass = evaluationCheckKeys.every(
    (key) =>
      (evaluationCheck[key as keyof RepresentativeSpecificProhibitedContentCheck] as EvaluationCheck).outcome ===
      "compliant" ||
      (evaluationCheck[key as keyof RepresentativeSpecificProhibitedContentCheck] as EvaluationCheck).outcome ===
        "not-applicable"
  );
  return allPass ? "pass" : "fail";
};

export const generateRequestConfig = (formData: GeneratePostForm): RequestConfig => {
  return {
    requestTitle: formData.requestTitle,
    postDescription: formData.postDescription,
    aspectRatio: BACKEND_ASPECT_RATIO_TO_FRONTEND_ASPECT_RATIO[formData.aspectRatio],
    artStyle: formData.artStyle,
    subject: formData.subject,
    backgroundColor: formData.backgroundColor,
    signOff: formData.signOff,
    isRecruitmentRelated: formData.isRecruitmentRelated,
    isCharityRelated: formData.isCharityRelated,
    postCount: formData.postCount,
    socialMediaPlatform: formData.socialMediaPlatform,
  };
};

export const generatePostFormFromRequestConfig = (requestConfig: RequestConfig): GeneratePostForm => {
  return {
    requestTitle: requestConfig.requestTitle,
    postDescription: requestConfig.postDescription,
    aspectRatio:
      FRONTEND_ASPECT_RATIO_TO_BACKEND_ASPECT_RATIO[
        requestConfig.aspectRatio as keyof typeof FRONTEND_ASPECT_RATIO_TO_BACKEND_ASPECT_RATIO
      ],
    artStyle: requestConfig.artStyle as ArtStyle,
    subject: requestConfig.subject,
    signOff: requestConfig.signOff,
    isRecruitmentRelated: requestConfig.isRecruitmentRelated,
    isCharityRelated: requestConfig.isCharityRelated,
    postCount: requestConfig.postCount,
    socialMediaPlatform: requestConfig.socialMediaPlatform || "instagram",
  };
};

export const getErrorMessage = (status: number | undefined): string => {
  if (!status) {
    return "Sorry, something went wrong. Please try again.";
  }
  const errorMessages: { [key: number]: string } = {
    400: "Bad Request. Please check your input.",
    401: "Unauthorized. Please log in again.",
    403: "You do not have permission to perform this action.",
    404: "The requested resource could not be found.",
    409: "There was a conflict with your request.",
    500: "Sorry, something went wrong. Please try again later.",
  };
  return errorMessages[status] || "Sorry, something went wrong. Please try again.";
};

export function formatHighLevelChecks(check: HighLevelChecks): FormattedCheck[] {
  const results: FormattedCheck[] = [];

  // Remove description fields and process only EvaluationCheck fields
  Object.entries(check).forEach(([key, value]) => {
    if (isEvaluationCheck(value)) {
      results.push({
        title: formatTitle(key),
        outcome: value.outcome,
        explanation: value.explanation,
      });
    }
  });

  return results;
}

// Type guard to check if a value is an EvaluationCheck
function isEvaluationCheck(value: any): value is EvaluationCheck {
  return value && typeof value === "object" && "outcome" in value && "explanation" in value;
}

// Helper to format the title from snake_case to Title Case
function formatTitle(key: string): string {
  return key
    .split("_")
    .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
    .join(" ");
}
