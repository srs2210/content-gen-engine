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

import { Link, useLocation } from "react-router-dom";

const routes = [
  {
    route: "/generate-post",
    displayText: "Generate Post",
  },
  {
    route: "/view-all-posts",
    displayText: "View All Posts",
  }
];

const SideBar = () => {
  const { pathname } = useLocation();

  return (
    <div className="flex flex-col justify-between h-full mt-4 p-4">
      <div className="flex flex-col gap-16">
        <div className="flex flex-col gap-2 w-fit">
          {routes.map((route, i) => {
            return (
              <Link to={route.route} key={i}>
                <div className={`py-2 px-4 min-w-[200px] rounded-md ${pathname === route.route ? "bg-red-200" : "hover:bg-red-50"}`}>
                  {route.displayText}
                </div>
              </Link>
            );
          })}
        </div>
      </div>
    </div>
  );
};

export default SideBar;
