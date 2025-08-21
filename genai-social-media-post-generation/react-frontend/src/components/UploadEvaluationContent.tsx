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

import React, { useCallback, useState } from 'react';
import { DropzoneOptions, FileRejection, useDropzone } from 'react-dropzone';

interface UploadEvaluationContentProps {
  caption: string;
  setCaption: (caption: string) => void;
  imageFile: File | null;
  setImageFile: (file: File | null) => void;
  imagePreview: string | null;
  setImagePreview: (preview: string | null) => void;
  handleSubmit: (e: React.FormEvent) => Promise<void>;
  isDisabled: boolean; // To disable form while submitting/loading
}

const MAX_CAPTION_LENGTH = 255;
const MAX_IMAGE_SIZE_MB = 10;
const MAX_IMAGE_SIZE_BYTES = MAX_IMAGE_SIZE_MB * 1024 * 1024;

const UploadEvaluationContent: React.FC<UploadEvaluationContentProps> = ({
  caption,
  setCaption,
  imageFile,
  setImageFile,
  imagePreview,
  setImagePreview,
  handleSubmit,
  isDisabled,
}) => {
  const [captionError, setCaptionError] = useState<string | null>(null);
  const [imageError, setImageError] = useState<string | null>(null);

  const handleCaptionChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    const newCaption = e.target.value;
    if (newCaption.length <= MAX_CAPTION_LENGTH) {
      setCaption(newCaption);
      setCaptionError(null);
    } else {
      // Optionally, allow setting caption up to MAX_CAPTION_LENGTH
      // setCaption(newCaption.substring(0, MAX_CAPTION_LENGTH));
      setCaptionError(`Caption cannot exceed ${MAX_CAPTION_LENGTH} characters.`);
    }
  };

  const onDrop = useCallback((acceptedFiles: File[], fileRejections: FileRejection[]) => {
    // Clear previous image error
    setImageError(null);

    if (fileRejections && fileRejections.length > 0) {
      fileRejections.forEach(rejection => {
        rejection.errors.forEach(err => {
          if (err.code === 'file-too-large') {
            setImageError(`Image size cannot exceed ${MAX_IMAGE_SIZE_MB}MB.`);
          } else {
            setImageError(err.message);
          }
        });
      });
      // Clear previous image if a new rejected file is dropped
      setImageFile(null);
      if (imagePreview) URL.revokeObjectURL(imagePreview);
      setImagePreview(null);
      return;
    }

    if (acceptedFiles && acceptedFiles.length > 0) {
      const file = acceptedFiles[0];
      setImageFile(file);
      if (imagePreview) URL.revokeObjectURL(imagePreview);
      setImagePreview(URL.createObjectURL(file));
      setImageError(null); // Clear error on successful upload
    }
  }, [imagePreview, setImageFile, setImagePreview]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone(
    {
      onDrop,
      accept: { 'image/*': [] },
      multiple: false,
      disabled: isDisabled,
      maxSize: MAX_IMAGE_SIZE_BYTES, // Add maxSize for react-dropzone validation
    } as unknown as DropzoneOptions
  );

  // Cleanup object URL on component unmount or when preview changes
  React.useEffect(() => {
    return () => {
      if (imagePreview) {
        URL.revokeObjectURL(imagePreview);
      }
    };
  }, [imagePreview]);

  const currentCaptionLength = caption.length;
  const isSubmitDisabled = !imageFile || !caption || !!captionError || !!imageError || isDisabled;

  return (
    <form onSubmit={handleSubmit} className="flex flex-col gap-6">
       {/* Title for the form section */}
       {/* <h3 className="text-xl font-semibold text-gray-700 mb-2">1. Upload Image & Caption</h3> */}

      {/* Image Upload Container */}
      <div className="flex flex-col gap-2">
        <label className="font-medium">Image</label>
        {/* Outer div gets root props for drag events */}
        <div 
          {...getRootProps()} 
          className={`flex flex-col justify-center items-center border-2 border-dashed rounded-lg p-10 h-80 max-w-80 
            text-gray-500 
            ${isDisabled ? 'bg-gray-100 cursor-not-allowed' : 'cursor-pointer'} 
            ${isDragActive ? 'border-blue-500 bg-blue-50' : (imageError ? 'border-blue-500' : 'border-gray-300 hover:border-gray-400')}`}
        >
          {/* Input gets input props */}
          <input {...getInputProps() as React.InputHTMLAttributes<HTMLInputElement>} />
          {imagePreview && !imageError ? (
             <img src={imagePreview} alt="Preview" className="max-h-full object-contain" />
          ) : (
             <p className="text-center">
                {isDragActive ? 'Drop the image here ...' : (imageError || 'Click or Drag and drop image here')}
             </p>
          )}
        </div>
        {imageError && <p className="text-sm text-blue-600 mt-1">{imageError}</p>}
         <p className="text-xs text-gray-500 mt-1">Max image size: {MAX_IMAGE_SIZE_MB}MB.</p>
      </div>

      {/* Caption Input */}
      <div className="flex flex-col gap-2">
        <div className="flex justify-between items-center">
            <label htmlFor="caption" className="font-medium">Caption</label>
            <span className={`text-xs ${currentCaptionLength > MAX_CAPTION_LENGTH ? 'text-blue-600' : 'text-gray-500'}`}>
                {currentCaptionLength}/{MAX_CAPTION_LENGTH}
            </span>
        </div>
        <textarea
          id="caption"
          rows={4}
          className={`border rounded-md p-2 focus:outline-none focus:ring-2 w-full disabled:bg-gray-100 
            ${captionError ? 'border-blue-500 focus:ring-blue-300' : 'border-gray-300 focus:ring-blue-200'}`}
          value={caption}
          onChange={handleCaptionChange}
          placeholder="Enter the post caption..."
          disabled={isDisabled}
          aria-invalid={!!captionError}
          aria-describedby={captionError ? "caption-error" : undefined}
        />
        {captionError && <p id="caption-error" className="text-sm text-blue-600 mt-1">{captionError}</p>}
      </div>

      {/* Submit Button - TODO: Replace with actual reusable Button component if available */}
      <button 
         type="submit" // Important for form submission
         className="bg-blue-600 text-white py-2 px-6 rounded-md hover:bg-blue-700 self-start disabled:opacity-50 disabled:cursor-not-allowed"
         disabled={isSubmitDisabled}
      >
         {isDisabled ? 'Submitting...' : 'Submit for Evaluation'}
      </button>
    </form>
  );
};

export default UploadEvaluationContent; 