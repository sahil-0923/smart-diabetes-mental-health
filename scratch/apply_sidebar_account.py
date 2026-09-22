import os
import re

sidebar_html = """<div class="sidebar-account-container">
    <button id="sidebarAccountBtn" class="user-profile-sidebar" aria-haspopup="true" aria-expanded="false" aria-label="User Account Profile" title="{{ user.name if user else 'Account' }}">
        <div class="avatar">{{ user.name[:2].upper() if user and user.name else 'PT' }}</div>
        <div class="user-info">
            <h4>{{ user.name if user else 'User' }}</h4>
            <p>{{ user.email if user and user.email else '' }}</p>
        </div>
        <svg class="sidebar-chevron" viewBox="0 0 24 24" width="14" height="14" fill="currentColor"><path d="M7.41 8.59L12 13.17l4.59-4.58L18 10l-6 6-6-6 1.41-1.41z"/></svg>
    </button>
    <div id="sidebarAccountDropdown" class="sidebar-account-dropdown" role="menu" aria-label="Sidebar Account options">
        <div class="account-dropdown-header">
            <div class="dropdown-avatar">{{ user.name[:2].upper() if user and user.name else 'PT' }}</div>
            <div class="dropdown-user-details">
                <div class="dropdown-user-name">{{ user.name if user and user.name else 'User' }}</div>
                <div class="dropdown-user-email">{{ user.email if user and user.email else '' }}</div>
            </div>
        </div>
        <div class="account-dropdown-divider"></div>
        <a href="/logout" class="account-dropdown-item" role="menuitem">
            <svg viewBox="0 0 24 24" width="16" height="16" fill="currentColor"><path d="M17 7l-1.41 1.41L18.17 11H8v2h10.17l-2.58 2.58L17 17l5-5zM4 5h8V3H4c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h8v-2H4V5z"/></svg>
            Logout
        </a>
    </div>
</div>"""

css_patch = """
        /* Sidebar Account Menu */
        .sidebar-account-container { position: relative; margin-top: auto; width: 100%; }
        .user-profile-sidebar { width: 100%; padding: 16px 20px; border-top: 1px solid var(--border); border-left: none; border-right: none; border-bottom: none; background: transparent; display: flex; align-items: center; gap: 12px; cursor: pointer; text-align: left; transition: background 0.15s ease; box-sizing: border-box; }
        .user-profile-sidebar:hover, .user-profile-sidebar:focus-visible { background: #f8fafc; }
        .user-profile-sidebar .avatar { width: 36px; height: 36px; background: var(--primary); color: #fff; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: 700; font-size: 13px; flex-shrink: 0; }
        .user-profile-sidebar .user-info { flex: 1; overflow: hidden; }
        .user-profile-sidebar .user-info h4 { font-size: 13px; font-weight: 700; color: var(--text-main); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; margin: 0; }
        .user-profile-sidebar .user-info p { font-size: 11px; color: var(--text-muted); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; margin: 2px 0 0 0; }
        .sidebar-chevron { color: var(--text-muted); transition: transform 0.15s ease; flex-shrink: 0; }
        .user-profile-sidebar[aria-expanded="true"] .sidebar-chevron { transform: rotate(180deg); }
        .sidebar-account-dropdown { display: none; position: absolute; bottom: calc(100% + 8px); left: 12px; right: 12px; background: #ffffff; border: 1px solid var(--border); border-radius: 10px; box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.15), 0 8px 10px -6px rgba(0, 0, 0, 0.08); z-index: 1000; overflow: hidden; animation: fadeInDropdown 0.15s ease-out; }
        .sidebar-account-dropdown.show { display: block; }
"""

