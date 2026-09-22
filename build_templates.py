import os
import re

templates_dir = "templates"

sidebar_html = """
    <!-- SIDEBAR -->
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
            <div class="user-info"><h4>{{ user.name if user else 'Maria Andrade' }}</h4><p>Type 2 - 4 yrs</p></div>
        </div>
        <a href="/logout" class="logout-btn"><svg viewBox="0 0 24 24"><path d="M17 7l-1.41 1.41L18.17 11H8v2h10.17l-2.58 2.58L17 17l5-5zM4 5h8V3H4c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h8v-2H4V5z"/></svg>Log Out</a>
    </aside>
"""

base_html = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>DiabetesAI - {title}</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        :root {{ --bg-body: #f8f9fc; --bg-card: #ffffff; --border: #e2e8f0; --text-main: #1e293b; --text-muted: #64748b; --primary: #3b82f6; --primary-bg: #eff6ff; --purple: #8b5cf6; --purple-bg: #f3e8ff; --demo-yellow: #fef3c7; --demo-yellow-text: #b45309; }}
        * {{ box-sizing: border-box; margin: 0; padding: 0; }}
        body {{ font-family: 'Inter', sans-serif; background-color: var(--bg-body); color: var(--text-main); display: flex; height: 100vh; overflow: hidden; }}
        svg {{ width: 16px; height: 16px; fill: currentColor; }}
        .sidebar {{ width: 260px; background: #fff; border-right: 1px solid var(--border); display: flex; flex-direction: column; flex-shrink: 0; overflow-y: auto; }}
        .logo-section {{ padding: 24px 20px; display: flex; align-items: center; gap: 12px; }}
        .logo-icon {{ width: 32px; height: 32px; background: #f1f5f9; border-radius: 50%; display: flex; align-items: center; justify-content: center; color: var(--text-muted); }}
        .logo-text h1 {{ font-size: 18px; font-weight: 700; color: #0f172a; }}
        .logo-text p {{ font-size: 11px; color: var(--text-muted); }}
        .nav-group {{ margin-top: 16px; }}
        .nav-label {{ font-size: 11px; font-weight: 600; color: #94a3b8; text-transform: uppercase; letter-spacing: 0.5px; padding: 0 20px; margin-bottom: 8px; }}
        .nav-item {{ display: flex; align-items: center; padding: 10px 20px; color: var(--text-muted); text-decoration: none; font-size: 14px; font-weight: 500; margin: 2px 12px; border-radius: 8px; gap: 12px; }}
        .nav-item:hover {{ background: #f8fafc; color: var(--text-main); }}
        .nav-item.active {{ background: var(--primary-bg); color: var(--primary); }}
        .nav-item.active-purple {{ background: var(--purple-bg); color: var(--purple); }}
        .badge-demo {{ background: var(--demo-yellow); color: var(--demo-yellow-text); font-size: 10px; font-weight: 600; padding: 2px 6px; border-radius: 4px; margin-left: auto; }}
        .badge-new {{ background: #dcfce7; color: #15803d; font-size: 10px; font-weight: 600; padding: 2px 6px; border-radius: 4px; margin-left: auto; }}
        .badge-today {{ background: var(--primary-bg); color: var(--primary); font-size: 11px; font-weight: 600; padding: 2px 6px; border-radius: 4px; margin-left: auto; }}
        .demo-badge {{ background: var(--demo-yellow); color: var(--demo-yellow-text); font-size: 12px; font-weight: 600; padding: 2px 6px; border-radius: 4px; display: inline-block;}}
        .user-profile-sidebar {{ margin-top: auto; padding: 20px; border-top: 1px solid var(--border); display: flex; align-items: center; gap: 12px; }}
        .avatar {{ width: 36px; height: 36px; background: var(--primary); color: #fff; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: 600; font-size: 14px; }}
        .user-info h4 {{ font-size: 14px; font-weight: 600; color: var(--text-main); }}
        .user-info p {{ font-size: 12px; color: var(--text-muted); }}
        .logout-btn {{ display: flex; align-items: center; gap: 8px; color: #dc2626; font-size: 14px; font-weight: 600; padding: 0 20px 20px; text-decoration: none; }}
        .main-wrapper {{ flex: 1; display: flex; flex-direction: column; overflow: hidden; }}
        .topbar {{ height: 64px; background: #fff; border-bottom: 1px solid var(--border); display: flex; align-items: center; padding: 0 32px; justify-content: space-between; flex-shrink: 0; }}
        .top-demo-warning {{ background: var(--demo-yellow); color: var(--demo-yellow-text); padding: 6px 12px; border-radius: 20px; font-size: 12px; font-weight: 600; display: flex; align-items: center; gap: 6px; border: 1px solid #fde68a; }}
        .top-actions {{ display: flex; align-items: center; gap: 20px; }}
        .search-box {{ display: flex; align-items: center; gap: 8px; color: var(--text-muted); font-size: 14px; background: #f1f5f9; padding: 6px 12px; border-radius: 20px; border: 1px solid var(--border); }}
        .emergency-btn {{ color: #dc2626; font-size: 13px; font-weight: 600; display: flex; align-items: center; gap: 6px; cursor: pointer; }}
        .top-avatar {{ width: 32px; height: 32px; background: var(--primary); color: #fff; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: 600; font-size: 13px; }}
        .content-scroll {{ flex: 1; overflow-y: auto; padding: 32px; }}
        .content {{ max-width: 1200px; margin: 0 auto; display: flex; flex-direction: column; gap: 24px; }}
        .header-section {{ display: flex; justify-content: space-between; align-items: flex-end; margin-bottom: 8px; }}
        .header-title {{ font-size: 24px; font-weight: 700; margin-bottom: 4px; display: flex; align-items: center; gap: 12px; }}
        .header-subtitle {{ color: var(--text-muted); font-size: 14px; }}
        .grid-2 {{ display: grid; grid-template-columns: 2fr 1fr; gap: 24px; }}
        .grid-3 {{ display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 24px; }}
        .grid-4 {{ display: grid; grid-template-columns: 1fr 1fr 1fr 1fr; gap: 16px; }}
        .card {{ background: var(--bg-card); border-radius: 12px; border: 1px solid var(--border); padding: 24px; display: flex; flex-direction: column; }}
        .card-header {{ display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 20px; }}
        .card-title {{ font-size: 16px; font-weight: 600; }}
        .stat-value {{ font-size: 28px; font-weight: 700; color: var(--text-main); margin-bottom: 4px; }}
        .stat-label {{ font-size: 13px; color: var(--text-muted); font-weight: 500; }}
        .alert-box {{ background: #fff1f2; border-left: 4px solid #e11d48; padding: 16px; border-radius: 4px; margin-bottom: 16px; }}
        .info-box {{ background: var(--primary-bg); border-left: 4px solid var(--primary); padding: 16px; border-radius: 4px; }}
        .table {{ width: 100%; border-collapse: collapse; }}
        .table th {{ text-align: left; padding: 12px; border-bottom: 1px solid var(--border); font-size: 12px; color: var(--text-muted); font-weight: 600; }}
        .table td {{ padding: 12px; border-bottom: 1px solid var(--border); font-size: 14px; }}
        .input-std {{ padding: 8px 12px; border: 1px solid var(--border); border-radius: 6px; font-family: inherit; font-size: 14px; width: 100%; }}
        .btn {{ background: var(--primary); color: #fff; border: none; padding: 10px 16px; border-radius: 6px; font-weight: 600; cursor: pointer; }}
    </style>
</head>
<body>
    {sidebar}
    <div class="main-wrapper">
        <header class="topbar">
            <div class="top-demo-warning"><svg viewBox="0 0 24 24"><path d="M1 21h22L12 2 1 21zm12-3h-2v-2h2v2zm0-4h-2v-4h2v4z"/></svg>DEMO MODE — AI predictions are not medical advice</div>
            <div class="top-actions">
                <div class="search-box">Search... ⌘K</div>
                <div class="emergency-btn">Emergency</div>
                <div class="top-avatar">MA</div>
            </div>
        </header>
        <main class="content-scroll">
            <div class="content">
                {content}
            </div>
        </main>
    </div>
    {scripts}
</body>
</html>
"""

pages = {}

# 1. Glucose Monitor
pages["glucose"] = {
    "title": "Glucose Monitor",
    "nav_dashboard": "", "nav_monitoring": "", "nav_glucose": "active", "nav_forecast": "", "nav_risk": "", "nav_simulator": "", "nav_mental": "", "nav_health": "",
    "content": """
    <div class="header-section">
        <div>
            <h2 class="header-title">Glucose Monitor <span class="demo-badge">DEMO DATA</span></h2>
            <p class="header-subtitle">Track your glucose history and understand your recent patterns.</p>
        </div>
    </div>
    
    <div class="grid-4">
        <div class="card" style="padding: 16px;">
            <div class="stat-label">Current Glucose</div>
            <div class="stat-value">148 <span style="font-size:14px; color:var(--text-muted);">mg/dL</span></div>
            <div style="font-size:12px; color:#f59e0b; font-weight:600; margin-top:4px;">Elevated (Today, 10:30 AM)</div>
        </div>
        <div class="card" style="padding: 16px;">
            <div class="stat-label">Today's Average</div>
            <div class="stat-value">135 <span style="font-size:14px; color:var(--text-muted);">mg/dL</span></div>
        </div>
        <div class="card" style="padding: 16px;">
            <div class="stat-label">Highest</div>
            <div class="stat-value">195 <span style="font-size:14px; color:var(--text-muted);">mg/dL</span></div>
        </div>
        <div class="card" style="padding: 16px;">
            <div class="stat-label">Lowest</div>
            <div class="stat-value">82 <span style="font-size:14px; color:var(--text-muted);">mg/dL</span></div>
        </div>
    </div>

    <div class="grid-2">
        <div class="card">
            <h3 class="card-title">Glucose History Chart</h3>
            <div style="height:300px; position:relative; width: 100%; margin-top:20px;">
                <canvas id="chartG"></canvas>
            </div>
        </div>
        
        <div style="display:flex; flex-direction:column; gap:24px;">
            <div class="card">
                <h3 class="card-title">Glucose Trend</h3>
                <div style="font-size:32px; font-weight:700; color:#f59e0b; margin-top:10px;">↗ Increasing</div>
                <p style="font-size:13px; color:var(--text-muted); margin-top:10px;">Your glucose has been steadily increasing over the last 3 hours.</p>
            </div>
            
            <div class="card">
                <h3 class="card-title">Recent Readings</h3>
                <table class="table">
                    <tr><th>Time</th><th>Glucose</th><th>Status</th></tr>
                    <tr><td>10:30 AM</td><td>148</td><td><span style="color:#f59e0b;font-weight:600;">Elevated</span></td></tr>
                    <tr><td>09:00 AM</td><td>125</td><td><span style="color:#10b981;font-weight:600;">In Range</span></td></tr>
                    <tr><td>07:30 AM</td><td>110</td><td><span style="color:#10b981;font-weight:600;">In Range</span></td></tr>
                </table>
            </div>
        </div>
    </div>
    
    <div class="info-box">
        <strong>Information:</strong> This page will eventually use real patient glucose records from the database. Currently displaying demo data.
    </div>
    """,
    "scripts": """<script>
    new Chart(document.getElementById('chartG'), {
        type: 'line', data: { labels: ['00:00','04:00','08:00','12:00','16:00'], datasets: [{ label: 'Glucose', data: [110, 105, 140, 135, 148], borderColor: '#3b82f6', tension: 0.4, fill: true, backgroundColor: 'rgba(59,130,246,0.1)' }] },
        options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { display: false } } }
    });
    </script>"""
}

# 2. AI Forecast (using active-purple for nav_forecast)
pages["ai_forecast"] = {
    "title": "AI Forecast",
    "nav_dashboard": "", "nav_monitoring": "", "nav_glucose": "", "nav_forecast": "active-purple", "nav_risk": "", "nav_simulator": "", "nav_mental": "", "nav_health": "",
    "content": """
    <div class="header-section">
        <div>
            <h2 class="header-title">AI Glucose Forecast <span class="demo-badge">DEMO DATA</span></h2>
            <p class="header-subtitle">Predict future glucose trends using the planned GRU deep-learning model.</p>
        </div>
    </div>
    
    <div class="alert-box">
        <strong>DEMO MODE: GRU MODEL NOT CONNECTED.</strong> Do not interpret these demo values as real medical predictions. The final version will connect to the trained GRU model using the verified longitudinal dataset.
    </div>

    <div class="grid-3">
        <div class="card">
            <div class="stat-label">Current Glucose</div>
            <div class="stat-value">135 <span style="font-size:14px; color:var(--text-muted);">mg/dL</span></div>
        </div>
        <div class="card">
            <div class="stat-label">30-minute Forecast</div>
            <div class="stat-value" style="color:var(--purple);">150 <span style="font-size:14px; color:var(--text-muted);">mg/dL</span></div>
        </div>
        <div class="card">
            <div class="stat-label">60-minute Forecast</div>
            <div class="stat-value" style="color:var(--purple);">165 <span style="font-size:14px; color:var(--text-muted);">mg/dL</span></div>
        </div>
    </div>

    <div class="grid-2">
        <div class="card">
            <h3 class="card-title">Forecast Chart (Demo)</h3>
            <div style="height:300px; position:relative; width: 100%; margin-top:20px;">
                <canvas id="chartF"></canvas>
            </div>
        </div>
        
        <div style="display:flex; flex-direction:column; gap:24px;">
            <div class="card">
                <h3 class="card-title">Forecast Trend</h3>
                <div style="font-size:32px; font-weight:700; color:#f59e0b; margin-top:10px;">↗ Increasing</div>
            </div>
            
            <div class="card">
                <h3 class="card-title">Model Information</h3>
                <p style="font-size:13px; margin-top:10px;"><strong>Model:</strong> GRU Time-Series</p>
                <p style="font-size:13px; margin-top:10px;"><strong>Input:</strong> Historical glucose + available physiological/context features</p>
                <p style="font-size:13px; margin-top:10px;"><strong>Status:</strong> Demo — model not connected</p>
            </div>
        </div>
    </div>
    """,
    "scripts": """<script>
    new Chart(document.getElementById('chartF'), {
        type: 'line', data: { labels: ['-60m','-30m','Now','+30m','+60m'], datasets: [{ label: 'Historical', data: [110, 120, 135, null, null], borderColor: '#3b82f6', tension: 0.4 }, { label: 'Demo Predicted', data: [null, null, 135, 150, 165], borderColor: '#8b5cf6', borderDash: [5,5], tension: 0.4 }] },
        options: { responsive: true, maintainAspectRatio: false }
    });
    </script>"""
}

# 3. Risk Trends
pages["risk_trends"] = {
    "title": "Risk Trends",
    "nav_dashboard": "", "nav_monitoring": "", "nav_glucose": "", "nav_forecast": "", "nav_risk": "active", "nav_simulator": "", "nav_mental": "", "nav_health": "",
    "content": """
    <div class="header-section">
        <div>
            <h2 class="header-title">Patient Risk Trends <span class="demo-badge">DEMO DATA</span></h2>
            <p class="header-subtitle">Monitor changes in health-related indicators over time.</p>
        </div>
        <select class="input-std" style="width:auto;"><option>7 Days</option><option>14 Days</option><option>30 Days</option><option>90 Days</option></select>
    </div>

    <div class="alert-box">
        <strong>⚠ Increasing-risk pattern detected</strong><br>
        Recent demo data shows an increasing trend across selected indicators.
    </div>

    <div class="grid-4">
        <div class="card"><div class="stat-label">Glucose Trend</div><div style="font-size:24px;font-weight:700;color:#f59e0b;">↗ Increasing</div></div>
        <div class="card"><div class="stat-label">Stress Trend</div><div style="font-size:24px;font-weight:700;color:#f59e0b;">↗ Increasing</div></div>
        <div class="card"><div class="stat-label">Sleep Trend</div><div style="font-size:24px;font-weight:700;color:#ef4444;">↘ Decreasing</div></div>
        <div class="card"><div class="stat-label">Activity Trend</div><div style="font-size:24px;font-weight:700;color:#10b981;">→ Stable</div></div>
    </div>

    <div class="card">
        <h3 class="card-title">Overall Risk Trend Chart</h3>
        <div style="height:300px; position:relative; width: 100%; margin-top:20px;">
            <canvas id="chartR"></canvas>
        </div>
    </div>
    
    <h3 style="margin-top:20px;">Complication Risk Indicators</h3>
    <div class="grid-3">
        <div class="card"><h3 class="card-title">Kidney</h3><p style="color:var(--text-muted);font-size:13px;margin-top:10px;">Demo / Risk model not connected</p></div>
        <div class="card"><h3 class="card-title">Cardiovascular</h3><p style="color:var(--text-muted);font-size:13px;margin-top:10px;">Demo / Risk model not connected</p></div>
        <div class="card"><h3 class="card-title">Eye</h3><p style="color:var(--text-muted);font-size:13px;margin-top:10px;">Demo / Risk model not connected</p></div>
    </div>
    """,
    "scripts": """<script>
    new Chart(document.getElementById('chartR'), {
        type: 'line', data: { labels: ['Mon','Tue','Wed','Thu','Fri'], datasets: [{ label: 'Risk Score (Demo)', data: [40, 45, 55, 60, 65], borderColor: '#f59e0b', tension: 0.4 }] },
        options: { responsive: true, maintainAspectRatio: false }
    });
    </script>"""
}

# 4. What-If Simulator
pages["simulator"] = {
    "title": "What-If Simulator",
    "nav_dashboard": "", "nav_monitoring": "", "nav_glucose": "", "nav_forecast": "", "nav_risk": "", "nav_simulator": "active", "nav_mental": "", "nav_health": "",
    "content": """
    <div class="header-section">
        <div>
            <h2 class="header-title">What-If Health Simulator <span class="demo-badge">DEMO DATA</span></h2>
            <p class="header-subtitle">Explore how changes in lifestyle inputs could affect a future glucose prediction.</p>
        </div>
    </div>
    
    <div class="info-box">
        <strong>DEMO MODE: GRU MODEL NOT CONNECTED.</strong> Final implementation will send the scenario to the trained GRU model and compare the resulting predictions. Do not claim the result is medically accurate.
    </div>
    
    <div class="grid-2">
        <div class="card">
            <h3 class="card-title">Input Controls</h3>
            <div style="display:flex; flex-direction:column; gap:16px; margin-top:16px;">
                <div><label class="stat-label">Meal / Carbohydrate Level</label><select class="input-std"><option>Low</option><option>Moderate</option><option>High</option></select></div>
                <div><label class="stat-label">Exercise Duration (min)</label><input type="number" class="input-std" value="30"></div>
                <div><label class="stat-label">Sleep Duration (hours)</label><input type="number" class="input-std" value="7"></div>
                <div><label class="stat-label">Stress Level</label><select class="input-std"><option>Low</option><option>Moderate</option><option>High</option></select></div>
                <button class="btn" style="margin-top:10px;">SIMULATE</button>
            </div>
        </div>
        
        <div style="display:flex; flex-direction:column; gap:24px;">
            <div class="card" style="background:#f1f5f9;">
                <h3 class="card-title">Current Scenario</h3>
                <p style="font-size:13px;margin-top:10px;"><strong>Exercise:</strong> 0 min<br><strong>Sleep:</strong> 5 hours<br><strong>Stress:</strong> High</p>
                <div style="font-size:24px; font-weight:700; color:#e11d48; margin-top:10px;">Predicted Peak: 195</div>
            </div>
            <div class="card" style="background:#eff6ff; border-color:var(--primary);">
                <h3 class="card-title">What-If Scenario (Demo Result)</h3>
                <p style="font-size:13px;margin-top:10px;"><strong>Exercise:</strong> 30 min<br><strong>Sleep:</strong> 7 hours<br><strong>Stress:</strong> Moderate</p>
                <div style="font-size:24px; font-weight:700; color:var(--primary); margin-top:10px;">Predicted Peak: 140</div>
            </div>
        </div>
    </div>
    
    <div class="card" style="margin-top:24px;">
        <h3 class="card-title">Before vs After Comparison</h3>
        <div style="height:300px; position:relative; width: 100%; margin-top:20px;">
            <canvas id="chartS"></canvas>
        </div>
    </div>
    """,
    "scripts": """<script>
    new Chart(document.getElementById('chartS'), {
        type: 'bar', data: { labels: ['Peak Glucose (mg/dL)'], datasets: [{ label: 'Current', data: [195], backgroundColor: '#e11d48' }, { label: 'What-If (Demo)', data: [140], backgroundColor: '#3b82f6' }] },
        options: { responsive: true, maintainAspectRatio: false }
    });
    </script>"""
}

# 5. Mental Wellness
pages["mental_wellness"] = {
    "title": "Mental Wellness",
    "nav_dashboard": "", "nav_monitoring": "", "nav_glucose": "", "nav_forecast": "", "nav_risk": "", "nav_simulator": "", "nav_mental": "active", "nav_health": "",
    "content": """
    <div class="header-section">
        <div>
            <h2 class="header-title">Mental Wellness <span class="demo-badge">DEMO DATA</span></h2>
            <p class="header-subtitle">Monitor stress, sleep, mood, and activity patterns over time.</p>
        </div>
    </div>

    <div class="grid-4">
        <div class="card" style="background:var(--primary-bg); border-color:var(--primary);"><div class="stat-label">Current Wellness Status</div><div style="font-size:24px;font-weight:700;color:var(--primary);">Moderate</div></div>
        <div class="card"><div class="stat-label">Stress</div><div style="font-size:20px;font-weight:600;margin-top:4px;">↗ Increasing</div></div>
        <div class="card"><div class="stat-label">Sleep</div><div style="font-size:20px;font-weight:600;margin-top:4px;">↘ Decreasing</div></div>
        <div class="card"><div class="stat-label">Mood</div><div style="font-size:20px;font-weight:600;margin-top:4px;">→ Stable</div></div>
    </div>

    <div class="grid-2">
        <div class="card">
            <h3 class="card-title">Wellness Trends Over Time</h3>
            <div style="height:300px; position:relative; width: 100%; margin-top:20px;">
                <canvas id="chartM"></canvas>
            </div>
        </div>
        <div class="card">
            <h3 class="card-title">Wellness Guidance</h3>
            <p style="font-size:14px; line-height:1.6; color:var(--text-muted); margin-top:16px;">
                Your recent demo data suggests an increase in stress paired with a decrease in sleep duration. 
                Consider establishing a relaxing bedtime routine and reducing screen time before bed to improve sleep quality. 
                <br><br>
                <em>Note: This is general informational guidance and does not diagnose mental-health conditions.</em>
            </p>
        </div>
    </div>
    """,
    "scripts": """<script>
    new Chart(document.getElementById('chartM'), {
        type: 'line', data: { labels: ['Day 1','Day 2','Day 3','Day 4'], datasets: [{ label: 'Stress (Demo)', data: [4, 5, 6, 8], borderColor: '#f59e0b', tension: 0.4 }, { label: 'Sleep hrs', data: [8, 7, 6, 5], borderColor: '#8b5cf6', tension: 0.4 }] },
        options: { responsive: true, maintainAspectRatio: false }
    });
    </script>"""
}

# 6. Health Trends
pages["health_trends"] = {
    "title": "Health Trends",
    "nav_dashboard": "", "nav_monitoring": "", "nav_glucose": "", "nav_forecast": "", "nav_risk": "", "nav_simulator": "", "nav_mental": "", "nav_health": "active",
    "content": """
    <div class="header-section">
        <div>
            <h2 class="header-title">Health Trends <span class="demo-badge">DEMO DATA</span></h2>
            <p class="header-subtitle">View long-term relationships between glucose and lifestyle patterns.</p>
        </div>
        <select class="input-std" style="width:auto;"><option>30 Days</option><option>90 Days</option></select>
    </div>

    <div class="grid-4">
        <div class="card"><div class="stat-label">Avg Glucose</div><div class="stat-value">138</div></div>
        <div class="card"><div class="stat-label">Avg Sleep</div><div class="stat-value">6.5h</div></div>
        <div class="card"><div class="stat-label">Avg Activity</div><div class="stat-value">4.2k</div></div>
        <div class="card"><div class="stat-label">Avg Stress</div><div class="stat-value">Moderate</div></div>
    </div>

    <div class="card">
        <h3 class="card-title">Comparison: Glucose vs Sleep (Demo)</h3>
        <select class="input-std" style="width:200px; margin-top:10px;"><option>Glucose vs Sleep</option><option>Glucose vs Activity</option><option>Glucose vs Stress</option></select>
        <div style="height:300px; position:relative; width: 100%; margin-top:20px;">
            <canvas id="chartH"></canvas>
        </div>
    </div>
    <div class="info-box" style="margin-top:20px;">
        <strong>Information:</strong> Page uses demo data until the real database is connected.
    </div>
    """,
    "scripts": """<script>
    new Chart(document.getElementById('chartH'), {
        type: 'line', data: { labels: ['Week 1','Week 2','Week 3','Week 4'], datasets: [{ label: 'Avg Glucose', data: [130, 140, 145, 138], borderColor: '#3b82f6', yAxisID: 'y' }, { label: 'Avg Sleep', data: [7.5, 6, 5.5, 6.5], borderColor: '#10b981', yAxisID: 'y1' }] },
        options: { responsive: true, maintainAspectRatio: false, scales: { y: { type: 'linear', position: 'left' }, y1: { type: 'linear', position: 'right' } } }
    });
    </script>"""
}

# Write out all pages
for page_name, data in pages.items():
    sidebar_filled = sidebar_html.format(**data)
    full_html = base_html.format(
        title=data["title"],
        sidebar=sidebar_filled,
        content=data["content"],
        scripts=data["scripts"]
    )
    with open(os.path.join(templates_dir, f"{page_name}.html"), "w", encoding="utf-8") as f:
        f.write(full_html)

print("Created all 6 HTML templates.")
