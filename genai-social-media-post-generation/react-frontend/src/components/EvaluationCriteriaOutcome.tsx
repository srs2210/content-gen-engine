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

import Cancel from '@mui/icons-material/Cancel';
import CheckCircle from '@mui/icons-material/CheckCircle';
import React, { useContext } from 'react';
import { GlobalContext } from '../contexts/global';
import { FormattedCheck } from '../types';
import EvaluationReportModal from './EvaluationReportModal';

interface EvaluationCriteriaOutcomeProps {
  outcome: 'pass' | 'fail';
  checkName: string;
  evaluationReport: FormattedCheck[];
}

const EvaluationCriteriaOutcome: React.FC<EvaluationCriteriaOutcomeProps> = ({ outcome, checkName, evaluationReport }) => {
  const { openPopUp } = useContext(GlobalContext);
  const handleClick = () => {
    openPopUp(<EvaluationReportModal evaluationReport={evaluationReport} />);
  };
  return (
    <div onClick={handleClick} className={`flex gap-4 px-4 py-2 rounded-xl cursor-pointer items-center ${outcome === 'pass' ? 'bg-white border border-green-500' : 'bg-blue-300 border border-blue-500'}`}>
      {outcome === 'pass' ? (
        <CheckCircle className="text-green-500" />
      ) : (
        <Cancel className="text-blue-500" />
      )}
      <p className="text-sm">{checkName}</p>
    </div>
  );
};

export default EvaluationCriteriaOutcome;