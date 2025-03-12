// Initialize all tooltips
document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Initialize popovers
    var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });

    // Add fade-in animation to cards
    document.querySelectorAll('.card').forEach(card => {
        card.classList.add('fade-in');
    });

    // Initialize DataTables
    $(document).ready(function() {
        if ($('.datatable').length) {
            $('.datatable').DataTable({
                pageLength: 10,
                responsive: true,
                dom: '<"row"<"col-sm-12 col-md-6"l><"col-sm-12 col-md-6"f>>' +
                     '<"row"<"col-sm-12"tr>>' +
                     '<"row"<"col-sm-12 col-md-5"i><"col-sm-12 col-md-7"p>>',
                language: {
                    search: "",
                    searchPlaceholder: "Search records..."
                }
            });
        }

        // Handle priority progress bars
        function initializePriorityBars() {
            document.querySelectorAll('.priority-progress').forEach(function(bar) {
                const score = bar.dataset.score;
                bar.style.setProperty('--priority-score', score + '%');
            });
        }

        // Initialize on page load
        initializePriorityBars();

        // Smart Search functionality
        $('.smart-search').on('input', function() {
            const query = $(this).val().toLowerCase();
            $('.datatable tbody tr').each(function() {
                const text = $(this).text().toLowerCase();
                $(this).toggle(text.includes(query));
            });
        });

        // Table action buttons
        $('.table-action-btn[data-action="delete"]').on('click', function(e) {
            e.preventDefault();
            const recordId = $(this).data('record-id');
            if (confirm('Are you sure you want to delete this record?')) {
                window.location.href = $(this).attr('href');
            }
        });
    });

    // Animate progress bars
    document.querySelectorAll('.progress-bar').forEach(bar => {
        const width = bar.style.width;
        bar.style.width = '0';
        setTimeout(() => {
            bar.style.width = width;
        }, 100);
    });

    // Add smooth scrolling to all links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth'
                });
            }
        });
    });

    // Smart Search Autocomplete
    const searchInput = document.querySelector('.smart-search');
    if (searchInput) {
        let typingTimer;
        const doneTypingInterval = 500;

        searchInput.addEventListener('keyup', () => {
            clearTimeout(typingTimer);
            if (searchInput.value) {
                typingTimer = setTimeout(performSmartSearch, doneTypingInterval);
            }
        });
    }

    // Dynamic Charts Update
    function updateCharts() {
        if (typeof Chart !== 'undefined' && window.dashboardCharts) {
            Object.values(window.dashboardCharts).forEach(chart => {
                chart.update();
            });
        }
    }

    // Real-time notifications
    function setupNotifications() {
        const notificationBell = document.querySelector('.notification-bell');
        if (notificationBell) {
            notificationBell.addEventListener('click', async () => {
                try {
                    const response = await fetch('/api/notifications/');
                    const notifications = await response.json();
                    updateNotificationDropdown(notifications);
                } catch (error) {
                    console.error('Error fetching notifications:', error);
                }
            });
        }
    }

    // Form validation enhancement
    document.querySelectorAll('form').forEach(form => {
        form.addEventListener('submit', function(event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
                highlightInvalidFields(form);
            }
            form.classList.add('was-validated');
        });
    });

    // Dynamic table row actions
    document.querySelectorAll('.table-action-btn').forEach(btn => {
        btn.addEventListener('click', async function(e) {
            e.preventDefault();
            const action = this.dataset.action;
            const recordId = this.dataset.recordId;
            
            try {
                const response = await fetch(`/api/records/${recordId}/${action}/`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': getCsrfToken()
                    }
                });
                
                if (response.ok) {
                    showToast('Success', 'Action completed successfully');
                    updateTableRow(recordId, action);
                } else {
                    showToast('Error', 'Failed to complete action', 'error');
                }
            } catch (error) {
                console.error('Error:', error);
                showToast('Error', 'An unexpected error occurred', 'error');
            }
        });
    });

    // Toast notification system
    function showToast(title, message, type = 'success') {
        const toastContainer = document.getElementById('toast-container');
        if (!toastContainer) {
            const container = document.createElement('div');
            container.id = 'toast-container';
            container.className = 'position-fixed bottom-0 end-0 p-3';
            document.body.appendChild(container);
        }

        const toast = document.createElement('div');
        toast.className = `toast align-items-center text-white bg-${type} border-0`;
        toast.setAttribute('role', 'alert');
        toast.setAttribute('aria-live', 'assertive');
        toast.setAttribute('aria-atomic', 'true');

        toast.innerHTML = `
            <div class="d-flex">
                <div class="toast-body">
                    <strong>${title}</strong><br>
                    ${message}
                </div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
            </div>
        `;

        document.getElementById('toast-container').appendChild(toast);
        const bsToast = new bootstrap.Toast(toast);
        bsToast.show();

        toast.addEventListener('hidden.bs.toast', () => {
            toast.remove();
        });
    };

    function showToast(message, type = 'success') {
        const toast = document.createElement('div');
        toast.className = `toast align-items-center text-white bg-${type} border-0`;
        toast.setAttribute('role', 'alert');
        toast.setAttribute('aria-live', 'assertive');
        toast.setAttribute('aria-atomic', 'true');
        
        toast.innerHTML = `
            <div class="d-flex">
                <div class="toast-body">
                    ${message}
                </div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
            </div>
        `;
        
        const container = document.querySelector('.toast-container') || document.body;
        container.appendChild(toast);
        
        const bsToast = new bootstrap.Toast(toast);
        bsToast.show();
        
        toast.addEventListener('hidden.bs.toast', function() {
            toast.remove();
        });
    }

    // Helper functions
    function getCsrfToken() {
        return document.querySelector('[name=csrfmiddlewaretoken]').value;
    }

    function highlightInvalidFields(form) {
        form.querySelectorAll(':invalid').forEach(input => {
            input.classList.add('highlight-invalid');
            input.addEventListener('input', function() {
                if (this.checkValidity()) {
                    this.classList.remove('highlight-invalid');
                }
            });
        });
    }

    function updateTableRow(recordId, action) {
        const row = document.querySelector(`tr[data-record-id="${recordId}"]`);
        if (row) {
            if (action === 'delete') {
                row.remove();
            } else {
                // Refresh row data
                fetch(`/api/records/${recordId}/`)
                    .then(response => response.json())
                    .then(data => updateRowContent(row, data));
            }
        }
    }

    // Initialize all components
    setupNotifications();
    updateCharts();
});

