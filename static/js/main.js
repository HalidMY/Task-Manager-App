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

function openEditModal(card) {
    const modalElement = document.getElementById("editTaskModal");
    const modal = bootstrap.Modal.getOrCreateInstance(modalElement);

    document.getElementById("edit-task-id").value = card.dataset.id;
    document.getElementById("edit-title").value = card.dataset.title;
    document.getElementById("edit-description").value = card.dataset.description;
    document.getElementById("edit-priority").value = card.dataset.priority;
    document.getElementById("edit-status").value = card.dataset.status;

    modal.show();
}



document.querySelectorAll(".task-card").forEach(card => {
    card.addEventListener("click", () => openEditModal(card));
});

document.getElementById("editTaskForm").addEventListener("submit", function(e){
    e.preventDefault();

    const id = document.getElementById("edit-task-id").value;

    fetch(`/task/update/${id}`, {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({
            title: document.getElementById("edit-title").value,
            description: document.getElementById("edit-description").value,
            priority: document.getElementById("edit-priority").value,
            status: document.getElementById("edit-status").value
        })
    }).then(() => location.reload());
});