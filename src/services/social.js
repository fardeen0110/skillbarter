import api, { getApiBaseUrl, getToken } from "./auth";

function getErrorMessage(error, fallbackMessage) {
  return error.response?.data?.detail || fallbackMessage;
}

export async function fetchSocialOverview() {
  try {
    const { data } = await api.get("/friends");
    return data;
  } catch (error) {
    throw new Error(getErrorMessage(error, "Unable to load social overview"));
  }
}

export async function sendMatchRequest(receiverId) {
  try {
    const { data } = await api.post("/send-request", { receiver_id: receiverId });
    return data;
  } catch (error) {
    throw new Error(getErrorMessage(error, "Unable to send match request"));
  }
}

export async function acceptMatchRequest(requestId) {
  try {
    const { data } = await api.post("/accept-request", { request_id: requestId });
    return data;
  } catch (error) {
    throw new Error(getErrorMessage(error, "Unable to accept request"));
  }
}

export async function rejectMatchRequest(requestId) {
  try {
    const { data } = await api.post("/reject-request", { request_id: requestId });
    return data;
  } catch (error) {
    throw new Error(getErrorMessage(error, "Unable to reject request"));
  }
}

export async function fetchMessages(userId) {
  try {
    const { data } = await api.get(`/messages/${userId}`);
    return data;
  } catch (error) {
    throw new Error(getErrorMessage(error, "Unable to load messages"));
  }
}

export function getChatWebSocketUrl() {
  const token = getToken();
  const apiBaseUrl = getApiBaseUrl();
  const websocketBaseUrl = apiBaseUrl.replace(/^http/i, "ws");
  return `${websocketBaseUrl}/ws/chat?token=${encodeURIComponent(token || "")}`;
}
