
const API_BASE = "http://127.0.0.1:8000";

async function apiRequest(path, options = {}) {
    const token = sessionStorage.getItem("itsm_token");

    const headers = {
        "Content-Type": "application/json",
        ...(token ? { Authorization: `Bearer ${token}` } : {}),
        ...options.headers,
    };

    const response = await fetch(`${API_BASE}${path}`, {
        ...options,
        headers,
    });

    if (response.status === 401) {
        sessionStorage.removeItem("itsm_token");
        window.location.href = "login.html";
        throw new Error("Your session has expired. Please log in again.");
    }

    const data = await response.json().catch(() => ({}));

    if (!response.ok) {
        const detail = data.detail;
        const message = Array.isArray(detail)
            ? detail.map(item => item.msg).join(", ")
            : detail || "Request failed";

        throw new Error(message);
    }

    return data;
}

function requireLogin() {
    if (!sessionStorage.getItem("itsm_token")) {
        window.location.href = "login.html";
    }
}

function logout() {
    sessionStorage.removeItem("itsm_token");
    window.location.href = "login.html";
}
