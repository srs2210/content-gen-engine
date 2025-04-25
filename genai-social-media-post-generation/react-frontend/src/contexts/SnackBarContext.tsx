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

import React, { createContext, ReactNode, useContext, useState } from 'react';

interface SnackbarContextType {
  openSnackbar: boolean;
  snackbarMessage: string;
  showSnackbar: (message: string, severity?: 'success' | 'error' | 'info') => void;
  closeSnackbar: () => void;
  snackbarSeverity: 'success' | 'error' | 'info';
}

const SnackbarContext = createContext<SnackbarContextType | undefined>(undefined);

export const SnackbarProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [openSnackbar, setOpenSnackbar] = useState(false);
  const [snackbarMessage, setSnackbarMessage] = useState('');
  const [snackbarSeverity, setSnackbarSeverity] = useState<'success' | 'error' | 'info'>('info');

  const showSnackbar = (message: string, severity: 'success' | 'error' | 'info' = 'error') => {
    setSnackbarMessage(message);
    setSnackbarSeverity(severity);
    setOpenSnackbar(true);
    setTimeout(() => setOpenSnackbar(false), 6000); // Auto-hide after 6 seconds
  };

  const closeSnackbar = () => {
    setOpenSnackbar(false);
  };

  return (
    <SnackbarContext.Provider value={{ openSnackbar, snackbarMessage, snackbarSeverity, showSnackbar, closeSnackbar }}>
      {children}
    </SnackbarContext.Provider>
  );
};

export const useSnackbar = () => {
  const context = useContext(SnackbarContext);
  if (!context) {
    throw new Error('useSnackbar must be used within a SnackbarProvider');
  }
  return context;
};