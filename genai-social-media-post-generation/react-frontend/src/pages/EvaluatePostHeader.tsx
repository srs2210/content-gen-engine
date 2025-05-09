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

 import AddIcon from '@mui/icons-material/Add';
import InfoIcon from '@mui/icons-material/Info';
import { Box, LinearProgress, Typography } from '@mui/material';
import { useEffect, useState } from 'react';
import { EvaluationWorkflowStage } from "../types";
 
 interface EvaluatePostHeaderProps {
   workflowStage: EvaluationWorkflowStage;
   setWorkflowStage: React.Dispatch<React.SetStateAction<EvaluationWorkflowStage>>;
   requestId: string;
   isRequestCompleted: boolean;
   setRequestId: React.Dispatch<React.SetStateAction<string>>;
 }
 
 const EvaluatePostHeader = ({
   workflowStage,
   setWorkflowStage,
   requestId,
   isRequestCompleted,
   setRequestId,
 }: EvaluatePostHeaderProps) => {
   const [progress, setProgress] = useState(0);
 
   useEffect(() => {
     if (!isRequestCompleted && requestId) {
       const duration = 60; // seconds
       const intervalTime = 1000; // update every second
       const incrementPerInterval = (95 / duration) * (intervalTime / 1000);
 
       const timer = setInterval(() => {
         setProgress((oldProgress) => {
           const newProgress = oldProgress + incrementPerInterval;
           return newProgress >= 95 ? 95 : newProgress;
         });
       }, intervalTime);
 
       return () => clearInterval(timer);
     } else {
       setProgress(0);
     }
   }, [isRequestCompleted, requestId]);
 
   const handleViewGeneratedPosts = () => {
     if (requestId) {
       setWorkflowStage(EvaluationWorkflowStage.VIEW_EVALUATION_RESULTS);
     }
   };
 
   const handleCreateNewPost = () => {
     setRequestId("");
     setWorkflowStage(EvaluationWorkflowStage.UPLOAD_EVALUATION_CONTENT);
   };
 
   return (
     <div className="flex flex-col">
       <div className="flex items-center justify-between">
         <h1 className="text-2xl font-semibold mb-6">Validate Social Media Content</h1>
         
       </div>
       {/* Timeline */}
       <div className="flex justify-between items-center max-w-5xl">
         <div className="mb-6 flex items-center">
           <div
             onClick={() => setWorkflowStage(EvaluationWorkflowStage.UPLOAD_EVALUATION_CONTENT)}
             className={`flex items-center border-2 rounded-full p-4 cursor-pointer ${
               workflowStage === EvaluationWorkflowStage.UPLOAD_EVALUATION_CONTENT ? "border-red-600" : "border-red-200"
             }`}
           >
             <div
               className={`w-8 h-8 ${
                 workflowStage === EvaluationWorkflowStage.UPLOAD_EVALUATION_CONTENT ? "bg-red-600" : "bg-red-200"
               } rounded-full flex items-center justify-center`}
             >
               1
             </div>
             <span className="ml-2 text-sm font-medium">Upload Content</span>
           </div>
           <div className={`h-1 w-8 bg-gray-300 mx-2 ${requestId ? "bg-red-600" : "bg-gray-300"}`}></div>
           <div
             onClick={handleViewGeneratedPosts}
             className={`flex items-center border-2 rounded-full p-4 cursor-pointer ${
               workflowStage === EvaluationWorkflowStage.VIEW_EVALUATION_RESULTS
                 ? "border-red-600"
                 : requestId
                 ? "border-red-200"
                 : "border-gray-200 cursor-not-allowed"
             }`}
           >
             <div
               className={`w-8 h-8 ${
                 workflowStage === EvaluationWorkflowStage.VIEW_EVALUATION_RESULTS
                   ? "bg-red-600"
                   : requestId
                   ? "bg-red-200"
                   : "bg-gray-300"
               } rounded-full flex items-center justify-center`}
             >
               2
             </div>
             <span className="ml-2 text-sm font-medium">View Results</span>
           </div>
         </div>
         {isRequestCompleted && requestId && (
           <div onClick={handleCreateNewPost} className="bg-red-600 text-white px-4 py-2 rounded-md cursor-pointer h-fit flex items-center gap-1">
             <AddIcon fontSize="small" />
             Evaluate New Post
           </div>
         )}
       </div>
       {workflowStage === EvaluationWorkflowStage.VIEW_EVALUATION_RESULTS && !isRequestCompleted && requestId && (
         <div className="flex flex-col justify-center items-center gap-2 w-full bg-orange-100 p-4 rounded-md mb-4 max-w-5xl">
           <div className="flex items-center gap-2">
             <InfoIcon fontSize="small" className="text-gray-500" />
             <p className="text-sm text-gray-500">Evaluation can take up to 1 minute to complete</p>
           </div>
           <Box sx={{ width: '100%', mt: 1 }}>
             <LinearProgress 
               variant="determinate" 
               value={progress} 
               sx={{
                 height: 10,
                 borderRadius: 5,
                 '& .MuiLinearProgress-bar': {
                   backgroundColor: '#dc2626' // red-600
                 },
                 backgroundColor: '#fee2e2' // red-100
               }}
             />
             <Typography 
               variant="body2" 
               color="text.secondary" 
               align="center"
               sx={{ mt: 1 }}
             >
               {Math.round(progress)}%
             </Typography>
           </Box>
         </div>
       )}
     </div>
   );
 };
 
 export default EvaluatePostHeader;
 