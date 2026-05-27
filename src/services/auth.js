import axios from "axios";

const TOKEN_KEY = "skillbarter_token";
const USER_KEY = "skillbarter_user";
const API_BASE_URL = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";
const SESSION_EVENT = "skillbarter:session-changed";

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

function emitSessionChange() {
  if (!hasWindow()) {
    return;
  }
  window.dispatchEvent(new CustomEvent(SESSION_EVENT));
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
  emitSessionChange();
}

export function saveAccessToken(accessToken) {
  if (!hasWindow() || !accessToken) {
    return;
  }
  window.localStorage.setItem(TOKEN_KEY, accessToken);
  emitSessionChange();
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
  emitSessionChange();
}

export function subscribeToSessionChanges(listener) {
  if (!hasWindow()) {
    return () => {};
  }

  const handleCustomChange = () => listener();
  const handleStorage = (event) => {
    if (event.key === TOKEN_KEY || event.key === USER_KEY || event.key === null) {
      listener();
    }
  };

  window.addEventListener(SESSION_EVENT, handleCustomChange);
  window.addEventListener("storage", handleStorage);

  return () => {
    window.removeEventListener(SESSION_EVENT, handleCustomChange);
    window.removeEventListener("storage", handleStorage);
  };
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

export async function updateProfile(payload) {
  try {
    const { data } = await api.patch("/profile", payload);
    saveSession({ accessToken: getToken(), user: data });
    return data;
  } catch (error) {
    throw new Error(getErrorMessage(error, "Unable to update profile"));
  }
}

export async function uploadProfileAvatar(file) {
  try {
    const formData = new FormData();
    formData.append("avatar", file);
    const { data } = await api.post("/profile/avatar", formData, {
      headers: {
        "Content-Type": "multipart/form-data",
      },
    });
    saveSession({ accessToken: getToken(), user: data });
    return data;
  } catch (error) {
    throw new Error(getErrorMessage(error, "Unable to upload avatar"));
  }
}

export async function fetchDashboardSummary() {
  try {
    const { data } = await api.get("/dashboard/summary");
    return data;
  } catch (error) {
    throw new Error(getErrorMessage(error, "Unable to load dashboard summary"));
  }
}

export async function fetchNotifications() {
  try {
    const { data } = await api.get("/notifications");
    return data;
  } catch (error) {
    throw new Error(getErrorMessage(error, "Unable to load notifications"));
  }
}

export function getOAuthStartUrl(provider, nextPath = "/dashboard") {
  const baseUrl = getApiBaseUrl();
  const params = new URLSearchParams({ next_path: nextPath });
  return `${baseUrl}/oauth/${provider}/start?${params.toString()}`;
}

export default api;
