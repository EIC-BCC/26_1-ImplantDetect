import { createSlice, createAsyncThunk } from "@reduxjs/toolkit";
import UserService from "../services/userService";

const loadFromLocalStorage = (key) => {
  try {
    const stored = localStorage.getItem(key);
    if (!stored || stored === "undefined") return null;
    try {
      return JSON.parse(stored);
    } catch {
      return stored;
    }
  } catch {
    return null;
  }
};

const initialToken = loadFromLocalStorage("token");
const initialUser = loadFromLocalStorage("user");

export const register = createAsyncThunk(
  "user/register",
  async (user, { rejectWithValue }) => {
    try {
      return await UserService.register(user);
    } catch (error) {
      return rejectWithValue(
        error?.message || error?.detail || "Erro ao registrar",
      );
    }
  },
);

export const login = createAsyncThunk(
  "user/login",
  async (user, { rejectWithValue }) => {
    try {
      return await UserService.login(user);
    } catch (error) {
      return rejectWithValue(error?.detail || "Credenciais inválidas");
    }
  },
);

export const logout = createAsyncThunk("user/logout", async () => {
  await UserService.logout();
});

export const verifySession = createAsyncThunk(
  "user/verifySession",
  async (_, { rejectWithValue }) => {
    try {
      return await UserService.getMe();
    } catch (error) {
      return rejectWithValue(error?.detail || "Sessão inválida");
    }
  },
);

export const fetchUser = createAsyncThunk(
  "user/fetch",
  async (userId, { rejectWithValue }) => {
    try {
      return await UserService.getUser(userId);
    } catch (error) {
      return rejectWithValue(error?.detail || "Erro ao buscar usuário");
    }
  },
);

export const updateUser = createAsyncThunk(
  "user/update",
  async (userData, { rejectWithValue }) => {
    try {
      return await UserService.updateUser(userData);
    } catch (error) {
      return rejectWithValue(error?.detail || "Erro ao atualizar usuário");
    }
  },
);

const userSlice = createSlice({
  name: "user",
  initialState: {
    user: initialUser,
    token: initialToken,
    status: "idle",
    error: null,
  },
  reducers: {
    clearError: (state) => {
      state.error = null;
    },
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
        state.error = action.payload;
      })
      .addCase(login.pending, (state) => {
        state.status = "loading";
        state.error = null;
      })
      .addCase(login.fulfilled, (state, action) => {
        state.status = "success";
        const response = action.payload;
        const token = response.access_token
          ? `${response.token_type || "Bearer"} ${response.access_token}`
          : null;
        state.token = token;
        state.user = {
          username: response.username || "",
          user_id: response.user_id ?? null,
          role: response.role || "user",
        };
        localStorage.setItem("user", JSON.stringify(state.user));
        localStorage.setItem("token", token);
      })
      .addCase(login.rejected, (state, action) => {
        state.status = "failed";
        state.error = action.payload;
      })
      .addCase(logout.fulfilled, (state) => {
        state.status = "idle";
        state.user = null;
        state.token = null;
        state.error = null;
      })
      .addCase(verifySession.fulfilled, (state, action) => {
        state.user = { ...state.user, ...action.payload };
        localStorage.setItem("user", JSON.stringify(state.user));
      })
      .addCase(verifySession.rejected, (state) => {
        state.user = null;
        state.token = null;
        localStorage.removeItem("user");
        localStorage.removeItem("token");
      })
      .addCase(fetchUser.fulfilled, (state, action) => {
        state.user = { ...state.user, ...action.payload };
        localStorage.setItem("user", JSON.stringify(state.user));
      })
      .addCase(updateUser.pending, (state) => {
        state.status = "loading";
      })
      .addCase(updateUser.fulfilled, (state, action) => {
        state.status = "success";
        state.user = { ...state.user, ...action.payload };
        localStorage.setItem("user", JSON.stringify(state.user));
      })
      .addCase(updateUser.rejected, (state, action) => {
        state.status = "failed";
        state.error = action.payload;
      });
  },
});

export const { clearError } = userSlice.actions;
export default userSlice.reducer;
