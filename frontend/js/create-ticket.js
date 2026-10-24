
requireLogin();

document.getElementById("logoutLink").addEventListener("click", event => {
    event.preventDefault();
    logout();
});

document.getElementById("createTicketForm").addEventListener(
    "submit", async event => {
        event.preventDefault();

        const error = document.getElementById("createError");
        const success = document.getElementById("createSuccess");
        error.textContent = "";
        success.textContent = "";

        const payload = {
            title: document.getElementById("title").value.trim(),
            type: document.getElementById("type").value,
            category: document.getElementById("category").value,
            priority: document.getElementById("priority").value,
            description:
                document.getElementById("description").value.trim(),
        };

        try {
            const ticket = await apiRequest("/api/tickets", {
                method: "POST",
                body: JSON.stringify(payload),
            });

            success.textContent =
                `Ticket ${ticket.ticket_number} created successfully.`;

            event.target.reset();
        } catch (err) {
            error.textContent = err.message;
        }
    }
);
