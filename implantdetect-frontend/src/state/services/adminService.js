import api from "./api";

const getUsers = async () => {
  const response = await api.get("/admin/users");
  return response.data.data?.users || [];
};

const setUserRole = async (userId, role) => {
  const response = await api.patch(`/admin/users/${userId}/role`, { role });
  return response.data.data;
};

const setUserActive = async (userId, active) => {
  const response = await api.patch(`/admin/users/${userId}/active`, { active });
  return response.data.data;
};

const getProcesses = async () => {
  const response = await api.get("/admin/processes");
  return response.data.data?.processes || [];
};

const adminService = { getUsers, setUserRole, setUserActive, getProcesses };
export default adminService;
