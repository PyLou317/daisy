// Main JavaScript for StaffingPro

document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Auto-hide alerts after 5 seconds
    const alerts = document.querySelectorAll('.alert:not(.alert-permanent)');
    alerts.forEach(function(alert) {
        setTimeout(function() {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 5000);
    });

    // Confirm deletion actions
    const deleteButtons = document.querySelectorAll('[data-confirm]');
    deleteButtons.forEach(function(button) {
        button.addEventListener('click', function(e) {
            const message = this.getAttribute('data-confirm') || 'Are you sure?';
            if (!confirm(message)) {
                e.preventDefault();
                return false;
            }
        });
    });

    // Form validation enhancements
    const forms = document.querySelectorAll('form[data-validate]');
    forms.forEach(function(form) {
        form.addEventListener('submit', function(e) {
            if (!form.checkValidity()) {
                e.preventDefault();
                e.stopPropagation();
            }
            form.classList.add('was-validated');
        });
    });

    // Auto-resize textareas
    const textareas = document.querySelectorAll('textarea[data-auto-resize]');
    textareas.forEach(function(textarea) {
        function resize() {
            textarea.style.height = 'auto';
            textarea.style.height = textarea.scrollHeight + 'px';
        }
        
        textarea.addEventListener('input', resize);
        resize(); // Initial resize
    });

    // Search form enhancements
    const searchForms = document.querySelectorAll('form[data-search]');
    searchForms.forEach(function(form) {
        const searchInput = form.querySelector('input[name="search"]');
        if (searchInput) {
            let timeout;
            searchInput.addEventListener('input', function() {
                clearTimeout(timeout);
                timeout = setTimeout(function() {
                    if (searchInput.value.length >= 3 || searchInput.value.length === 0) {
                        form.submit();
                    }
                }, 500);
            });
        }
    });

    // Loading state for forms
    const submitForms = document.querySelectorAll('form[data-loading]');
    submitForms.forEach(function(form) {
        form.addEventListener('submit', function() {
            const submitButton = form.querySelector('button[type="submit"]');
            if (submitButton) {
                const originalText = submitButton.innerHTML;
                submitButton.disabled = true;
                submitButton.innerHTML = '<i data-feather="loader" class="spinner me-1"></i>Processing...';
                
                // Re-initialize feather icons
                feather.replace();
                
                // Re-enable after 10 seconds as fallback
                setTimeout(function() {
                    submitButton.disabled = false;
                    submitButton.innerHTML = originalText;
                    feather.replace();
                }, 10000);
            }
        });
    });

    // Dynamic table sorting (if needed)
    const sortableHeaders = document.querySelectorAll('th[data-sort]');
    sortableHeaders.forEach(function(header) {
        header.style.cursor = 'pointer';
        header.addEventListener('click', function() {
            const column = this.getAttribute('data-sort');
            const currentUrl = new URL(window.location);
            const currentSort = currentUrl.searchParams.get('sort');
            const currentOrder = currentUrl.searchParams.get('order');
            
            let newOrder = 'asc';
            if (currentSort === column && currentOrder === 'asc') {
                newOrder = 'desc';
            }
            
            currentUrl.searchParams.set('sort', column);
            currentUrl.searchParams.set('order', newOrder);
            window.location.href = currentUrl.toString();
        });
    });

    // File upload drag and drop
    const fileInputs = document.querySelectorAll('input[type="file"]');
    fileInputs.forEach(function(input) {
        const parent = input.closest('.mb-3') || input.parentElement;
        
        parent.addEventListener('dragover', function(e) {
            e.preventDefault();
            this.classList.add('drag-over');
        });
        
        parent.addEventListener('dragleave', function(e) {
            e.preventDefault();
            this.classList.remove('drag-over');
        });
        
        parent.addEventListener('drop', function(e) {
            e.preventDefault();
            this.classList.remove('drag-over');
            
            const files = e.dataTransfer.files;
            if (files.length > 0) {
                input.files = files;
                
                // Trigger change event
                const event = new Event('change', { bubbles: true });
                input.dispatchEvent(event);
            }
        });
    });

    // Client-side CSV preview (optional enhancement)
    const csvInputs = document.querySelectorAll('input[type="file"][accept*="csv"]');
    csvInputs.forEach(function(input) {
        input.addEventListener('change', function(e) {
            const file = e.target.files[0];
            if (file && file.type === 'text/csv') {
                const reader = new FileReader();
                reader.onload = function(e) {
                    const csv = e.target.result;
                    const lines = csv.split('\n');
                    const headers = lines[0].split(',');
                    
                    // Show preview if there's a preview container
                    const previewContainer = document.getElementById('csv-preview');
                    if (previewContainer && lines.length > 1) {
                        let previewHtml = '<h6>CSV Preview (first 5 rows):</h6>';
                        previewHtml += '<div class="table-responsive"><table class="table table-sm">';
                        previewHtml += '<thead><tr>';
                        headers.forEach(header => {
                            previewHtml += `<th>${header.trim()}</th>`;
                        });
                        previewHtml += '</tr></thead><tbody>';
                        
                        for (let i = 1; i < Math.min(6, lines.length); i++) {
                            if (lines[i].trim()) {
                                const cells = lines[i].split(',');
                                previewHtml += '<tr>';
                                cells.forEach(cell => {
                                    previewHtml += `<td>${cell.trim()}</td>`;
                                });
                                previewHtml += '</tr>';
                            }
                        }
                        
                        previewHtml += '</tbody></table></div>';
                        previewContainer.innerHTML = previewHtml;
                        previewContainer.style.display = 'block';
                    }
                };
                reader.readAsText(file);
            }
        });
    });

    // Auto-refresh for dashboard (every 5 minutes)
    if (window.location.pathname === '/' || window.location.pathname.includes('/dashboard')) {
        setInterval(function() {
            // Only refresh if the page is visible
            if (!document.hidden) {
                const refreshIndicator = document.createElement('div');
                refreshIndicator.className = 'position-fixed top-0 end-0 m-3 alert alert-info alert-sm';
                refreshIndicator.innerHTML = '<i data-feather="refresh-cw" class="spinner me-1"></i>Updating...';
                refreshIndicator.style.zIndex = '9999';
                document.body.appendChild(refreshIndicator);
                
                // Refresh the page
                setTimeout(() => window.location.reload(), 1000);
            }
        }, 300000); // 5 minutes
    }

    // Add keyboard shortcuts
    document.addEventListener('keydown', function(e) {
        // Ctrl/Cmd + K for quick search
        if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
            e.preventDefault();
            const searchInput = document.querySelector('input[name="search"]');
            if (searchInput) {
                searchInput.focus();
                searchInput.select();
            }
        }
        
        // Escape to close modals/cancel forms
        if (e.key === 'Escape') {
            const activeModal = document.querySelector('.modal.show');
            if (activeModal) {
                const modal = bootstrap.Modal.getInstance(activeModal);
                if (modal) modal.hide();
            }
        }
    });

    // Initialize any progress bars
    const progressBars = document.querySelectorAll('.progress-bar[data-animate]');
    progressBars.forEach(function(bar) {
        const width = bar.style.width || bar.getAttribute('data-width');
        bar.style.width = '0%';
        setTimeout(function() {
            bar.style.transition = 'width 1s ease-in-out';
            bar.style.width = width;
        }, 100);
    });

    console.log('StaffingPro JavaScript initialized');
});

// Utility functions
window.StaffingPro = {
    // Show loading state
    showLoading: function(element, text = 'Loading...') {
        if (typeof element === 'string') {
            element = document.querySelector(element);
        }
        if (element) {
            element.disabled = true;
            element.innerHTML = `<i data-feather="loader" class="spinner me-1"></i>${text}`;
            feather.replace();
        }
    },
    
    // Hide loading state
    hideLoading: function(element, originalText) {
        if (typeof element === 'string') {
            element = document.querySelector(element);
        }
        if (element) {
            element.disabled = false;
            element.innerHTML = originalText;
            feather.replace();
        }
    },
    
    // Show toast notification
    showToast: function(message, type = 'info') {
        const toast = document.createElement('div');
        toast.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
        toast.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px;';
        toast.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        document.body.appendChild(toast);
        
        setTimeout(() => {
            toast.remove();
        }, 5000);
    },
    
    // Format currency
    formatCurrency: function(amount) {
        return new Intl.NumberFormat('en-US', {
            style: 'currency',
            currency: 'USD'
        }).format(amount);
    },
    
    // Format date
    formatDate: function(date) {
        return new Intl.DateTimeFormat('en-US').format(new Date(date));
    }
};
