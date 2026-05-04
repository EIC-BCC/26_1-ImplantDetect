import { useSelector } from 'react-redux';
import { Navigate, Outlet } from 'react-router-dom';

export const ProtectedRoute = () => {
  const token = useSelector((state) => state.user.token);
  if (!token) return <Navigate to="/login" replace />;
  return <Outlet />;
};

export const AdminRoute = () => {
  const token = useSelector((state) => state.user.token);
  const user = useSelector((state) => state.user.user);
  if (!token) return <Navigate to="/login" replace />;
  if (user?.role !== 'admin') return <Navigate to="/403" replace />;
  return <Outlet />;
};

export const GuestRoute = () => {
  const token = useSelector((state) => state.user.token);
  if (token) return <Navigate to="/home" replace />;
  return <Outlet />;
};
