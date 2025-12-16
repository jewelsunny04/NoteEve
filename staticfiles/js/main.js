/* NoteEve Main JavaScript */

// Initialize on DOM ready
document.addEventListener('DOMContentLoaded', function() {

    // Initialize Bootstrap tooltips
    const tooltipTriggerList = [].slice.call(
        document.querySelectorAll('[data-bs-toggle="tooltip"]')
    );
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Initialize Bootstrap popovers
    const popoverTriggerList = [].slice.call(
        document.querySelectorAll('[data-bs-toggle="popover"]')
    );
    popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });

    // Auto-hide alerts after 5 seconds
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(function(alert) {
        setTimeout(function() {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 5000);
    });

});

// Toggle Bookmark
function toggleBookmark(noteId) {
    const csrf = document.querySelector('[name=csrfmiddlewaretoken]')?.value || '{{ csrf_token }}';

    fetch(`/bookmarks/toggle/${noteId}/`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': csrf,
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({})
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'added') {
            showNotification('Bookmark added!', 'success');
        } else {
            showNotification('Bookmark removed!', 'info');
        }
        location.reload();
    })
    .catch(error => {
        console.error('Error:', error);
        showNotification('Error toggling bookmark', 'danger');
    });
}

// Show Notification
function showNotification(message, type = 'info') {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
    alertDiv.role = 'alert';
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;

    const container = document.querySelector('.container');
    container.insertBefore(alertDiv, container.firstChild);

    setTimeout(function() {
        const bsAlert = new bootstrap.Alert(alertDiv);
        bsAlert.close();
    }, 3000);
}

// Format Date
function formatDate(date) {
    const options = { year: 'numeric', month: 'short', day: 'numeric' };
    return new Date(date).toLocaleDateString('en-US', options);
}

// Confirm Delete
function confirmDelete(message = 'Are you sure you want to delete this?') {
    return confirm(message);
}

// Copy to Clipboard
function copyToClipboard(text) {
    navigator.clipboard.writeText(text)
    .then(() => showNotification('Copied to clipboard!', 'success'))
    .catch(() => showNotification('Failed to copy', 'danger'));
}

// Enable Auto-save (placeholder)
function enableAutoSave(formId, interval = 30000) {
    const form = document.getElementById(formId);
    if (!form) return;

    setInterval(() => {
        console.log('Auto-saving form...');
    }, interval);
}

// Load Progress Chart
function loadProgressChart() {
    fetch('/api/progress/')
        .then(response => response.json())
        .then(data => {
            const ctx = document.getElementById('progressChart');
            if (!ctx) return;

            new Chart(ctx, {
                type: 'bar',
                data: {
                    labels: data.labels,
                    datasets: [{
                        label: 'Progress %',
                        data: data.data,
                        backgroundColor: 'rgba(75, 192, 192, 0.6)',
                        borderColor: 'rgba(75, 192, 192, 1)',
                        borderWidth: 2,
                        borderRadius: 5
                    }]
                },
                options: {
                    responsive: true,
                    plugins: {
                        legend: { display: true, position: 'top' },
                        title: { display: true, text: 'Your Progress' }
                    },
                    scales: {
                        y: {
                            beginAtZero: true,
                            max: 100,
                            ticks: {
                                callback: value => value + '%'
                            }
                        }
                    }
                }
            });
        })
        .catch(error => console.error('Error loading chart:', error));
}

// Debounce function
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        clearTimeout(timeout);
        timeout = setTimeout(() => func(...args), wait);
    };
}

// Search/Filter in Table
function filterTable(inputId, tableId) {
    const input = document.getElementById(inputId);
    const table = document.getElementById(tableId);
    if (!input || !table) return;

    input.addEventListener(
        'keyup',
        debounce(() => {
            const filter = input.value.toUpperCase();
            const rows = table.getElementsByTagName('tr');

            for (let row of rows) {
                const cells = row.getElementsByTagName('td');
                let visible = false;

                for (let cell of cells) {
                    if (cell.textContent.toUpperCase().includes(filter)) {
                        visible = true;
                        break;
                    }
                }

                row.style.display = visible ? '' : 'none';
            }
        }, 300)
    );
}

// Export table to CSV
function exportTableToCSV(filename, tableId) {
    const table = document.getElementById(tableId);
    if (!table) return;

    let csv = [];
    const rows = table.querySelectorAll('tr');

    rows.forEach(row => {
        const cols = row.querySelectorAll('td, th');
        const csvRow = [];

        cols.forEach(col => csvRow.push(`"${col.textContent}"`));
        csv.push(csvRow.join(','));
    });

    downloadCSV(csv.join('\n'), filename);
}

function downloadCSV(csv, filename) {
    const csvFile = new Blob([csv], { type: 'text/csv' });
    const link = document.createElement('a');
    link.href = URL.createObjectURL(csvFile);
    link.download = filename;
    link.click();
}

// Email validation
function isValidEmail(email) {
    const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return re.test(email);
}

// Show loading spinner
function showLoading(elementId) {
    const el = document.getElementById(elementId);
    if (el) el.innerHTML = '<div class="spinner-border" role="status"></div>';
}

// Hide loading spinner
function hideLoading(elementId) {
    const el = document.getElementById(elementId);
    if (el) el.innerHTML = '';
}

console.log('NoteEve JavaScript loaded successfully!');
