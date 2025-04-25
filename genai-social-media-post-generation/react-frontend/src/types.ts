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

export type UserData = {
  display_name: string;
  email?: string;
  photo_url?: string;
  uid: string;
  signOff?: string;
};

export type QueryObject = {
  faviconImageUrl?: string;
  primaryColor?: string;
  secondaryColor?: string;
  warningColor?: string;
  alertColor?: string;
  logoUrl?: string;
  fontUrl?: string;
};

export type LoginResponse = {
  userId: string;
  signOff: string;
  name: string;
};

export enum AspectRatio {
  SQUARE_OVERLAY = "Square Overlay",
  FULL_IMAGE = "Full Image",
  VERTICAL_OVERLAY = "Vertical Overlay",
  PLAIN_SQUARE = "Plain Square",
}
export type ArtStyle = "Photorealistic" | "Abstract" | "Vector Art";

export interface GeneratePostForm {
  requestTitle: string;
  postDescription: string;
  aspectRatio: AspectRatio;
  artStyle: ArtStyle;
  subject: string;
  backgroundColor?: string;
  signOff: string;
  isRecruitmentRelated: boolean;
  isCharityRelated: boolean;
  postCount: number;
  socialMediaPlatform: SocialMediaPlatform;
}

export enum WorkflowStage {
  CONFIGURE_POST = "Configure Post",
  VIEW_GENERATED_POSTS = "View Generated Posts",
}

export type Request = {
  requestId: string;
  userId: string;
  status: RequestStatus;
  requestDate: string;
  requestConfig: RequestConfig;
  originalRequestId?: string;
}

export type RequestConfig = {
  requestTitle: string;
  postDescription: string;
  aspectRatio: string;
  artStyle: string;
  subject: string;
  backgroundColor?: string;
  signOff: string;
  isRecruitmentRelated: boolean;
  isCharityRelated: boolean;
  postCount: number;
  socialMediaPlatform?: SocialMediaPlatform;
}

export type SocialMediaPlatform = "instagram" | "facebook" | "x" | "linkedin";

export interface EvaluationCheck {
  explanation: string;
  outcome: 'compliant' | 'non-compliant' | 'not-applicable';
}

export interface ContentAccuracyAndBalanceCheck {
  professional_language: EvaluationCheck;
  description_of_post: string;
  customer_data_handling: EvaluationCheck;
  fairness_and_balance: EvaluationCheck;
  non_exaggeration: EvaluationCheck;
}

export interface RepresentativeSpecificProhibitedContentCheck {
  response_to_negative_content_check: EvaluationCheck;
  misrepresentation_of_affiliation_check: EvaluationCheck;
  unauthorized_logo_use_check: EvaluationCheck;
  post_description: string;
  internal_information_disclosure_check: EvaluationCheck;
}

export interface ProhibitedContentCheck {
  offensive_content_check: EvaluationCheck;
  post_description: string;
  reputational_damage_check: EvaluationCheck;
  competitor_comparison_check: EvaluationCheck;
}

export interface FactualCompletenessCheck {
  factual_completeness_check: EvaluationCheck;
  post_description: string;
}

export interface JobTitleCheck {
  approved_titles_found: string[];
  forbidden_titles_found: string[];
  outcome: 'compliant' | 'non-compliant' | 'not-applicable';
}

export interface DisclaimerAndSignoffCheck {
  disclaimer_signoff_check: {
      explanation: string;
      valid_sign_off_present: boolean;
      valid_disclaimer_present: boolean;
      outcome: 'compliant' | 'non-compliant' | 'not-applicable';
      post_description: string;
      disclaimer_required: boolean;
  };
}

export interface CharityReferenceCheck {
  charity_reference_check: {
      explanation: string;
      valid_disclaimer_present: boolean;
      charity_mentioned: boolean;
      outcome: 'compliant' | 'non-compliant' | 'not-applicable';
      conditional_fundraising_present: boolean;
  };
}

export interface RecruitmentComplianceCheck {
  recruitment_post_check: {
      explanation: string;
      corporate_impersonation: boolean;
      pacs_tagged: boolean;
      benefits_mentioned: boolean;
      disclaimer_present: boolean;
      outcome: 'compliant' | 'non-compliant' | 'not-applicable';
  };
}

export interface ImageQualityCheck {
    explanation: string;
    image_quality_check: 'pass' | 'fail';
}

export type PostVote = 1 | -1 | 0;

// Define the type for a single post
export interface Post {
  userId: string;
  generatedImageUrl: string;
  finalImageUrl: string;
  postCreationTime: string;
  postId: string;
  requestId: string;
  postStatus: string;
  postVote: PostVote;
  postCaption?: string;
  evaluationStatus: string;
  evaluationOutcome?: 'pass' | 'fail';
  evaluationReport?: {
      content_accuracy_and_balance_check: ContentAccuracyAndBalanceCheck;
      factual_completeness_check: FactualCompletenessCheck;
      representative_specific_prohibited_content_check: RepresentativeSpecificProhibitedContentCheck;
      prohibited_content_check: ProhibitedContentCheck;
      job_title_check: JobTitleCheck;
      disclaimer_and_signoff_check: DisclaimerAndSignoffCheck;
      charity_reference_check: CharityReferenceCheck;
      recruitment_compliance_check: RecruitmentComplianceCheck;
      image_quality_check: ImageQualityCheck;
  };
}

export type HighLevelChecks = ContentAccuracyAndBalanceCheck | RepresentativeSpecificProhibitedContentCheck | ProhibitedContentCheck;

// Define the main response type
export interface GeneratedResultsResponse {
  requestStatus: RequestStatus;
  posts: Post[];
}

export type RequestStatus = 'pending' | 'completed' | 'evaluating' | 'error';

export interface FormattedCheck {
  title: string;
  outcome: "compliant" | "non-compliant" | "not-applicable";
  explanation: string;
}

export interface AllRequestsResponse {
  requests: Request[];
}