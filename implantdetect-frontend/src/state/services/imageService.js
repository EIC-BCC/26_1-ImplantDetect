import axios from 'axios';

const token = localStorage.getItem('token');

const upload = async (item) => {
    try {
        const response = await axios.post(`/api/images/submit`, item,
            {
                headers: {
                    'Content-Type': 'multipart/form-data',
                    'Authorization': `${token}`
                }
            }
        );
        return response.data.data;
    } catch (error) {
        return Promise.reject(error.response?.data);
    }
};

const get = async (id) => {
    try {
        const response = await axios.get(`/api/images/${id}`);
        return response.data.data;
    } catch (error) {
        return Promise.reject(error.response?.data);
    }
};

const getProcessResults = async (process_id) => {
    try {
        const response = await axios.get(`/api/processing/${process_id}/results`, {
            headers: {
                'Authorization': `${token}`
            }
        });
        return response.data.data.results || [];
    } catch (error) {
        return Promise.reject(error.response?.data);
    }
};

const uploadService = {
    upload,
    get,
    getProcessResults
};

export default uploadService;