function openCreateTaskModal() {
    const modalElement = document.getElementById("createTaskModal");
    const modal = bootstrap.Modal.getOrCreateInstance(modalElement);
    modal.show();
}
