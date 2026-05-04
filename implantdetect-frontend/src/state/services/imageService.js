import api from './api';

const upload = async (formData) => {
  const response = await api.post('/images/submit', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });
  return response.data.data;
};

const get = async (id) => {
  const response = await api.get(`/images/${id}`);
  return response.data.data;
};

const getUserImages = async () => {
  const response = await api.get('/images/user');
  return response.data.data?.images || [];
};

const getProcessResults = async (processId) => {
  const response = await api.get(`/processing/${processId}/results`);
  return response.data.data?.results || [];
};

const getUserProcesses = async () => {
  const response = await api.get('/processing/user/processes');
  return response.data.data?.processes || [];
};

const getProcess = async (processId) => {
  const response = await api.get(`/processing/${processId}`);
  return response.data.data?.process;
};

const getImageBlob = async (filename) => {
  const response = await api.get(`/uploads/${filename}`, { responseType: 'blob' });
  return URL.createObjectURL(response.data);
};

const imageService = { upload, get, getUserImages, getProcessResults, getUserProcesses, getProcess, getImageBlob };
export default imageService;
