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

import { CircularProgress } from "@mui/material";
import { DESCRIPTION_PLACEHOLDER, SIGN_OFF_PLACEHOLDER, SUBJECT_PLACEHOLDER } from "../constants";
import { AspectRatio, GeneratePostForm } from "../types";

interface ConfigurePostFormProps {
  formData: GeneratePostForm;
  handleInputChange: (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>) => void;
  handleSubmit: (e: React.FormEvent<HTMLFormElement>) => void;
  isFormSubmitted: boolean;
  rememberSignOff: boolean;
  handleRememberSignOffChange: (e: React.ChangeEvent<HTMLInputElement>) => void;
  isDisabled: boolean;
  isRequestCompleted: boolean;
}

const ConfigurePostForm = ({
  formData,
  handleInputChange,
  handleSubmit,
  isFormSubmitted,
  rememberSignOff,
  handleRememberSignOffChange,
  isDisabled,
  isRequestCompleted,
}: ConfigurePostFormProps) => {
  return (
    <form onSubmit={handleSubmit}>
      {/* Post Title */}
      <div className="mb-4">
        <label htmlFor="postTitle" className="block text-sm font-medium text-gray-700">
          Post Title
        </label>
        <input
          type="text"
          name="requestTitle"
          id="requestTitle"
          value={formData.requestTitle}
          onChange={handleInputChange}
          className="mt-1 p-2 w-full border rounded-md placeholder-custom"
          required
          placeholder="Enter your post title here"
          minLength={3}
          disabled={isDisabled}
        />
        {isFormSubmitted && formData.requestTitle.length < 3 && (
          <p className="text-red-500 text-xs mt-1">Title must be at least 3 characters long.</p>
        )}
      </div>

      {/* Description */}
      <div className="mb-4">
        <label htmlFor="description" className="block text-sm font-medium text-gray-700">
          Describe your post
        </label>
        <textarea
          name="postDescription"
          id="postDescription"
          value={formData.postDescription}
          onChange={handleInputChange}
          className="mt-1 p-2 w-full border rounded-md placeholder-custom"
          rows={4}
          required
          placeholder={DESCRIPTION_PLACEHOLDER}
          minLength={10}
          disabled={isDisabled}
        />
        {isFormSubmitted && formData.postDescription.length < 10 && (
          <p className="text-red-500 text-xs mt-1">Description must be at least 10 characters long.</p>
        )}
      </div>

      {/* Flex Row for Aspect Ratio, Art Style, Subject */}
      <div className="flex flex-wrap -mx-2 mb-4">
        {/* Aspect Ratio */}
        <div className="w-full md:w-1/3 px-2">
          <label htmlFor="aspectRatio" className="block text-sm font-medium text-gray-700">
            Aspect Ratio
          </label>
          <select
            name="aspectRatio"
            id="aspectRatio"
            value={formData.aspectRatio}
            onChange={handleInputChange}
            className="mt-1 p-2 w-full border rounded-md"
            disabled={isDisabled}
          >
            <option value={AspectRatio.PLAIN_SQUARE}>{AspectRatio.PLAIN_SQUARE}</option>
            <option value={AspectRatio.FULL_IMAGE}>{AspectRatio.FULL_IMAGE}</option>
            <option value={AspectRatio.SQUARE_OVERLAY}>{AspectRatio.SQUARE_OVERLAY}</option>
            <option value={AspectRatio.VERTICAL_OVERLAY}>{AspectRatio.VERTICAL_OVERLAY}</option>
          </select>
        </div>

        {/* Art Style */}
        <div className="w-full md:w-1/3 px-2">
          <label htmlFor="artStyle" className="block text-sm font-medium text-gray-700">
            Art Style
          </label>
          <select
            name="artStyle"
            id="artStyle"
            value={formData.artStyle}
            onChange={handleInputChange}
            className="mt-1 p-2 w-full border rounded-md"
            disabled={isDisabled}
          >
            <option value="Photorealistic">Photorealistic</option>
            <option value="Vector Art">Vector Art</option>
          </select>
        </div>

        {/* Subject */}
        <div className="w-full md:w-1/3 px-2">
          <label htmlFor="subject" className="block text-sm font-medium text-gray-700">
            Subject
          </label>
          <input
            type="text"
            name="subject"
            id="subject"
            value={formData.subject}
            onChange={handleInputChange}
            className="mt-1 p-2 w-full border rounded-md placeholder-custom"
            required
            placeholder={SUBJECT_PLACEHOLDER}
            disabled={isDisabled}
          />
        </div>
      </div>

      {/* Background Color */}
      {formData.aspectRatio === AspectRatio.FULL_IMAGE && (
        <div className="mb-4">
          <label htmlFor="backgroundColor" className="block text-sm font-medium text-gray-700">
            Background Color <span className="text-xs text-gray-500">(Only for Full Image posts)</span>
          </label>
          <input
            type="color"
            name="backgroundColor"
            id="backgroundColor"
            value={formData.backgroundColor}
            onChange={handleInputChange}
            className="mt-1 p-1 w-20 h-10 border rounded-md"
            defaultValue="#ffffff"
            disabled={isDisabled}
          />
        </div>
      )}

      <div className="w-full md:w-1/3 mb-4">
        <label htmlFor="socialMediaPlatform" className="block text-sm font-medium text-gray-700">
          Social Media Platform
        </label>
        <select
          name="socialMediaPlatform"
          id="socialMediaPlatform"
          value={formData.socialMediaPlatform}
          onChange={handleInputChange}
          className="mt-1 p-2 w-full border rounded-md"
          disabled={isDisabled}
        >
          <option value="instagram">Instagram</option>
          <option value="facebook">Facebook</option>
          <option value="x">X</option>
          <option value="linkedin">LinkedIn</option>
        </select>
      </div>

      {/* Sign-off */}
      <div className="mb-4">
        <div className="flex justify-between items-center">
          <label htmlFor="signOff" className="block text-sm font-medium text-gray-700">
            Sign-off
          </label>
          <div className="flex items-center mt-2">
            <input
              type="checkbox"
              name="rememberSignOff"
              id="rememberSignOff"
              checked={rememberSignOff}
              onChange={handleRememberSignOffChange}
              className="mr-2"
              disabled={isDisabled}
            />
            <label htmlFor="rememberSignOff" className="text-sm font-medium text-gray-700">
              Remember Sign-off
            </label>
          </div>
        </div>
        <textarea
          name="signOff"
          id="signOff"
          value={formData.signOff}
          onChange={handleInputChange}
          className="mt-1 p-2 w-full border rounded-md placeholder-custom"
          placeholder={SIGN_OFF_PLACEHOLDER}
          disabled={isDisabled}
        />
      </div>

      {/* Recruitment Related */}
      <div className="mb-4">
        <label htmlFor="isRecruitmentRelated" className="flex items-center">
          <input
            type="checkbox"
            name="isRecruitmentRelated"
            id="isRecruitmentRelated"
            checked={formData.isRecruitmentRelated}
            onChange={handleInputChange}
            className="mr-2"
            disabled={isDisabled}
          />
          <span className="text-sm font-medium text-gray-700">Is this post recruitment related?</span>
        </label>
      </div>

      {/* Charity Related */}
      <div className="mb-4">
        <label htmlFor="isCharityRelated" className="flex items-center">
          <input
            type="checkbox"
            name="isCharityRelated"
            id="isCharityRelated"
            checked={formData.isCharityRelated}
            onChange={handleInputChange}
            className="mr-2"
            disabled={isDisabled}
          />
          <span className="text-sm font-medium text-gray-700">Is this post charity related?</span>
        </label>
      </div>

      {/* Submit Button */}
      <div className="mt-6 flex items-center justify-center">
        <button
          type="submit"
          className={`w-fit px-4 bg-red-600 text-white py-2 rounded-md hover:bg-red-700 focus:outline-none ${
            isDisabled ? "opacity-50 cursor-not-allowed" : ""
          }`}
          disabled={isDisabled}
        >
          {isDisabled ? (
            <div className="flex items-center">
              {!isRequestCompleted && <CircularProgress size={24} style={{ color: "white" }} className="mr-2" />}
              {isRequestCompleted ? "Post Generated" : "Generating..."}
            </div>
          ) : (
            "Generate Post"
          )}
        </button>
      </div>
    </form>
  );
};

export default ConfigurePostForm;
