// src/index.js
import React from 'react';
import ReactDOM from 'react-dom/client';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';

import App from './App';
import LearnPage from './LearnPage';
import ProfilePage from './ProfilePage';
import LoginPage from './LoginPage';
import RegisterPage from './RegisterPage';
import RequireAuth from './RequireAuth';
import CulturePage from './CulturePage';

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
  <BrowserRouter>
    <Routes>
      {/* 公共路由 */}
      <Route path="login" element={<LoginPage />} />
      <Route path="register" element={<RegisterPage />} />

      {/* 受保护路由组 （pathless） */}
      <Route element={<RequireAuth />}>
        {/* 根路由 */}
        <Route index element={<App />} />
        {/* 相对子路由 */}
        <Route path="learn" element={<LearnPage />} />
        <Route path="profile" element={<ProfilePage />} />
        <Route path="culture" element={<CulturePage />} />
      </Route>

      {/* 兜底：未匹配的全部重定向到 /login */}
      <Route path="*" element={<Navigate to="/login" replace />} />
    </Routes>
  </BrowserRouter>
);
