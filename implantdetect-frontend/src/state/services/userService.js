import api from './api';

const register = async (user) => {
  const response = await api.post('/users/register', user);
  return response.data;
};

const login = async (user) => {
  const formData = new FormData();
  formData.append('username', user.username);
  formData.append('password', user.password);
  const response = await api.post('/users/login', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });
  if (response.data) {
    const { access_token, token_type } = response.data;
    const token = `${token_type} ${access_token}`;
    localStorage.setItem('token', token);
    return response.data;
  }
};

const logout = async () => {
  localStorage.removeItem('token');
  localStorage.removeItem('user');
};

const getUser = async (userId) => {
  const response = await api.get(`/users/get/${userId}`);
  return response.data.data;
};

const updateUser = async (userData) => {
  const response = await api.post('/users/update', userData);
  return response.data.data;
};

const userService = { register, login, logout, getUser, updateUser };
export default userService;