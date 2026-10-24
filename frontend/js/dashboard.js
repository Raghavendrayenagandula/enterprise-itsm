
requireLogin();

document.getElementById("logoutLink").addEventListener("click", event => {
    event.preventDefault();
    logout();
});

async function loadDashboard() {
    try {
        const data = await apiRequest("/api/dashboard");

        document.getElementById("totalTickets").textContent =
            data.total_tickets;
        document.getElementById("openTickets").textContent =
            data.open_tickets;
        document.getElementById("criticalTickets").textContent =
            data.critical_tickets;

        const list = document.getElementById("statusList");
        list.replaceChildren();

        for (const [status, count] of Object.entries(data.tickets_by_status)) {
            const row = document.createElement("p");
            row.textContent = `${status}: ${count}`;
            list.appendChild(row);
        }

        if (!Object.keys(data.tickets_by_status).length) {
            list.textContent = "No tickets have been created yet.";
        }
    } catch (error) {
        document.getElementById("dashboardError").textContent =
            error.message;
    }
}

loadDashboard();
