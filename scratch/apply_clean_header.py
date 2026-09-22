import os
import re

css_addition = """
        /* Topbar & Account Menu */
        .topbar { height: 64px; background: #fff; border-bottom: 1px solid var(--border); display: flex; align-items: center; padding: 0 32px; justify-content: flex-end; flex-shrink: 0; }
        .account-menu-container { position: relative; display: flex; align-items: center; }
        .top-avatar { width: 36px; height: 36px; background: var(--primary); color: #fff; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: 600; font-size: 13px; border: none; cursor: pointer; transition: transform 0.15s ease, box-shadow 0.15s ease; outline: none; }
        .top-avatar:hover, .top-avatar:focus-visible { transform: scale(1.05); box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.25); }
        .account-dropdown { display: none; position: absolute; top: calc(100% + 8px); right: 0; width: 240px; background: #ffffff; border: 1px solid var(--border); border-radius: 10px; box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.1), 0 8px 10px -6px rgba(0, 0, 0, 0.05); z-index: 1000; overflow: hidden; animation: fadeInDropdown 0.15s ease-out; }
        .account-dropdown.show { display: block; }
        .account-dropdown-header { padding: 14px 16px; display: flex; align-items: center; gap: 12px; background: #f8fafc; }
        .dropdown-avatar { width: 36px; height: 36px; background: var(--primary); color: #fff; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: 700; font-size: 13px; flex-shrink: 0; }
        .dropdown-user-details { overflow: hidden; }
        .dropdown-user-name { font-size: 13px; font-weight: 700; color: var(--text-main); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
        .dropdown-user-email { font-size: 11px; color: var(--text-muted); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; margin-top: 2px; }
        .account-dropdown-divider { height: 1px; background: var(--border); }
        .account-dropdown-item { display: flex; align-items: center; gap: 8px; padding: 12px 16px; color: #dc2626; font-size: 13px; font-weight: 600; text-decoration: none; transition: background 0.15s ease; width: 100%; border: none; background: transparent; cursor: pointer; text-align: left; box-sizing: border-box; }
        .account-dropdown-item:hover, .account-dropdown-item:focus-visible { background: #fef2f2; }
        @keyframes fadeInDropdown { from { opacity: 0; transform: translateY(-4px); } to { opacity: 1; transform: translateY(0); } }
"""

header_html = """<header class="topbar">
<div class="account-menu-container">
    <button id="accountAvatarBtn" class="top-avatar" aria-haspopup="true" aria-expanded="false" aria-label="User Account Menu" title="{{ user.name if user else 'Account' }}">
        {{ user.name[:2].upper() if user and user.name else "PT" }}
    </button>
    <div id="accountDropdown" class="account-dropdown" role="menu" aria-label="Account options">
        <div class="account-dropdown-header">
            <div class="dropdown-avatar">{{ user.name[:2].upper() if user and user.name else "PT" }}</div>
            <div class="dropdown-user-details">
                <div class="dropdown-user-name">{{ user.name if user and user.name else "User" }}</div>
                <div class="dropdown-user-email">{{ user.email if user and user.email else "" }}</div>
            </div>
        </div>
        <div class="account-dropdown-divider"></div>
        <a href="/logout" class="account-dropdown-item" role="menuitem">
            <svg viewBox="0 0 24 24" width="16" height="16" fill="currentColor"><path d="M17 7l-1.41 1.41L18.17 11H8v2h10.17l-2.58 2.58L17 17l5-5zM4 5h8V3H4c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h8v-2H4V5z"/></svg>
            Logout
        </a>
    </div>
</div>
</header>"""

js_addition = """
<script>
document.addEventListener("DOMContentLoaded", function() {
    const avatarBtn = document.getElementById("accountAvatarBtn");
    const dropdown = document.getElementById("accountDropdown");
    if (avatarBtn && dropdown) {
        avatarBtn.addEventListener("click", function(e) {
            e.stopPropagation();
            const isOpen = dropdown.classList.toggle("show");
            avatarBtn.setAttribute("aria-expanded", isOpen ? "true" : "false");
        });
        document.addEventListener("click", function(e) {
            if (!avatarBtn.contains(e.target) && !dropdown.contains(e.target)) {
                dropdown.classList.remove("show");
                avatarBtn.setAttribute("aria-expanded", "false");
            }
        });
        document.addEventListener("keydown", function(e) {
            if (e.key === "Escape") {
                dropdown.classList.remove("show");
                avatarBtn.setAttribute("aria-expanded", "false");
            }
        });
    }
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

    # 1. Replace topbar block
    # Match <header class="topbar"> ... </header>
    content = re.sub(
        r'<header class="topbar">[\s\S]*?</header>',
        header_html,
        content
    )

    # 2. Add CSS if not already present
    if ".account-menu-container" not in content:
        if "</style>" in content:
            content = content.replace("</style>", css_addition + "\n    </style>")

    # 3. Add JS if not already present
    if "accountAvatarBtn" not in content or "accountDropdown" not in content:
        if "</body>" in content:
            content = content.replace("</body>", js_addition + "\n</body>")
    else:
        # Check if the event listener is present
        if "avatarBtn.addEventListener" not in content:
            content = content.replace("</body>", js_addition + "\n</body>")

    with open(tpath, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"Clean header applied to {tpath}")

print("All templates updated successfully!")
