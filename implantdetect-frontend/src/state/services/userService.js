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
        const response = await axios.post(`/api/users/login`, user);

        if (response.data) {
            const { token, user } = response.data;
            localStorage.setItem("token", token);
            localStorage.setItem("user", JSON.stringify(user));

            return response.data;
        }
    } catch (error) {
        return Promise.reject(error.response.data);
    }
}

const logout = async () => {
    try {
        localStorage.removeItem("token");
        localStorage.removeItem("user");
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