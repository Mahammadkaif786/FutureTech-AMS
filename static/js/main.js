// FutureTech Computer Institute - Main JavaScript Controls

document.addEventListener('DOMContentLoaded', function () {
    // 1. Initialize Theme Switcher (Dark/Light mode)
    initTheme();

    // 2. Initialize Password Show/Hide toggle
    initPasswordToggle();

    // 3. Initialize Student Form Auto-Calculations
    initStudentFormCalculations();

    // 4. Initialize Photo Upload Preview
    initPhotoPreview();

    // 5. Auto-Dismiss Alert Toasts
    initToasts();
});

// Theme Management
function initTheme() {
    const themeToggle = document.getElementById('theme-toggle');
    const savedTheme = localStorage.getItem('theme') || 'light';
    
    // Apply saved theme
    document.documentElement.setAttribute('data-theme', savedTheme);
    updateThemeIcon(savedTheme);
    
    if (themeToggle) {
        themeToggle.addEventListener('click', function () {
            const currentTheme = document.documentElement.getAttribute('data-theme');
            const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
            
            document.documentElement.setAttribute('data-theme', newTheme);
            localStorage.setItem('theme', newTheme);
            updateThemeIcon(newTheme);
            
            // Trigger chart update if on dashboard
            if (typeof window.updateChartsTheme === 'function') {
                window.updateChartsTheme(newTheme);
            }
        });
    }
}

function updateThemeIcon(theme) {
    const icon = document.querySelector('#theme-toggle i');
    if (icon) {
        if (theme === 'dark') {
            icon.className = 'bi bi-sun-fill';
        } else {
            icon.className = 'bi bi-moon-fill';
        }
    }
}

// Password Visiblity Toggle
function initPasswordToggle() {
    const toggleBtn = document.getElementById('toggle-password');
    const passwordInput = document.getElementById('password');
    
    if (toggleBtn && passwordInput) {
        toggleBtn.addEventListener('click', function () {
            const icon = toggleBtn.querySelector('i');
            if (passwordInput.type === 'password') {
                passwordInput.type = 'text';
                icon.className = 'bi bi-eye-fill';
            } else {
                passwordInput.type = 'password';
                icon.className = 'bi bi-eye-slash-fill';
            }
        });
    }
}

// Student Form Auto Calculations & Default Loaders
function initStudentFormCalculations() {
    const totalFeeInput = document.getElementById('total_fee');
    const discountInput = document.getElementById('discount');
    const paidAmountInput = document.getElementById('paid_amount');
    const pendingAmountInput = document.getElementById('pending_amount');
    const courseSelect = document.getElementById('course_id');
    const durationInput = document.getElementById('duration');

    // Trigger calculation
    function calculatePending() {
        if (!totalFeeInput || !pendingAmountInput) return;
        
        const total = parseFloat(totalFeeInput.value) || 0;
        const discount = parseFloat(discountInput ? discountInput.value : 0) || 0;
        const paid = parseFloat(paidAmountInput ? paidAmountInput.value : 0) || 0;
        
        // Validation: Paid cannot exceed total - discount
        const maxPaid = total - discount;
        if (paidAmountInput && paid > maxPaid) {
            paidAmountInput.value = maxPaid.toFixed(2);
            showToast('Warning', 'Paid amount cannot exceed the net fee (Total Fee - Discount).', 'warning');
        }
        
        const finalPaid = parseFloat(paidAmountInput ? paidAmountInput.value : 0) || 0;
        const pending = total - discount - finalPaid;
        
        pendingAmountInput.value = pending >= 0 ? pending.toFixed(2) : '0.00';
    }

    // Auto-fill course details on select
    if (courseSelect) {
        courseSelect.addEventListener('change', function () {
            const selectedOpt = courseSelect.options[courseSelect.selectedIndex];
            if (selectedOpt && selectedOpt.value) {
                const defaultFee = selectedOpt.getAttribute('data-fee');
                const defaultDuration = selectedOpt.getAttribute('data-duration');
                
                if (totalFeeInput && defaultFee) {
                    totalFeeInput.value = parseFloat(defaultFee).toFixed(2);
                }
                if (durationInput && defaultDuration) {
                    durationInput.value = defaultDuration;
                }
                calculatePending();
            }
        });
    }

    // Listeners for adjustments
    if (totalFeeInput) {
        totalFeeInput.addEventListener('input', calculatePending);
    }
    if (discountInput) {
        discountInput.addEventListener('input', calculatePending);
    }
    if (paidAmountInput) {
        paidAmountInput.addEventListener('input', calculatePending);
    }
}

// Uploaded Photo Real-time Preview
function initPhotoPreview() {
    const fileInput = document.getElementById('photo');
    const previewImg = document.getElementById('photo-preview');
    const placeholderIcon = document.getElementById('photo-upload-placeholder');
    
    if (fileInput) {
        fileInput.addEventListener('change', function () {
            const file = this.files[0];
            if (file) {
                // Client-side file type check
                const allowedTypes = ['image/jpeg', 'image/png', 'image/jpg'];
                if (!allowedTypes.includes(file.type)) {
                    showToast('Upload Error', 'Only JPG, JPEG, and PNG images are allowed!', 'danger');
                    this.value = ''; // Clear selection
                    return;
                }
                
                // Client-side file size check (2MB)
                const maxSize = 2 * 1024 * 1024;
                if (file.size > maxSize) {
                    showToast('Upload Error', 'File size must be less than 2MB!', 'danger');
                    this.value = ''; // Clear selection
                    return;
                }

                const reader = new FileReader();
                reader.onload = function (e) {
                    if (previewImg) {
                        previewImg.src = e.target.result;
                        previewImg.style.display = 'block';
                    }
                    if (placeholderIcon) {
                        placeholderIcon.style.display = 'none';
                    }
                }
                reader.readAsDataURL(file);
            }
        });
    }
}

// Bootstrap Toast System
function initToasts() {
    const toastElList = [].slice.call(document.querySelectorAll('.toast'));
    toastElList.map(function (toastEl) {
        return new bootstrap.Toast(toastEl, { delay: 5000 }).show();
    });
}

function showToast(title, message, type = 'info') {
    const container = document.querySelector('.toast-container');
    if (!container) return;
    
    const toastId = 'toast_' + Date.now();
    const typeClasses = {
        success: 'bg-success text-white',
        danger: 'bg-danger text-white',
        warning: 'bg-warning text-dark',
        info: 'bg-info text-white'
    };
    
    const toastHtml = `
        <div id="${toastId}" class="toast align-items-center ${typeClasses[type] || 'bg-primary text-white'} border-0" role="alert" aria-live="assertive" aria-atomic="true">
            <div class="d-flex">
                <div class="toast-body">
                    <strong>${title}:</strong> ${message}
                </div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
            </div>
        </div>
    `;
    
    container.insertAdjacentHTML('beforeend', toastHtml);
    const newToastEl = document.getElementById(toastId);
    const bsToast = new bootstrap.Toast(newToastEl, { delay: 5000 });
    bsToast.show();
    
    newToastEl.addEventListener('hidden.bs.toast', function () {
        newToastEl.remove();
    });
}
