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

import ContentCopyIcon from "@mui/icons-material/ContentCopy";
import DownloadIcon from "@mui/icons-material/Download";
import ThumbDownIcon from "@mui/icons-material/ThumbDown";
import ThumbUpIcon from "@mui/icons-material/ThumbUp";
import { useState } from "react";
import Markdown from "react-markdown";
import { useSnackbar } from "../contexts/SnackBarContext";
import { apiService } from "../services/api";
import { Post, PostVote } from "../types";
import {
  consolidateContentAccuracyAndBalanceCheck,
  consolidateProhibitedContentCheck,
  consolidateRepresentativeSpecificProhibitedContentCheck,
  formatHighLevelChecks,
} from "../utils";
import EvaluationCriteriaOutcome from "./EvaluationCriteriaOutcome";

interface GeneratedPostProps {
  post: Post;
  evaluationOutcome?: string;
  postNumber: number;
}

const evaluationTitles: { [key: string]: string } = {
  content_accuracy_and_balance_check: "Content Accuracy and Balance Check",
  representative_specific_prohibited_content_check: "Representative Specific Prohibited Content Check",
  prohibited_content_check: "Prohibited Content Check",
  job_title_check: "Job Title Check",
  disclaimer_and_signoff_check: "Disclaimer and Signoff Check",
  charity_reference_check: "Charity Reference Check",
  recruitment_post_check: "Recruitment Post Check",
};

