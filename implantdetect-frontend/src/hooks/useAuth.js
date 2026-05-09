import { useSelector } from "react-redux";

const useAuth = () => {
  const token = useSelector((state) => state.user.token);
  const user = useSelector((state) => state.user.user);
  const status = useSelector((state) => state.user.status);

  return {
    isAuthenticated: !!token,
    user,
    token,
    status,
    isAdmin: user?.role === "admin",
    isSpecialist: user?.role === "specialist" || user?.role === "admin",
    isUser: !!token,
  };
};

export default useAuth;
