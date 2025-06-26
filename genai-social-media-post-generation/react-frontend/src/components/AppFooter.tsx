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

const AppFooter = () => {
  return (
    <div className="absolute bottom-0 z-10 py-2">
      <div className="flex flex-col px-4">
        <p className="text-xs text-gray-500">Powered by:</p>
        <img
          src="/ai_lab_logo.png"
          alt="Company Logo"
          className="h-full max-h-[60px] bg-white object-contain rounded-xl p-2"
        />
      </div>
    </div>
  );
};

export default AppFooter;
