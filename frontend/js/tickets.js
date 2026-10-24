
requireLogin();

const form = document.getElementById("filterForm");
const rows = document.getElementById("ticketRows");
const errorBox = document.getElementById("ticketError");

let page = 0;
const pageSize = 20;

document.getElementById("logoutLink").addEventListener("click", event => {
    event.preventDefault();
    logout();
});

form.addEventListener("submit", event => {
    event.preventDefault();
    page = 0;
    loadTickets();
});

document.getElementById("previousPage").addEventListener("click", () => {
    if (page > 0) {
        page--;
        loadTickets();
    }
});

document.getElementById("nextPage").addEventListener("click", () => {
    page++;
    loadTickets();
});

async function loadTickets() {
    errorBox.textContent = "";
    rows.replaceChildren();

    const params = new URLSearchParams({
        skip: String(page * pageSize),
        limit: String(pageSize),
    });

    const q = document.getElementById("search").value.trim();
    const status = document.getElementById("status").value;
    const priority = document.getElementById("priority").value;

    if (q) params.set("q", q);
    if (status) params.set("status", status);
    if (priority) params.set("priority", priority);

    try {
        const tickets = await apiRequest(
            `/api/tickets?${params.toString()}`
        );

        for (const ticket of tickets) {
            const row = document.createElement("tr");

            const values = [
                ticket.ticket_number || `#${ticket.id}`,
                ticket.title,
                ticket.priority,
                ticket.status,
                new Date(ticket.created_at).toLocaleString(),
            ];

            for (const value of values) {
                const cell = document.createElement("td");
                cell.textContent = value ?? "";
                row.appendChild(cell);
            }

            rows.appendChild(row);
        }

        document.getElementById("pageLabel").textContent =
            `Page ${page + 1}`;

        document.getElementById("previousPage").disabled = page === 0;
        document.getElementById("nextPage").disabled =
            tickets.length < pageSize;

        if (tickets.length === 0) {
            errorBox.textContent = "No tickets found.";
        }
    } catch (error) {
        errorBox.textContent = error.message;
    }
}

loadTickets();
