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

import MuiAlert, { AlertProps } from '@mui/material/Alert';
import CircularProgress from '@mui/material/CircularProgress';
import Snackbar from '@mui/material/Snackbar';
import React, { useEffect, useState } from 'react';
import { useSnackbar } from '../contexts/SnackBarContext';
import { apiService } from '../services/api';

const Alert = React.forwardRef<HTMLDivElement, AlertProps>(function Alert(props, ref) {
  return <MuiAlert elevation={6} ref={ref} variant="filled" {...props} />;
});

const Login: React.FC = () => {
  const [currentSlide, setCurrentSlide] = useState(0);
  const { showSnackbar, closeSnackbar, openSnackbar, snackbarMessage, snackbarSeverity } = useSnackbar();
  const [isLoading, setIsLoading] = useState(false);

  const slides = [
    { id: 1, text: 'Generate your own posts with AI in minutes.' },
    { id: 2, text: 'Customize your posts to your needs and your audience.' },
    { id: 3, text: 'Save time in maintaining your social media.' },
  ];

  // Auto-move carousel every 5 seconds
  useEffect(() => {
    const timer = setInterval(() => {
      setCurrentSlide((prev) => (prev + 1) % slides.length);
    }, 5000); // 5 seconds interval
    return () => clearInterval(timer); // Clear interval on unmount
  }, [slides.length]);

  const handleNextSlide = () => {
    setCurrentSlide((prev) => (prev + 1) % slides.length);
  };

  const handlePrevSlide = () => {
    setCurrentSlide((prev) => (prev - 1 + slides.length) % slides.length);
  };

  const handleLogin = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    const email = e.currentTarget.email.value;
    const pin = e.currentTarget.pin.value;
    try {
      setIsLoading(true);
      const response = await apiService.login(email, pin);
      // set cookies
      const expiryDate = new Date();
      expiryDate.setMonth(expiryDate.getMonth() + 1);
      document.cookie = `userSignOff=${encodeURIComponent(response.signOff)}; path=/; expires=${expiryDate.toUTCString()};`;
      document.cookie = `userId=${response.userId}; path=/; expires=${expiryDate.toUTCString()};`;
      document.cookie = `userName=${response.name}; path=/; expires=${expiryDate.toUTCString()};`;
      // redirect to home
      window.location.href = '/generate-post';
    } catch (error) {
      showSnackbar('Login failed. Please check your credentials.');
      console.error(error);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex p-8 h-screen items-center justify-center bg-zinc-200">
      {/* Left Section - Login Form */}
      <div className="flex h-[50vh] w-1/3 flex-col rounded-l-2xl items-center justify-center bg-white p-8 shadow-md">
        <h1 className="text-2xl font-bold text-gray-800 mb-6">Log in to Create Your Post</h1>
        <form className="w-full max-w-sm" onSubmit={(e) => handleLogin(e)}>
          <div className="mb-4">
            <label htmlFor="email" className="block text-gray-700 font-medium mb-2">
              User ID
            </label>
            <input
              type="text"
              id="email"
              className="w-full px-4 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
              placeholder="Enter your User ID"
            />
          </div>
          <div className="mb-6">
            <label htmlFor="pin" className="block text-gray-700 font-medium mb-2">
              PIN
            </label>
            <input
              type="password"
              id="pin"
              className="w-full px-4 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
              placeholder="Enter your PIN"
            />
          </div>
          <button
            type="submit"
            className="flex items-center justify-center w-full bg-[#2563EB] text-white py-2 px-4 rounded-md hover:bg-blue-600 focus:ring-4 focus:ring-blue-300"
            disabled={isLoading}
          >
            {isLoading ? <CircularProgress size={20} style={{ color: 'white' }}/> : 'Login'}
          </button>
        </form>
      </div>

      {/* Right Section - Carousel */}
      <div className="w-1/3 bg-[#2563EB] h-[50vh] rounded-r-2xl text-white flex flex-col items-center shadow-lg justify-center relative">
        <div className="absolute inset-0 flex items-center justify-center">
          <h2 className="text-xl font-semibold text-center px-4">{slides[currentSlide].text}</h2>
        </div>
        <div className="absolute bottom-6 flex gap-4">
          <button
            className="p-2 bg-[#043FC1] w-10 h-10 rounded-full hover:bg-blue-800"
            onClick={handlePrevSlide}
          >
            &lt;
          </button>
          <button
            className="p-2 bg-[#043FC1] w-10 h-10 rounded-full hover:bg-blue-800"
            onClick={handleNextSlide}
          >
            &gt;
          </button>
        </div>
      </div>
      <Snackbar open={openSnackbar} onClose={closeSnackbar}>
        <Alert onClose={closeSnackbar} severity={snackbarSeverity} sx={{ width: '100%' }}>
          {snackbarMessage}
        </Alert>
      </Snackbar>
    </div>
  );
};

export default Login;
