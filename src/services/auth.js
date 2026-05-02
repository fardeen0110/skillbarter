import axios from "axios";

const TOKEN_KEY = "skillbarter_token";
const USER_KEY = "skillbarter_user";
const API_BASE_URL = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    "Content-Type": "application/json",
  },
});

api.interceptors.request.use((config) => {
  const token = getToken();

  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }

  return config;
});

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      clearSession();
    }

    return Promise.reject(error);
  },
);

function getErrorMessage(error, fallbackMessage) {
  return error.response?.data?.detail || fallbackMessage;
}

function hasWindow() {
  return typeof window !== "undefined";
}

export function getToken() {
  return hasWindow() ? window.localStorage.getItem(TOKEN_KEY) : null;
}

export function getApiBaseUrl() {
  return API_BASE_URL;
}

export function hasStoredToken() {
  return Boolean(getToken());
}

export function saveSession({ accessToken, user }) {
  if (!hasWindow()) {
    return;
  }

  if (accessToken) {
    window.localStorage.setItem(TOKEN_KEY, accessToken);
  }
  window.localStorage.setItem(USER_KEY, JSON.stringify(user));
}

export function getStoredUser() {
  if (!hasWindow()) {
    return null;
  }

  const serializedUser = window.localStorage.getItem(USER_KEY);
  if (!serializedUser) {
    return null;
  }

  try {
    return JSON.parse(serializedUser);
  } catch {
    clearSession();
    return null;
  }
}

export function clearSession() {
  if (!hasWindow()) {
    return;
  }

  window.localStorage.removeItem(TOKEN_KEY);
  window.localStorage.removeItem(USER_KEY);
}

export async function loginUser(credentials) {
  try {
    const { data } = await api.post("/login", credentials);
    saveSession({ accessToken: data.access_token, user: data.user });
    return data;
  } catch (error) {
    clearSession();
    throw new Error(getErrorMessage(error, "Login failed"));
  }
}

export async function registerUser(payload) {
  try {
    const { data } = await api.post("/register", payload);
    return data;
  } catch (error) {
    throw new Error(getErrorMessage(error, "Registration failed"));
  }
}

export async function fetchCurrentUser() {
  try {
    const { data } = await api.get("/me");
    saveSession({ accessToken: getToken(), user: data });
    return data;
  } catch (error) {
    throw new Error(getErrorMessage(error, "Unable to fetch account details"));
  }
}

export async function fetchMatchmakingSkills() {
  try {
    const { data } = await api.get("/matchmaking/skills");
    return data.skills;
  } catch (error) {
    throw new Error(getErrorMessage(error, "Unable to load skills"));
  }
}

export async function requestMatches(payload) {
  try {
    const { data } = await api.post("/matchmaking", payload);
    return data.matches;
  } catch (error) {
    throw new Error(getErrorMessage(error, "Unable to fetch matches"));
  }
}

export default api;
