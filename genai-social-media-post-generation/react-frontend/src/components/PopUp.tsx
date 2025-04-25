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

import { useContext } from "react";
import { GlobalContext } from "../contexts/global";

function PopUp() {
  const { closePopUp, isPopUpOpen, popUpChild } = useContext(GlobalContext);

  const handleClick = (e: MouseEvent) => {
    const modalBackground = document.getElementById("modal-background");
    if (e.target === modalBackground) {
      closePopUp();
    }
  };

  return isPopUpOpen ? (
    <div
      id="modal-background"
      className="absolute bg-black/60 w-full h-full z-20 flex items-center justify-center flex-col gap-4"
      onClick={(e) => handleClick(e as any)}
    >
      <div id="modal" className="bg-white w-fit max-w-[600px] p-4 rounded-lg">
        {popUpChild}
      </div>
    </div>
  ) : null;
}

export default PopUp;