const GeneratedPost = ({ post, evaluationOutcome, postNumber }: GeneratedPostProps) => {
  const [postVote, setPostVote] = useState(post.postVote);
  const { showSnackbar } = useSnackbar();

  const handlePostVote = async (vote: PostVote) => {
    const prevVote = postVote;
    const newVote = postVote === vote ? 0 : vote;
    setPostVote(newVote);
    try {
      const result = await apiService.updatePostVote(post.userId, post.postId, newVote);
      if (!result) {
        setPostVote(prevVote);
      }
    } catch (error) {
      setPostVote(prevVote);
    }
  };

  const handleDownload = async () => {
    try {
      showSnackbar("Download will start shortly", "info");
      const response = await apiService.downloadImage(post.userId, post.postId);
      // Create a temporary URL for the blob
      const url = window.URL.createObjectURL(response);

      // Create a temporary link element
      const link = document.createElement("a");
      link.href = url;
      link.download = `post-${post.postId}.png`; // Set desired filename

      // Append to document, click, and cleanup
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);

      // Release the blob URL
      window.URL.revokeObjectURL(url);
    } catch (error) {
      console.error("Failed to download image:", error);
      showSnackbar("Sorry, failed to download image. Please try again later.", "error");
    }
  };

  const handleCopyCaption = () => {
    if (post.postCaption) {
      navigator.clipboard
        .writeText(post.postCaption)
        .then(() => showSnackbar("Caption copied to clipboard", "success"))
        .catch((err) => console.error("Failed to copy caption:", err));
    }
  };

  return (
    <div className="flex flex-col gap-4">
      <p className="text-xl font-medium">Version {postNumber}</p>
      <div className="flex gap-4">
        {/* Post */}
        <div className="flex flex-col gap-4 w-1/2">
          <div className="relative">
            <img
              src={post.finalImageUrl}
              alt="Generated post"
              onContextMenu={(e) => {
                if (evaluationOutcome !== "pass") {
                  e.preventDefault();
                }
              }}
              className={`max-w-full ${evaluationOutcome !== "pass" ? "cursor-not-allowed select-none" : ""}`}
              draggable="false"
            />
            {evaluationOutcome && evaluationOutcome === "pass" && (
              <DownloadIcon
                onClick={handleDownload}
                className="absolute top-2 right-2 cursor-pointer text-white hover:text-gray-200 bg-black/30 rounded-full p-1"
                style={{ fontSize: "24px" }}
              />
            )}
          </div>
          {evaluationOutcome ? (
            <div className="flex justify-between">
              <div className="flex gap-2">
                <p
                  className={`text-base font-medium text-center px-4 py-2 rounded-full w-fit text-white ${
                    evaluationOutcome === "pass" ? "bg-green-500" : "bg-blue-500"
                  }`}
                >
                  {evaluationOutcome === "pass" ? "Passed" : "Failed"}
                </p>
                {/* {post.evaluationReport?.image_quality_check.image_quality_check === "fail" && (
                  <p className="flex items-center text-xs text-gray-500 bg-yellow-200 px-4 py-2 rounded-full text-center">
                    ⚠️ Masking Issues detected. Please rerun.
                  </p>
                )} */}
              </div>
              <div className="flex items-center space-x-2">
                <ThumbUpIcon
                  onClick={() => handlePostVote(1)}
                  style={{ color: postVote === 1 ? "green" : "gray", cursor: "pointer" }}
                />
                <ThumbDownIcon
                  onClick={() => handlePostVote(-1)}
                  style={{ color: postVote === -1 ? "red" : "gray", cursor: "pointer" }}
                />
              </div>
            </div>
          ) : (
            <div className="flex flex-col gap-4 w-1/2">
              <p className="text-base font-medium text-center px-4 py-2 rounded-xl bg-gray-300" />
            </div>
          )}
        </div>
        {/* Caption */}
        <div className="flex flex-col gap-4 w-1/4">
          <div className="bg-white rounded-lg shadow-md h-fit flex flex-col">
            <div className="p-4 flex-grow">
              <p className="text-sm font-medium mb-2">Caption</p>
              <Markdown className="text-xs">{post.postCaption}</Markdown>
            </div>
            <div
              className="border-t p-2 flex items-center gap-2 cursor-pointer hover:bg-gray-50"
              onClick={handleCopyCaption}
            >
              <ContentCopyIcon className="text-gray-500" sx={{ fontSize: 16 }} />
              <span className="text-sm text-gray-500">Copy Caption</span>
            </div>
          </div>
        </div>
        {/* Evaluation */}
        <div className="flex flex-col gap-2 w-1/4">
          <p className="text-sm font-medium">Evaluation</p>
          {/* <div className="flex gap-4 bg-white border border-green-500 px-4 py-2 rounded-xl items-center">
          <CheckCircle className="text-green-500" />
          <p className="text-sm">{evaluationTitles.overallCompliance}</p>
        </div> */}
          {post.evaluationReport ? (
            <>
              <EvaluationCriteriaOutcome
                outcome={consolidateContentAccuracyAndBalanceCheck(
                  post.evaluationReport.content_accuracy_and_balance_check
                )}
                checkName={evaluationTitles.content_accuracy_and_balance_check}
                evaluationReport={formatHighLevelChecks(post.evaluationReport.content_accuracy_and_balance_check)}
              />
              <EvaluationCriteriaOutcome
                outcome={consolidateRepresentativeSpecificProhibitedContentCheck(
                  post.evaluationReport.representative_specific_prohibited_content_check
                )}
                checkName={evaluationTitles.representative_specific_prohibited_content_check}
                evaluationReport={formatHighLevelChecks(
                  post.evaluationReport.representative_specific_prohibited_content_check
                )}
              />
              <EvaluationCriteriaOutcome
                outcome={consolidateProhibitedContentCheck(post.evaluationReport.prohibited_content_check)}
                checkName={evaluationTitles.prohibited_content_check}
                evaluationReport={formatHighLevelChecks(post.evaluationReport.prohibited_content_check)}
              />
              <EvaluationCriteriaOutcome
                outcome={post.evaluationReport.job_title_check.outcome !== "non-compliant" ? "pass" : "fail"}
                checkName={evaluationTitles.job_title_check}
                evaluationReport={[
                  {
                    title: evaluationTitles.job_title_check,
                    outcome: post.evaluationReport.job_title_check.outcome,
                    explanation: `Approved Titles: ${
                      post.evaluationReport.job_title_check.approved_titles_found.length
                        ? post.evaluationReport.job_title_check.approved_titles_found.join(", ")
                        : "None"
                    } Forbidden Titles: ${
                      post.evaluationReport.job_title_check.forbidden_titles_found.length
                        ? post.evaluationReport.job_title_check.forbidden_titles_found.join(", ")
                        : "None"
                    }`,
                  },
                ]}
              />
              <EvaluationCriteriaOutcome
                outcome={
                  post.evaluationReport.disclaimer_and_signoff_check.disclaimer_signoff_check.outcome !==
                  "non-compliant"
                    ? "pass"
                    : "fail"
                }
                checkName={evaluationTitles.disclaimer_and_signoff_check}
                evaluationReport={[
                  {
                    title: evaluationTitles.disclaimer_and_signoff_check,
                    outcome: post.evaluationReport.disclaimer_and_signoff_check.disclaimer_signoff_check.outcome,
                    explanation:
                      post.evaluationReport.disclaimer_and_signoff_check.disclaimer_signoff_check.explanation,
                  },
                ]}
              />
              <EvaluationCriteriaOutcome
                outcome={
                  post.evaluationReport.charity_reference_check.charity_reference_check.outcome !== "non-compliant"
                    ? "pass"
                    : "fail"
                }
                checkName={evaluationTitles.charity_reference_check}
                evaluationReport={[
                  {
                    title: evaluationTitles.charity_reference_check,
                    outcome: post.evaluationReport.charity_reference_check.charity_reference_check.outcome,
                    explanation: post.evaluationReport.charity_reference_check.charity_reference_check.explanation,
                  },
                ]}
              />
              <EvaluationCriteriaOutcome
                outcome={
                  post.evaluationReport.recruitment_compliance_check.recruitment_post_check.outcome !== "non-compliant"
                    ? "pass"
                    : "fail"
                }
                checkName={evaluationTitles.recruitment_post_check}
                evaluationReport={[
                  {
                    title: evaluationTitles.recruitment_post_check,
                    outcome: post.evaluationReport.recruitment_compliance_check.recruitment_post_check.outcome,
                    explanation: post.evaluationReport.recruitment_compliance_check.recruitment_post_check.explanation,
                  },
                ]}
              />
            </>
          ) : (
            <>
              <div className="skeleton-evaluation bg-gray-300 h-4 rounded" />
              <div className="skeleton-evaluation bg-gray-300 h-4 rounded" />
              <div className="skeleton-evaluation bg-gray-300 h-4 rounded" />
              <div className="skeleton-evaluation bg-gray-300 h-4 rounded" />
              <div className="skeleton-evaluation bg-gray-300 h-4 rounded" />
              <div className="skeleton-evaluation bg-gray-300 h-4 rounded" />
              <div className="skeleton-evaluation bg-gray-300 h-4 rounded" />
            </>
          )}
        </div>
      </div>
    </div>
  );
};

export default GeneratedPost;
