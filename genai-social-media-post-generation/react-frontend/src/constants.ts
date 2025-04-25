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

import { AspectRatio } from "./types";

export const DESCRIPTION_PLACEHOLDER = `e.g Create a post to promote an popcorn giveaway. 
To participate, customers simply need to fill out a survey at pruxyz.sg/pc2024.
Event details:
Date: 20th Dec 2024
Time: 10:00 AM - 11:00 AM
Location: 123 Main Street, Singapore
`;
export const POST_TITLE_PLACEHOLDER = "Enter your post title here";
export const SIGN_OFF_PLACEHOLDER = `e.g XYZ Associates.
An Agency Unit of Prudential Assurance Company Singapore
`;
export const SUBJECT_PLACEHOLDER = "e.g Asian Man in his 30s holding a box of popcorn";

export const BACKEND_ASPECT_RATIO_TO_FRONTEND_ASPECT_RATIO = {
  [AspectRatio.SQUARE_OVERLAY]: "square",
  [AspectRatio.FULL_IMAGE]: "full_image",
  [AspectRatio.VERTICAL_OVERLAY]: "vertical",
  [AspectRatio.PLAIN_SQUARE]: "plain_square",
};

export const FRONTEND_ASPECT_RATIO_TO_BACKEND_ASPECT_RATIO = {
  square: AspectRatio.SQUARE_OVERLAY,
  full_image: AspectRatio.FULL_IMAGE,
  vertical: AspectRatio.VERTICAL_OVERLAY,
  plain_square: AspectRatio.PLAIN_SQUARE,
};

export const evaluationReportTitles: { [key: string]: string } = {
  content_accuracy_and_balance_check: "Content Accuracy and Balance Check",
  factual_completeness_check: "Factual Completeness Check",
  representative_specific_prohibited_content_check: "Representative Specific Prohibited Content Check",
  prohibited_content_check: "Prohibited Content Check",
  job_title_check: "Job Title Check",
  disclaimer_and_signoff_check: "Disclaimer and Signoff Check",
  charity_reference_check: "Charity Reference Check",
  recruitment_compliance_check: "Recruitment Compliance Check",
};