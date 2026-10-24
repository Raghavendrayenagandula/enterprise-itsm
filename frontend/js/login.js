
const loginForm = document.getElementById("loginForm");
const errorMessage = document.getElementById("errorMessage");

loginForm.addEventListener("submit", async (event) => {
    event.preventDefault();
    errorMessage.textContent = "";

    const email = document.getElementById("email").value.trim();
    const password = document.getElementById("password").value;

    try {
        const result = await apiRequest("/api/auth/login", {
            method: "POST",
            body: JSON.stringify({ email, password }),
        });

        sessionStorage.setItem("itsm_token", result.access_token);
        window.location.href = "dashboard.html";
    } catch (error) {
        errorMessage.textContent = error.message;
    }
});
