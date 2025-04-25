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

interface SkeletonGeneratedPostProps {
  postNumber: number;
}

const SkeletonGeneratedPost = ({ postNumber }: SkeletonGeneratedPostProps) => {
  return (
    <div className="flex flex-col gap-4 animate-pulse">
      <p className="text-xl font-medium">Version {postNumber}</p>
      <div className="flex gap-4">
        {/* Post */}
        <div className="flex flex-col gap-4 w-1/2 aspect-square">
          <div className="skeleton-image h-full bg-gray-300 rounded" />
          <p className="text-base font-medium text-center px-4 py-2 rounded-xl bg-gray-300" />
        </div>
        {/* Caption */}
        <div className="flex flex-col gap-4 w-1/4">
          <p className="text-sm font-medium">Caption</p>
          <p className="text-xs bg-gray-300 h-4 rounded" />
        </div>
        {/* Evaluation */}
        <div className="flex flex-col gap-2 w-1/4">
          <p className="text-sm font-medium">Evaluation</p>
          <div className="skeleton-evaluation bg-gray-300 h-4 rounded" />
          <div className="skeleton-evaluation bg-gray-300 h-4 rounded" />
          <div className="skeleton-evaluation bg-gray-300 h-4 rounded" />
          <div className="skeleton-evaluation bg-gray-300 h-4 rounded" />
          <div className="skeleton-evaluation bg-gray-300 h-4 rounded" />
          <div className="skeleton-evaluation bg-gray-300 h-4 rounded" />
          <div className="skeleton-evaluation bg-gray-300 h-4 rounded" />
        </div>
      </div>
    </div>
  );
};

export default SkeletonGeneratedPost; 