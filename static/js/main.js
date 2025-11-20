document.addEventListener("DOMContentLoaded", function () {
    const alerts = document.querySelectorAll(".flash-message");

    alerts.forEach(alert => {
        setTimeout(() => {
            alert.classList.add("fade-out");
        }, 1500);

        setTimeout(() => {
            alert.remove();
        }, 2300); 
    });
});

document.querySelectorAll(".task-card").forEach(card => {
    card.addEventListener("dragstart", e => {
        e.dataTransfer.setData("task_id", card.dataset.id);
    });
});

document.querySelectorAll(".kanban-column").forEach(column => {
    column.addEventListener("dragover", e => e.preventDefault());

    column.addEventListener("drop", e => {
        e.preventDefault();

        const task_id = e.dataTransfer.getData("task_id");
        const newStatus = column.dataset.status;

        fetch(`/task/update-status/${task_id}`, {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({ status: newStatus })
        })
        .then(res => res.json())
        .then(() => location.reload());
    });
});