js_unified = """
<script>
document.addEventListener("DOMContentLoaded", function() {
    // 1. Topbar Dropdown
    const topAvatarBtn = document.getElementById("accountAvatarBtn");
    const topDropdown = document.getElementById("accountDropdown");
    
    // 2. Sidebar Dropdown
    const sidebarBtn = document.getElementById("sidebarAccountBtn");
    const sidebarDropdown = document.getElementById("sidebarAccountDropdown");

    if (topAvatarBtn && topDropdown) {
        topAvatarBtn.addEventListener("click", function(e) {
            e.stopPropagation();
            if (sidebarDropdown) {
                sidebarDropdown.classList.remove("show");
                if (sidebarBtn) sidebarBtn.setAttribute("aria-expanded", "false");
            }
            const isOpen = topDropdown.classList.toggle("show");
            topAvatarBtn.setAttribute("aria-expanded", isOpen ? "true" : "false");
        });
    }

    if (sidebarBtn && sidebarDropdown) {
        sidebarBtn.addEventListener("click", function(e) {
            e.stopPropagation();
            if (topDropdown) {
                topDropdown.classList.remove("show");
                if (topAvatarBtn) topAvatarBtn.setAttribute("aria-expanded", "false");
            }
            const isOpen = sidebarDropdown.classList.toggle("show");
            sidebarBtn.setAttribute("aria-expanded", isOpen ? "true" : "false");
        });
    }

    document.addEventListener("click", function(e) {
        if (topAvatarBtn && topDropdown && !topAvatarBtn.contains(e.target) && !topDropdown.contains(e.target)) {
            topDropdown.classList.remove("show");
            topAvatarBtn.setAttribute("aria-expanded", "false");
        }
        if (sidebarBtn && sidebarDropdown && !sidebarBtn.contains(e.target) && !sidebarDropdown.contains(e.target)) {
            sidebarDropdown.classList.remove("show");
            sidebarBtn.setAttribute("aria-expanded", "false");
        }
    });

    document.addEventListener("keydown", function(e) {
        if (e.key === "Escape") {
            if (topDropdown) {
                topDropdown.classList.remove("show");
                if (topAvatarBtn) topAvatarBtn.setAttribute("aria-expanded", "false");
            }
            if (sidebarDropdown) {
                sidebarDropdown.classList.remove("show");
                if (sidebarBtn) sidebarBtn.setAttribute("aria-expanded", "false");
            }
        }
    });
});
</script>
"""

templates = [
    "templates/dashboard.html",
    "templates/glucose.html",
    "templates/monitoring.html",
    "templates/ai_forecast.html",
    "templates/simulator.html",
    "templates/risk_trends.html",
    "templates/health_trends.html",
    "templates/mental_wellness.html",
    "templates/forecast.html"
]

for tpath in templates:
    if not os.path.exists(tpath):
        continue
    with open(tpath, "r", encoding="utf-8") as f:
        content = f.read()

    # Replace the existing sidebar profile + logout block
    # Match from <div class="user-profile-sidebar"> (and optionally following <a ... logout-btn>) up to </aside>
    pattern = r'<div class="user-profile-sidebar">[\s\S]*?(?:<a[^>]*class="logout-btn"[^>]*>[\s\S]*?</a>\s*)?</aside>'
    if re.search(pattern, content):
        content = re.sub(pattern, sidebar_html + "\n</aside>", content)
    elif '<div class="sidebar-account-container">' not in content:
        # Fallback if pattern didn't match
        content = content.replace("</aside>", sidebar_html + "\n</aside>")

    # Add CSS patch
    if ".sidebar-account-container" not in content:
        if "</style>" in content:
            content = content.replace("</style>", css_patch + "\n    </style>")

    # Replace JS script block with unified handler
    # Remove previous script if injected
    content = re.sub(r'<script>\s*document\.addEventListener\("DOMContentLoaded",\s*function\(\)\s*\{[\s\S]*?accountAvatarBtn[\s\S]*?</script>', '', content)
    if "</body>" in content:
        content = content.replace("</body>", js_unified + "\n</body>")

    with open(tpath, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"Updated sidebar account in {tpath}")

print("All templates successfully updated with dynamic sidebar account popover!")
