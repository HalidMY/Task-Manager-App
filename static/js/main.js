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