// Chart.js Configuration
window.chartColors = {
    primary: '#4a90e2',
    success: '#5cb85c',
    warning: '#f0ad4e',
    danger: '#d9534f',
    info: '#5bc0de'
};

// Initialize Dashboard Charts
function initializeDashboardCharts() {
    if (typeof Chart === 'undefined') return;

    window.dashboardCharts = {};

    // Customer Categories Chart
    const categoriesCtx = document.getElementById('customerCategoriesChart');
    if (categoriesCtx) {
        window.dashboardCharts.categories = new Chart(categoriesCtx, {
            type: 'doughnut',
            data: {
                labels: Object.keys(categoriesData),
                datasets: [{
                    data: Object.values(categoriesData),
                    backgroundColor: Object.values(window.chartColors)
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom'
                    }
                }
            }
        });
    }

    // Sentiment Trends Chart
    const sentimentCtx = document.getElementById('sentimentTrendsChart');
    if (sentimentCtx) {
        window.dashboardCharts.sentiment = new Chart(sentimentCtx, {
            type: 'line',
            data: {
                labels: sentimentLabels,
                datasets: [{
                    label: 'Average Sentiment',
                    data: sentimentData,
                    borderColor: window.chartColors.primary,
                    tension: 0.4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom'
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true
                    }
                }
            }
        });
    }
}
