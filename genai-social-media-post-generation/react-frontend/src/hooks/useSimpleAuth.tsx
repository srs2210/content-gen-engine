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

import { useEffect } from "react";
import { useHistory } from "react-router-dom";
import { UserData } from "../types";

const useSimpleAuth = () => {
  const history = useHistory();
  let userId = document.cookie.split('; ').find(row => row.startsWith('userId='));
  let userName = document.cookie.split('; ').find(row => row.startsWith('userName='));
  let userSignOff = document.cookie.split('; ').find(row => row.startsWith('userSignOff='));

  useEffect(() => {
    if (userId) {
      const id = userId.split('=')[1];
      userId = id;
    } else {
      // Redirect to login if userId is not found
      if (window.location.pathname !== '/') {
        window.location.href = '/';
      }
    }
  }, [userId, history]);

  const signOut = () => {
    // Remove session cookies
    document.cookie = "userId=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;";
    document.cookie = "userName=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;"; // Clear userName
    document.cookie = "userSignOff=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;"; // Clear userSignOff
    window.location.href = '/'; // Redirect to login page
  };

  const user: UserData = {
    uid: userId?.split('=')[1] || '',
    display_name: userName?.split('=')[1] || '',
    signOff: decodeURIComponent(userSignOff?.split('=')[1] || ''),
  };

  return { user, signOut };
};

export default useSimpleAuth;