import axios from 'axios';

const token = localStorage.getItem('token');

const upload = async (item) => {
    try {
        const response = await axios.post(`/api/images/upload`, item,
            {
                headers: {
                    'Content-Type': 'multipart/form-data',
                    'Authorization': `Bearer ${token}`
                }
            }
        );
        return response.data;
    } catch (error) {
        return Promise.reject(error.response.data);
    }
};

const get = async (id) => {
    try {
        const response = await axios.get(`/api/images/${id}`);
        return response.data;
    } catch (error) {
        return Promise.reject(error.response.data);
    }
}

const uploadService = {
    upload,
    get
};

export default uploadService;