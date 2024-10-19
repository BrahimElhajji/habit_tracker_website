document.addEventListener('DOMContentLoaded', function() {
    // Dark Mode Toggle
    const toggle = document.getElementById('darkModeToggle');
    const currentTheme = localStorage.getItem('theme') || 'light';
    setTheme(currentTheme);

    toggle.addEventListener('click', function(e) {
        e.preventDefault();
        const theme = document.documentElement.getAttribute('data-bs-theme') === 'light' ? 'dark' : 'light';
        setTheme(theme);
    });

    function setTheme(theme) {
        document.documentElement.setAttribute('data-bs-theme', theme);
        localStorage.setItem('theme', theme);
        updateToggleIcon(theme);
    }

    function updateToggleIcon(theme) {
        if (theme === 'dark') {
            toggle.innerHTML = '<i class="fa-solid fa-sun"></i> Light Mode';
        } else {
            toggle.innerHTML = '<i class="fa-solid fa-moon"></i> Dark Mode';
        }
    }

    // Initialize Theme on Page Load
    updateToggleIcon(currentTheme);

    // Initialize Toasts
    const toastContainer = document.getElementById('toast-container');

    // Function to show toast
    function showToast(message, category) {
        const toastEl = document.createElement('div');
        toastEl.className = `toast align-items-center text-bg-${category} border-0 animate__animated animate__fadeIn`;
        toastEl.setAttribute('role', 'alert');
        toastEl.setAttribute('aria-live', 'assertive');
        toastEl.setAttribute('aria-atomic', 'true');

        toastEl.innerHTML = `
            <div class="d-flex">
                <div class="toast-body">
                    ${message}
                </div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
            </div>
        `;

        toastContainer.appendChild(toastEl);
        const toast = new bootstrap.Toast(toastEl, { delay: 5000 });
        toast.show();

        // Remove toast from DOM after hidden
        toastEl.addEventListener('hidden.bs.toast', () => {
            toastEl.remove();
        });
    }

    // Expose showToast to global scope for inline scripts
    window.showToast = showToast;
});
