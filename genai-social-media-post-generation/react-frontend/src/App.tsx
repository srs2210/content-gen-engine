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

import { ThemeProvider, createTheme } from "@mui/material";
import { ReactElement, useState } from "react";
import { BrowserRouter, Redirect, Route, Switch } from "react-router-dom";
import "./App.css";
// import AppFooter from "./components/AppFooter";
import AppHeader from "./components/AppHeader";
import PopUp from "./components/PopUp";
import SideBar from "./components/SideBar";
import { GlobalContext, GlobalContextType } from "./contexts/global";
import { SnackbarProvider } from "./contexts/SnackBarContext";
import useSimpleAuth from "./hooks/useSimpleAuth";
import EvaluatePostPage from "./pages/EvaluatePostPage";
import GeneratePost from "./pages/GeneratePost";
import Login from "./pages/Login";
import ViewAllPosts from "./pages/ViewAllPosts";

const muiTheme = createTheme({
  typography: {
    fontFamily: '"Google Sans", sans-serif',
    button: {
      textTransform: "none",
      fontSize: "inherit",
      fontWeight: "normal",
      fontFamily: "inherit",
    },
  },
});

function App() {
  const [globalContext, setGlobalContext] = useState<GlobalContextType>({
    popUpChild: null,
    isPopUpOpen: false,
    closePopUp: () => {
      setGlobalContext((prevContext) => ({
        ...prevContext,
        popUpChild: null,
        isPopUpOpen: false,
      }));
    },
    openPopUp: (childNode: ReactElement) => {
      setGlobalContext((prevContext) => ({
        ...prevContext,
        popUpChild: childNode,
        isPopUpOpen: true,
      }));
    },
  });

  const { user, signOut } = useSimpleAuth();

  return (
    <GlobalContext.Provider value={globalContext}>
      <SnackbarProvider>
        <ThemeProvider theme={muiTheme}>
          <BrowserRouter>
          <div className="h-fit">
            {user.uid && (
              <AppHeader user={user} signOut={signOut}></AppHeader>
            )}
            {!user.uid ? <Login></Login> : <div className="app-container w-full flex">
              <PopUp></PopUp>
              <SideBar></SideBar>
              <Switch>
                <Route path="/generate-post">
                  <GeneratePost></GeneratePost>
                </Route>
                <Route path="/view-all-posts">
                  <ViewAllPosts></ViewAllPosts>
                </Route>
                <Route path="/evaluate-post">
                  <EvaluatePostPage></EvaluatePostPage>
                </Route>
                <Redirect to={"/generate-post"}></Redirect>
              </Switch>
            </div>}
            {/* <AppFooter></AppFooter> */}
            </div>
          </BrowserRouter>
        </ThemeProvider>
      </SnackbarProvider> 
    </GlobalContext.Provider>
  );
}

export default App;
