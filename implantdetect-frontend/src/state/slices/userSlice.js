import { createSlice, createAsyncThunk } from "@reduxjs/toolkit";
import UserService from "../services/userService";

const loadTokenFromLocalStorage = () => {
  try {
    const storedToken = localStorage.getItem("token");
    return storedToken && storedToken !== "undefined" ? storedToken : null;
  } catch (e) {
    console.error("Error parsing token from localStorage:", e);
    return null;
  }
};

const token = loadTokenFromLocalStorage();

export const register = createAsyncThunk("user/register", async (user) => {
  try {
    const response = await UserService.register(user);
    return response;
  } catch (error) {
    return Promise.reject(error);
  }
});

export const login = createAsyncThunk("user/login", async (user) => {
  try {
    const response = await UserService.login(user);
    return response;
  } catch (error) {
    return Promise.reject(error);
  }
});

export const logout = createAsyncThunk("user/logout", async () => {
  try {
    const response = await UserService.logout();
    return response;
  } catch (error) {
    return Promise.reject(error);
  }
});

const userSlice = createSlice({
  name: "user",
  initialState: {
    token: token,
    status: "idle",
    error: null,
  },
  extraReducers: (builder) => {
    builder
      .addCase(register.pending, (state) => {
        state.status = "loading";
        state.error = null;
      })
      .addCase(register.fulfilled, (state) => {
        state.status = "success";
      })
      .addCase(register.rejected, (state, action) => {
        state.status = "failed";
        state.error = action.error?.message || action.payload;
      })
      .addCase(login.pending, (state) => {
        state.status = "loading";
        state.error = null;
      })
      .addCase(login.fulfilled, (state, action) => {
        state.status = "success";
        const response = action.payload;
        // O backend retorna apenas o token, não o user
        state.user = { username: response.username || "" }; // ou null se não houver username
        state.token =
          response.token || response.access_token
            ? `${response.token_type || "Bearer"} ${response.access_token || response.token}`
            : null;
        localStorage.setItem("user", JSON.stringify(state.user));
        localStorage.setItem("token", state.token);
      })
      .addCase(login.rejected, (state, action) => {
        state.status = "failed";
        state.error = action.error?.message || action.payload;
      })
      .addCase(logout.pending, (state) => {
        state.status = "loading";
      })
      .addCase(logout.fulfilled, (state) => {
        state.status = "success";
        state.user = null;
        state.token = null;
        localStorage.removeItem("user");
        localStorage.removeItem("token");
      })
      .addCase(logout.rejected, (state, action) => {
        state.status = "failed";
        state.error = action.error?.message || action.payload;
      });
  },
});

export default userSlice.reducer;
