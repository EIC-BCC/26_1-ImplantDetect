import axios from 'axios';

const register = async (user) => {
    try {
        const response = await axios.post(`/api/users/register`, user);
        return response.data;
    } catch (error) {
        return Promise.reject(error.response.data);
    }
};

const login = async (user) => {
    try {
        const formData = new FormData();
        formData.append("username", user.username);
        formData.append("password", user.password);

        const response = await axios.post(`/api/users/login`, formData, {
            headers: {
                "Content-Type": "multipart/form-data",
            },
        });

        if (response.data) {
            const { access_token, token_type } = response.data;
            const token = `${token_type} ${access_token}`;
            localStorage.setItem("token", token);

            return response.data;
        }
    } catch (error) {
        return Promise.reject(error?.response?.data || error.message);
    }
};

const logout = async () => {
    try {
        localStorage.removeItem("token");
    } catch (error) {
        return Promise.reject(error.response.data);
    }
}

const userService = {
    register,
    login,
    logout
};

export default userService;