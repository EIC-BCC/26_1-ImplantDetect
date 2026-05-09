import { useEffect, useState } from "react";
import { useDispatch, useSelector } from "react-redux";
import { Navigate, Outlet } from "react-router-dom";
import { verifySession } from "../../state/slices/userSlice";

const useSessionVerification = () => {
  const dispatch = useDispatch();
  const token = useSelector((state) => state.user.token);
  const [verified, setVerified] = useState(!token);

  useEffect(() => {
    if (!token) return;
    dispatch(verifySession()).finally(() => setVerified(true));
  }, [dispatch, token]);

  return { token, verified };
};

export const ProtectedRoute = () => {
  const { token, verified } = useSessionVerification();
  if (!verified) return null;
  if (!token) return <Navigate to="/login" replace />;
  return <Outlet />;
};

export const AdminRoute = () => {
  const { token, verified } = useSessionVerification();
  const user = useSelector((state) => state.user.user);
  if (!verified) return null;
  if (!token) return <Navigate to="/login" replace />;
  if (user?.role !== "admin") return <Navigate to="/403" replace />;
  return <Outlet />;
};

export const GuestRoute = () => {
  const token = useSelector((state) => state.user.token);
  if (token) return <Navigate to="/home" replace />;
  return <Outlet />;
};
