import os
import re

sidebar_template = """    <!-- SIDEBAR -->
    <aside class="sidebar">
        <div class="logo-section">
            <div class="logo-icon"><svg viewBox="0 0 24 24"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 18c-4.41 0-8-3.59-8-8s3.59-8 8-8 8 3.59 8 8-3.59 8-8 8zm-1-13h2v6h-2zm0 8h2v2h-2z"/></svg></div>
            <div class="logo-text"><h1>DiabetesAI</h1><p>Early-Warning System</p></div>
        </div>

        <div class="nav-group">
            <div class="nav-label">OVERVIEW</div>
            <a href="/dashboard" class="nav-item {nav_dashboard}"><svg viewBox="0 0 24 24"><path d="M4 13h6c.55 0 1-.45 1-1V4c0-.55-.45-1-1-1H4c-.55 0-1 .45-1 1v8c0 .55.45 1 1 1zm0 8h6c.55 0 1-.45 1-1v-4c0-.55-.45-1-1-1H4c-.55 0-1 .45-1 1v4c0 .55.45 1 1 1zm10 0h6c.55 0 1-.45 1-1v-8c0-.55-.45-1-1-1h-6c-.55 0-1 .45-1 1v8c0 .55.45 1 1 1zM13 4v4c0 .55.45 1 1 1h6c.55 0 1-.45 1-1V4c0-.55-.45-1-1-1h-6c-.55 0-1 .45-1 1z"/></svg>Dashboard</a>
            <a href="/monitoring" class="nav-item {nav_monitoring}"><svg viewBox="0 0 24 24"><path d="M19 3h-1V1h-2v2H8V1H6v2H5c-1.11 0-2 .9-2 2v14c0 1.1.89 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm0 16H5V9h14v10zm0-12H5V5h14v2zM7 11h5v5H7z"/></svg>Daily Check-in<span class="badge-today">Today</span></a>
        </div>

        <div class="nav-group">
            <div class="nav-label">GLUCOSE & AI</div>
            <a href="/glucose" class="nav-item {nav_glucose}"><svg viewBox="0 0 24 24"><path d="M16 6l2.29 2.29-4.88 4.88-4-4L2 16.59 3.41 18l6-6 4 4 6.3-6.29L22 12V6z"/></svg>Glucose Monitor</a>
            <a href="/ai-forecast" class="nav-item {nav_forecast}"><svg viewBox="0 0 24 24"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-6h2v6zm0-8h-2V7h2v2z"/></svg>AI Forecast<span class="badge-demo">DEMO</span></a>
            <a href="/risk-trends" class="nav-item {nav_risk}"><svg viewBox="0 0 24 24"><path d="M3.5 18.49l6-6.01 4 4L22 6.92l-1.41-1.41-7.09 7.97-4-4L2 16.99z"/></svg>Risk Trends</a>
            <a href="/simulator" class="nav-item {nav_simulator}"><svg viewBox="0 0 24 24"><path d="M19 3H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm-7 9h-2V7h-2v5H6v2h2v5h2v-5h2v-2z"/></svg>What-If Simulator<span class="badge-new">NEW</span></a>
        </div>

        <div class="nav-group">
            <div class="nav-label">WELLNESS</div>
            <a href="/mental-wellness" class="nav-item {nav_mental}"><svg viewBox="0 0 24 24"><path d="M12 21.35l-1.45-1.32C5.4 15.36 2 12.28 2 8.5 2 5.42 4.42 3 7.5 3c1.74 0 3.41.81 4.5 2.09C13.09 3.81 14.76 3 16.5 3 19.58 3 22 5.42 22 8.5c0 3.78-3.4 6.86-8.55 11.54L12 21.35z"/></svg>Mental Wellness</a>
            <a href="/health-trends" class="nav-item {nav_health}"><svg viewBox="0 0 24 24"><path d="M13 2.05v3.03c3.39.49 6 3.39 6 6.92 0 .9-.18 1.75-.48 2.54l2.6 1.53c.56-1.24.88-2.62.88-4.07 0-5.18-3.95-9.45-9-9.95zM12 19c-3.87 0-7-3.13-7-7 0-3.53 2.61-6.43 6-6.92V2.05c-5.06.5-9 4.76-9 9.95 0 5.52 4.48 10 10 10 3.31 0 6.23-1.61 8.06-4.09l-2.6-1.53C16.17 17.98 14.21 19 12 19z"/></svg>Health Trends</a>
        </div>

        <div class="user-profile-sidebar">
            <div class="avatar">MA</div>
            <div class="user-info">
                <h4>{{ user.name if user else 'Maria Andrade' }}</h4>
                <p>Type 2 - 4 yrs</p>
            </div>
        </div>
        <a href="/logout" class="logout-btn">
            <svg viewBox="0 0 24 24"><path d="M17 7l-1.41 1.41L18.17 11H8v2h10.17l-2.58 2.58L17 17l5-5zM4 5h8V3H4c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h8v-2H4V5z"/></svg>
            Log Out
        </a>
    </aside>"""

def replace_sidebar(file_path, active_dict):
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    # regex to find the sidebar
    pattern = re.compile(r'<!-- SIDEBAR -->.*?</aside>', re.DOTALL)
    new_sidebar = sidebar_template.format(**active_dict)
    
    if pattern.search(content):
        content = pattern.sub(new_sidebar, content)
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"Updated {file_path}")

active_dash = {"nav_dashboard": "active", "nav_monitoring": "", "nav_glucose": "", "nav_forecast": "", "nav_risk": "", "nav_simulator": "", "nav_mental": "", "nav_health": ""}
active_mon = {"nav_dashboard": "", "nav_monitoring": "active", "nav_glucose": "", "nav_forecast": "", "nav_risk": "", "nav_simulator": "", "nav_mental": "", "nav_health": ""}

replace_sidebar("templates/dashboard.html", active_dash)
replace_sidebar("templates/monitoring.html", active_mon)
