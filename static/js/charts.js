document.addEventListener("DOMContentLoaded", function () {

    // -----------------------------
    // Orders Last 7 Days (Line Chart)
    // -----------------------------
    const ordersCanvas = document.getElementById("ordersChart");

    if (ordersCanvas && window.ordersChartData) {
        const labels = window.ordersChartData.map(item => item.order_date);
        const values = window.ordersChartData.map(item => item.total_orders);

        const ctx = ordersCanvas.getContext('2d');
        const gradient = ctx.createLinearGradient(0, 0, 0, 300);
        gradient.addColorStop(0, 'rgba(245, 158, 11, 0.4)');
        gradient.addColorStop(1, 'rgba(245, 158, 11, 0.0)');

        new Chart(ordersCanvas, {
            type: 'line',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Orders Volume',
                    data: values,
                    borderColor: '#f59e0b',
                    backgroundColor: gradient,
                    borderWidth: 3,
                    pointBackgroundColor: '#f59e0b',
                    pointBorderColor: '#ffffff',
                    pointBorderWidth: 2,
                    pointRadius: 5,
                    tension: 0.4,
                    fill: true
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        labels: { color: '#94a3b8', font: { family: 'Plus Jakarta Sans', weight: 600 } }
                    }
                },
                scales: {
                    x: {
                        ticks: { color: '#94a3b8', font: { family: 'Plus Jakarta Sans' } },
                        grid: { color: 'rgba(255, 255, 255, 0.06)' }
                    },
                    y: {
                        ticks: { color: '#94a3b8', font: { family: 'Plus Jakarta Sans' }, precision: 0 },
                        grid: { color: 'rgba(255, 255, 255, 0.06)' }
                    }
                }
            }
        });
    }

    // -----------------------------
    // Status Distribution (Doughnut Chart)
    // -----------------------------
    const statusCanvas = document.getElementById("statusChart");

    if (statusCanvas && window.statusChartData) {
        const labels = window.statusChartData.map(item => item.status);
        const values = window.statusChartData.map(item => item.total);

        const colorMap = {
            'Pending': '#f59e0b',
            'Preparing': '#38bdf8',
            'Ready': '#34d399',
            'Completed': '#94a3b8',
            'Cancelled': '#fca5a5'
        };

        const bgColors = labels.map(l => colorMap[l] || '#818cf8');

        new Chart(statusCanvas, {
            type: 'doughnut',
            data: {
                labels: labels,
                datasets: [{
                    data: values,
                    backgroundColor: bgColors,
                    borderWidth: 2,
                    borderColor: '#1e293b'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: { color: '#94a3b8', font: { family: 'Plus Jakarta Sans', weight: 600 }, padding: 20 }
                    }
                },
                cutout: '70%'
            }
        });
    }

});