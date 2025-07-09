import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import UserService from '../services/userService';

let user = null;
let token = null;

try {

   const user = localStorage.getItem('user');
   const token = localStorage.getItem('token');

user = storedUser && storedUser !== 'undefined' ? JSON.parse(storedUser) : null;
    token = storedToken && storedToken !== 'undefined' ? storedToken : null;
} catch (e) {
    user = null;
    token = null;
}

export const register = createAsyncThunk('user/register', async (user) => {
    try {
        const response = await UserService.register(user);
        return response;
    }
    catch (error) {
        return Promise.reject(error);
    }
});

export const login = createAsyncThunk('user/login', async (user) => {
    try {
        const response = await UserService.login(user);
        return response;
    }
    catch (error) {
        return Promise.reject(error);
    }
});

export const logout = createAsyncThunk('user/logout', async () => {
    try {
        const response = await UserService.logout();
        return response;
    }
    catch (error) {
        return Promise.reject(error);
    }
});

const userSlice = createSlice({
    name: 'user',
    initialState: {
        user: user ? JSON.parse(user) : null,
        token: token ? token : null,
        status: 'idle',
        error: null
    },
    extraReducers: (builder) => {
        (builder)
            .addCase(register.pending, (state) => {
                state.status = 'loading';
                state.error = null;
            })
            .addCase(register.fulfilled, (state) => {
                state.status = 'success';
            })
            .addCase(register.rejected, (state, action) => {
                state.status = 'failed';
                state.error = action.payload;
            })
            .addCase(login.pending, (state) => {
                state.status = 'loading';
            })
            .addCase(login.fulfilled, (state, action) => {
                state.status = 'success';
                state.user = action.payload.user;
                state.token = action.payload.token;
            })
            .addCase(login.rejected, (state, action) => {
                state.status = 'failed';
                state.error = action.payload;
            })
            .addCase(logout.pending, (state) => {
                state.status = 'loading';
            })
            .addCase(logout.fulfilled, (state) => {
                state.status = 'success';
                state.user = null;
            })
            .addCase(logout.rejected, (state, action) => {
                state.status = 'failed';
                state.error = action.payload;
            });
    }
});

export default userSlice.reducer;