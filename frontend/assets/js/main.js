// Shared UI Logic (Navbar, Theme, Auth Check)

document.addEventListener('DOMContentLoaded', () => {
    initTheme();
    initNavbar();
});

// === THEME HANDLING ===
function initTheme() {
    const themeToggle = document.getElementById('themeToggle');
    const themeIcon = document.getElementById('themeIcon');
    const html = document.documentElement;

    const savedTheme = localStorage.getItem('theme') || 'dark';
    html.setAttribute('data-theme', savedTheme);
    updateIcon(savedTheme, themeIcon);

    if (themeToggle) {
        themeToggle.addEventListener('click', () => {
            const currentTheme = html.getAttribute('data-theme');
            const newTheme = currentTheme === 'dark' ? 'light' : 'dark';

            html.setAttribute('data-theme', newTheme);
            localStorage.setItem('theme', newTheme);
            updateIcon(newTheme, themeIcon);
        });
    }
}

function updateIcon(theme, icon) {
    if (!icon) return;
    if (theme === 'dark') {
        icon.classList.remove('fa-moon');
        icon.classList.add('fa-sun');
    } else {
        icon.classList.remove('fa-sun');
        icon.classList.add('fa-moon');
    }
}

// === NAVBAR AUTH STATE ===
function initNavbar() {
    const userRole = localStorage.getItem('userRole'); // 'owner' or 'customer'
    const username = localStorage.getItem('username');
    const isLoggedIn = !!username;

    const navLinks = document.getElementById('navLinks');
    if (!navLinks) return;

    let linksHtml = '';

    if (isLoggedIn) {
        if (userRole === 'owner') {
            linksHtml += `
                <li class="nav-item">
                    <a class="nav-link" href="owner-dashboard.html">
                        <i class="fas fa-chart-line me-1"></i>Dashboard
                    </a>
                </li>
            `;
        } else {
            linksHtml += `
                <li class="nav-item">
                    <a class="nav-link" href="explore.html">
                        <i class="fas fa-search me-1"></i>Explore
                    </a>
                </li>
            `;
        }
        linksHtml += `
            <li class="nav-item">
                <a class="btn btn-glass btn-sm px-3" href="#" onclick="logout()">
                    <i class="fas fa-sign-out-alt me-1"></i>Logout
                </a>
            </li>
        `;
    } else {
        linksHtml += `
            <li class="nav-item">
                <a class="nav-link" href="explore.html">Explore</a>
            </li>
            <li class="nav-item">
                <a class="btn btn-outline-neon btn-sm px-3" href="login.html">Login</a>
            </li>
        `;
    }

    // Add Theme Toggle button to the end
    linksHtml = `
        <li class="nav-item me-2">
            <button class="btn btn-glass btn-sm" id="themeToggleNav" title="Toggle Theme">
                <i class="fas fa-sun" id="themeIconNav"></i>
            </button>
        </li>
    ` + linksHtml;

    navLinks.innerHTML = linksHtml;

    // Re-bind theme toggle since we overwrote the HTML
    const newToggle = document.getElementById('themeToggleNav');
    const newIcon = document.getElementById('themeIconNav');
    if (newToggle) {
        // Initial icon state
        const currentTheme = document.documentElement.getAttribute('data-theme');
        updateIcon(currentTheme, newIcon);

        newToggle.addEventListener('click', () => {
            const theme = document.documentElement.getAttribute('data-theme');
            const newTheme = theme === 'dark' ? 'light' : 'dark';
            document.documentElement.setAttribute('data-theme', newTheme);
            localStorage.setItem('theme', newTheme);
            updateIcon(newTheme, newIcon);
        });
    }
}

// === AUTH UTILS ===
function logout() {
    localStorage.removeItem('username');
    localStorage.removeItem('userRole');
    localStorage.removeItem('isOwner');
    window.location.href = 'index.html';
}

function checkAuth() {
    if (!localStorage.getItem('username')) {
        window.location.href = 'login.html';
    }
}
