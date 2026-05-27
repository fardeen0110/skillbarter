import api from "./auth";

function getErrorMessage(error, fallbackMessage) {
  return error.response?.data?.detail || fallbackMessage;
}

export async function markNotificationAsRead(notificationId) {
  try {
    const { data } = await api.post(`/notifications/${notificationId}/read`);
    return data;
  } catch (error) {
    throw new Error(getErrorMessage(error, "Unable to update notification"));
  }
}

export async function fetchMarketplaceRequests({ query = "", status = "", skill = "", page = 1, pageSize = 9 } = {}) {
  try {
    const { data } = await api.get("/marketplace/requests", {
      params: {
        query,
        status,
        skill,
        page,
        page_size: pageSize,
      },
    });
    return data;
  } catch (error) {
    throw new Error(getErrorMessage(error, "Unable to load marketplace requests"));
  }
}

export async function createMarketplaceRequest(payload) {
  try {
    const { data } = await api.post("/marketplace/requests", payload);
    return data;
  } catch (error) {
    throw new Error(getErrorMessage(error, "Unable to create learning request"));
  }
}

export async function applyToMarketplaceRequest(requestId, payload) {
  try {
    const { data } = await api.post(`/marketplace/requests/${requestId}/apply`, payload);
    return data;
  } catch (error) {
    throw new Error(getErrorMessage(error, "Unable to apply to request"));
  }
}

export async function fetchAdminSummary() {
  try {
    const { data } = await api.get("/admin/summary");
    return data;
  } catch (error) {
    throw new Error(getErrorMessage(error, "Unable to load admin summary"));
  }
}

export async function fetchAdminUsers({ query = "", page = 1, pageSize = 20 } = {}) {
  try {
    const { data } = await api.get("/admin/users", {
      params: {
        query,
        page,
        page_size: pageSize,
      },
    });
    return data;
  } catch (error) {
    throw new Error(getErrorMessage(error, "Unable to load users"));
  }
}
