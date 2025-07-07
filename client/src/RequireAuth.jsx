// src/RequireAuth.jsx
import React from 'react';
import { Navigate, useLocation, Outlet } from 'react-router-dom';

export default function RequireAuth() {
  const userId = localStorage.getItem('user_id');
  const location = useLocation();

  // 如果没有 user_id，就跳到登录页
  if (!userId) {
    return <Navigate to="/login" state={{ from: location }} replace />;
  }
  // 已登录，渲染子路由
  return <Outlet />;
}