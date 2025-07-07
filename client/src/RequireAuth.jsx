// src/RequireAuth.jsx
import { Navigate, useLocation, Outlet } from 'react-router-dom';

export default function RequireAuth() {
  const token = localStorage.getItem('token');
  const location = useLocation();

  if (!token) {
    return <Navigate to="/login" state={{ from: location }} replace />;
  }
  return <Outlet />;
}