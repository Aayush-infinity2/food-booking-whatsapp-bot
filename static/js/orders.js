document.addEventListener("DOMContentLoaded", function () {

    console.log("Orders JS Loaded");

    initializeSearch();

    initializeFilters();

    initializeResetButton();

});
function initializeSearch() {

    const searchInput = document.getElementById("searchInput");

    if (!searchInput) return;

    searchInput.addEventListener("keyup", function () {

        const keyword = this.value.toLowerCase();

        const rows = document.querySelectorAll("#ordersTable tbody tr");

        rows.forEach(row => {

            const text = row.innerText.toLowerCase();

            row.style.display = text.includes(keyword) ? "" : "none";

        });

    });

}
function initializeFilters() {

    const statusFilter = document.getElementById("statusFilter");

    const restaurantFilter = document.getElementById("restaurantFilter");

    if (!statusFilter || !restaurantFilter) return;

    statusFilter.addEventListener("change", filterTable);

    restaurantFilter.addEventListener("change", filterTable);

}
function filterTable() {

    const selectedStatus = document
        .getElementById("statusFilter")
        .value
        .toLowerCase();

    const selectedRestaurant = document
        .getElementById("restaurantFilter")
        .value
        .toLowerCase();

    const rows = document.querySelectorAll("#ordersTable tbody tr");

    rows.forEach(row => {

        const status = row.children[6].innerText.toLowerCase();

        const restaurant = row.children[2].innerText.toLowerCase();

        const statusMatch =
            !selectedStatus || status.includes(selectedStatus);

        const restaurantMatch =
            !selectedRestaurant || restaurant.includes(selectedRestaurant);

        row.style.display =
            statusMatch && restaurantMatch ? "" : "none";

    });

}
function initializeResetButton() {

    const resetBtn = document.getElementById("resetFilters");

    if (!resetBtn) return;

    resetBtn.addEventListener("click", function () {

        document.getElementById("searchInput").value = "";

        document.getElementById("statusFilter").value = "";

        document.getElementById("restaurantFilter").value = "";

        const rows = document.querySelectorAll("#ordersTable tbody tr");

        rows.forEach(row => {

            row.style.display = "";

        });

    });

}
document.addEventListener("click", function (event) {

    if (!event.target.closest(".update-btn")) return;

    const button = event.target.closest(".update-btn");

    const orderId = button.dataset.id;
    const status = button.dataset.status;

    document.getElementById("statusOrderId").value = orderId;
    document.getElementById("newStatus").value = status;

    const modal = new bootstrap.Modal(
        document.getElementById("statusModal")
    );

    modal.show();

});
document.addEventListener("click", function (event) {

    if (!event.target.closest(".delete-btn")) return;

    const button = event.target.closest(".delete-btn");

    const form = document.getElementById("deleteOrderForm");
    form.action = form.dataset.actionTemplate.replace(/0$/, button.dataset.id);

    const modal = new bootstrap.Modal(
        document.getElementById("deleteModal")
    );

    modal.show();

});

document.addEventListener("submit", function (event) {
    if (event.target.id !== "updateStatusForm") return;
    const form = event.target;
    const orderId = document.getElementById("statusOrderId").value;
    form.action = form.dataset.actionTemplate.replace(/0$/, orderId);
});
