with open("templates/dashboard.html", "r", encoding="utf-8") as f:
    text = f.read()

# 1. Topbar replacement
text = text.replace("DEMO MODE — AI predictions are not medical advice", "RESEARCH PROTOTYPE — AI forecasts are informational and not medical advice.")
text = text.replace('<div class="top-avatar">MA</div>', '<div class="top-avatar">{{ user.name[:2].upper() if user and user.name else "PT" }}</div>')

# 2. Welcome subtitle dynamic replacement
old_welcome = """<p>Sunday, 23 August 2026 · Last check-in: <strong>today at 07:30</strong></p>
<p style="margin-top:4px;">Type 2 Diabetes · Diagnosed 4 years ago · HbA1c 7.2%</p>"""
new_welcome = """<p><span id="dash_header_date">Today</span> · Last check-in: <strong id="dash_header_last_checkin">--</strong></p>
<p style="margin-top:4px;">{{ user.diabetes_type or 'Diabetes' }} · Diagnosed {{ user.years_since_diagnosis or '--' }} yrs ago · HbA1c {{ user.hba1c or '--' }}%</p>"""
text = text.replace(old_welcome, new_welcome)

# 3. GRU Warning banner
old_gru_warn = """<div class="gru-warning">
<svg viewbox="0 0 24 24"><path d="M19 15.59L14.41 11 19 6.41 17.59 5 13 9.59 8.41 5 7 6.41 11.59 11 7 15.59 8.41 17 13 12.41 17.59 17 19 15.59z"></path></svg>
<strong>GRU MODEL NOT CONNECTED</strong> Demo predictions shown for interface development only. Not for medical use.
                </div>"""
new_gru_warn = """<div id="dash_model_banner" class="gru-warning" style="background:#eff6ff; color:#1d4ed8; border:1px solid #bfdbfe;">
<svg viewbox="0 0 24 24"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-6h2v6zm0-8h-2V7h2v2z"></path></svg>
<strong id="dash_model_banner_text">AI DEEP LEARNING ACTIVE</strong> — GRU multi-horizon forecasting enabled.
</div>"""
text = text.replace(old_gru_warn, new_gru_warn)

# 4. Current Glucose trend text
old_curr_trend = """<div class="card-trend trend-up">
<svg viewbox="0 0 24 24"><path d="M16 6l2.29 2.29-4.88 4.88-4-4L2 16.59 3.41 18l6-6 4 4 6.3-6.29L22 12V6z"></path></svg>
                                    +12 from last reading
                                    <span style="color:var(--text-muted); font-size:12px; margin-left:8px;">07:30 today</span>
</div>"""
new_curr_trend = """<div class="card-trend" id="dash_gluc_delta" style="color:var(--text-muted); font-size:12px;">--</div>"""
text = text.replace(old_curr_trend, new_curr_trend)

# 5. Risk badge and target status
text = text.replace('<div class="risk-badge risk-moderate" style="margin-bottom:0;">\n<svg viewbox="0 0 24 24"><path d="M16 6l2.29 2.29-4.88 4.88-4-4L2 16.59 3.41 18l6-6 4 4 6.3-6.29L22 12V6z"></path></svg>\n                                Increasing Risk\n                            </div>',
                    '<div class="risk-badge" id="dash_risk_badge" style="margin-bottom:0; background:#f1f5f9; color:#64748b;">Monitoring</div>')
text = text.replace('<span style="font-weight:600; color:#b45309;">2 mg/dL above target</span>',
                    '<span id="dash_target_status" style="font-weight:600; color:var(--text-muted);">Reference: 70–140 mg/dL</span>')
text = text.replace('<span>Target range: 70–140 mg/dL (fasting)</span>', '<span>Informational reference range</span>')

# 6. Last check-in details
old_checkin_detail = '<div class="card-trend" style="color:var(--text-muted);">Breakfast · 142 mg/dL · Stress 4/10</div>'
new_checkin_detail = '<div class="card-trend" id="dash_last_checkin_detail" style="color:var(--text-muted);">--</div>'
text = text.replace(old_checkin_detail, new_checkin_detail)

# 7. Complications DEMO DATA badges & hardcoded notes
text = text.replace('<span class="demo-badge" style="margin-left:auto;">DEMO DATA</span>', '<span class="demo-badge" style="margin-left:auto; background:#f1f5f9; color:#64748b; border:1px solid #e2e8f0;">INFORMATIONAL</span>')
text = text.replace('ℹ️ HbA1c 7.2% and 4-year duration contribute to moderate indicator. Annual eye exam recommended.', 'ℹ️ Annual comprehensive clinical eye examination recommended for longitudinal diabetes monitoring.')

# 8. Timeline legend
text = text.replace('AI Forecast (Demo)', 'AI Forecast (GRU)')

# 9. Recent Checkins JS - update dash_last_checkin_detail and header
js_snippet_old = """if(data.records && data.records.length > 0) {
                    const latest = data.records[0];
                    const elTime = document.getElementById('dash_last_checkin');
                    if(elTime) {
                        const t = new Date(latest.timestamp);
                        elTime.innerHTML = t.toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'});
                    }"""

js_snippet_new = """if(data.records && data.records.length > 0) {
                    const latest = data.records[0];
                    const elTime = document.getElementById('dash_last_checkin');
                    const elHeaderTime = document.getElementById('dash_header_last_checkin');
                    const elDetail = document.getElementById('dash_last_checkin_detail');
                    const elDelta = document.getElementById('dash_gluc_delta');
                    
                    if(elTime) {
                        const t = new Date(latest.timestamp);
                        const timeStr = t.toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'});
                        elTime.innerHTML = timeStr;
                        if (elHeaderTime) elHeaderTime.innerText = `${t.toLocaleDateString()} at ${timeStr}`;
                    }
                    if(elDetail) {
                        let parts = [];
                        if (latest.meal_context) parts.push(latest.meal_context);
                        if (latest.glucose) parts.push(`${latest.glucose} mg/dL`);
                        if (latest.stress) parts.push(`Stress ${latest.stress}/10`);
                        elDetail.innerText = parts.join(' · ') || 'Check-in recorded';
                    }
                    if(elDelta && data.records.length >= 2) {
                        const prev = data.records[1];
                        if (latest.glucose && prev.glucose) {
                            const diff = Math.round((latest.glucose - prev.glucose)*10)/10;
                            const sign = diff > 0 ? '+' : '';
                            elDelta.innerHTML = `<strong>${sign}${diff} mg/dL</strong> from previous reading`;
                        }
                    }"""
text = text.replace(js_snippet_old, js_snippet_new)

with open("templates/dashboard.html", "w", encoding="utf-8") as f:
    f.write(text)

print("dashboard.html patched successfully!")
