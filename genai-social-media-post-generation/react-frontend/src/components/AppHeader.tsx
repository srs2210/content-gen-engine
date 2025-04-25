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

import LogoutIcon from "@mui/icons-material/Logout";
import { Avatar } from "@mui/material";
import { UserData } from "../types";
import { LinkWithQuery } from "./LinkWithQuery";

const AppHeader = ({ user, signOut }: { user: UserData; signOut: () => void }) => {

  return (
    <div className="app-header px-4 flex items-center bg-[#ED1B2E]">
      <LinkWithQuery to="/generate-post">
        <img src={"/prudential_logo.png"} alt="" className="h-full max-h-[60px] bg-white object-contain rounded-xl p-2" />
      </LinkWithQuery>
      <p className="flex items-center ml-4 border-l-2 border-gray-300 pl-4 h-[60px] font-bold text-xl text-white">Post Generator</p>
      <div className="flex flex-row gap-6 items-center ml-auto text-gray-500">
        <p className="text-white">Welcome, {user.display_name}!</p>
        <div onClick={signOut} className="cursor-pointer">
          <LogoutIcon style={{ color: "white" }}></LogoutIcon>
        </div>
        <Avatar sizes="small" src={user.photo_url}>{user.photo_url ? "" : user.display_name.split(' ').map(n => n[0]).join('')}</Avatar>
      </div>
    </div>
  );
};

export default AppHeader;
