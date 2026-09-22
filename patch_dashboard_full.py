# 1. Update onboarding_processing.html
with open("templates/onboarding_processing.html", "r", encoding="utf-8") as f:
    proc_html = f.read()

proc_html = proc_html.replace(
    '<span style="color:var(--text-muted);">AI forecasting model — Not connected yet</span>',
    '<span style="color:var(--primary); font-weight:600;">GRU forecasting model — Initializing personalized inference</span>'
)
with open("templates/onboarding_processing.html", "w", encoding="utf-8") as f:
    f.write(proc_html)
print("Updated onboarding_processing.html")

# 2. Update dashboard.html
with open("templates/dashboard.html", "r", encoding="utf-8") as f:
    dash_html = f.read()

# Replace SHAP fake numbers section
old_shap_section = """<div class="shap-row">
<div class="shap-label">
<svg style="color:var(--text-muted)" viewbox="0 0 24 24"><path d="M16 6l2.29 2.29-4.88 4.88-4-4L2 16.59 3.41 18l6-6 4 4 6.3-6.29L22 12V6z"></path></svg>
                                Recent glucose trend
                            </div>
<div class="shap-bar-container">
<div class="shap-bar-bg"><div class="shap-bar-fill" style="width:85%; background:#ef4444;"></div></div>
<div class="shap-value">+34 mg/dL in 3h<br/><strong>85%</strong></div>
</div>
</div>
<div class="shap-row">
<div class="shap-label">
<svg style="color:var(--text-muted)" viewbox="0 0 24 24"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-6h2v6zm0-8h-2V7h2v2z"></path></svg>
                                Meal carb load (dinner)
                            </div>
<div class="shap-bar-container">
<div class="shap-bar-bg"><div class="shap-bar-fill" style="width:72%; background:#f97316;"></div></div>
<div class="shap-value">74g carbs<br/><strong>72%</strong></div>
</div>
</div>
<div class="shap-row">
<div class="shap-label">
<svg style="color:var(--text-muted)" viewbox="0 0 24 24"><path d="M19 3H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm-7 9h-2V7h-2v5H6v2h2v5h2v-5h2v-2z"></path></svg>
                                Low activity yesterday
                            </div>
<div class="shap-bar-container">
<div class="shap-bar-bg"><div class="shap-bar-fill" style="width:55%; background:#d97706;"></div></div>
<div class="shap-value">2,890 steps<br/><strong>55%</strong></div>
</div>
</div>
<div class="shap-row">
<div class="shap-label">
<svg style="color:var(--text-muted)" viewbox="0 0 24 24"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-2h2v2zm0-4h-2V7h2v6z"></path></svg>
                                Poor sleep quality
                            </div>
<div class="shap-bar-container">
<div class="shap-bar-bg"><div class="shap-bar-fill" style="width:48%; background:#eab308;"></div></div>
<div class="shap-value">5.5h, poor quality<br/><strong>48%</strong></div>
</div>
</div>
<div class="shap-row">
<div class="shap-label">
<svg style="color:var(--text-muted)" viewbox="0 0 24 24"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-2h2v2zm0-4h-2V7h2v6z"></path></svg>
                                Elevated stress level
                            </div>
<div class="shap-bar-container">
<div class="shap-bar-bg"><div class="shap-bar-fill" style="width:61%; background:#facc15;"></div></div>
<div class="shap-value">Stress 8/10<br/><strong>61%</strong></div>
</div>
</div>"""

new_shap_section = """<div style="padding: 24px; background: #f8fafc; border-radius: 8px; border: 1px dashed #cbd5e1; text-align: center; margin-top: 12px;">
<div style="font-weight: 600; color: #475569; font-size: 14px; margin-bottom: 6px;">Factor Explainability (SHAP Attribution)</div>
<p style="font-size: 13px; color: #64748b; margin: 0; line-height: 1.5;">
Explainability will be available when longitudinal continuous monitoring inputs are available. The GRU model forecasts future glucose trajectories directly from your verified time-series health records.
</p>
</div>"""

dash_html = dash_html.replace(old_shap_section, new_shap_section)

# Replace 4-Week Trend chart container with dynamic IDs
old_4w_chart = """<div style="height:150px; display:flex; align-items:flex-end; gap:16px; justify-content:space-around; margin-top:20px; border-bottom:1px solid var(--border); padding-bottom:10px;">
<div style="width:40px; background:var(--primary); border-radius:4px 4px 0 0; height:40%;"></div>
<div style="width:40px; background:var(--primary); border-radius:4px 4px 0 0; height:50%;"></div>
<div style="width:40px; background:#60a5fa; border-radius:4px 4px 0 0; height:60%;"></div>
<div style="width:40px; background:#ef4444; border-radius:4px 4px 0 0; height:80%;"></div>
</div>
<div style="display:flex; justify-content:space-around; font-size:11px; color:var(--text-muted); margin-top:8px;">
<span>Week 1</span><span>Week 2</span><span>Week 3</span><span>Week 4</span>
</div>
<div style="margin-top:24px; padding-top:16px; border-top:1px solid var(--border); font-size:12px;">
<div style="color:#b91c1c; font-weight:600; display:flex; align-items:center; gap:6px; margin-bottom:4px;">
<svg viewbox="0 0 24 24"><path d="M1 21h22L12 2 1 21zm12-3h-2v-2h2v2zm0-4h-2v-4h2v4z"></path></svg> Upward trend detected
                            </div>
<div style="color:var(--text-muted);">Avg glucose increased 23 mg/dL over 4 weeks</div>
</div>"""

new_4w_chart = """<div style="height:150px; display:flex; align-items:flex-end; gap:16px; justify-content:space-around; margin-top:20px; border-bottom:1px solid var(--border); padding-bottom:10px;" id="dash_4w_bars">
<div id="bar_w1" style="width:40px; background:#e2e8f0; border-radius:4px 4px 0 0; height:10%; transition:height 0.4s ease;" title="Week 1: No data"></div>
<div id="bar_w2" style="width:40px; background:#e2e8f0; border-radius:4px 4px 0 0; height:10%; transition:height 0.4s ease;" title="Week 2: No data"></div>
<div id="bar_w3" style="width:40px; background:#e2e8f0; border-radius:4px 4px 0 0; height:10%; transition:height 0.4s ease;" title="Week 3: No data"></div>
<div id="bar_w4" style="width:40px; background:var(--primary); border-radius:4px 4px 0 0; height:10%; transition:height 0.4s ease;" title="Week 4"></div>
</div>
<div style="display:flex; justify-content:space-around; font-size:11px; color:var(--text-muted); margin-top:8px;">
<span id="lbl_w1">Wk -3</span><span id="lbl_w2">Wk -2</span><span id="lbl_w3">Wk -1</span><span id="lbl_w4">Current</span>
</div>
<div style="margin-top:24px; padding-top:16px; border-top:1px solid var(--border); font-size:12px;">
<div id="dash_4w_trend_title" style="color:var(--text-muted); font-weight:600; display:flex; align-items:center; gap:6px; margin-bottom:4px;">
<svg viewbox="0 0 24 24" style="width:16px; height:16px;"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-6h2v6zm0-8h-2V7h2v2z"/></svg> Historical Period Analysis
</div>
<div id="dash_4w_trend_desc" style="color:var(--text-muted);">Calculated dynamically from verified database records.</div>
</div>"""

dash_html = dash_html.replace(old_4w_chart, new_4w_chart)

# Replace the entire script block at bottom with clean, independent fetch calls and correct Chart.js mapping
script_start = dash_html.find("<script>")
if script_start != -1:
    clean_html = dash_html[:script_start]
else:
    clean_html = dash_html

new_scripts = """<script>
    let dashChart = null;

    function initChart() {
        const canvas = document.getElementById('glucoseTimelineChart');
        if (!canvas) return;
        const ctx = canvas.getContext('2d');
        
        let gradientBlue = ctx.createLinearGradient(0, 0, 0, 250);
        gradientBlue.addColorStop(0, 'rgba(59, 130, 246, 0.25)');
        gradientBlue.addColorStop(1, 'rgba(59, 130, 246, 0.0)');
        
        let gradientPurple = ctx.createLinearGradient(0, 0, 0, 250);
        gradientPurple.addColorStop(0, 'rgba(139, 92, 246, 0.25)');
        gradientPurple.addColorStop(1, 'rgba(139, 92, 246, 0.0)');

        dashChart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: [],
                datasets: [
                    {
                        label: 'Actual Glucose',
                        data: [],
                        borderColor: '#3b82f6',
                        backgroundColor: gradientBlue,
                        borderWidth: 2.5,
                        fill: true,
                        tension: 0.3,
                        pointRadius: 4,
                        pointBackgroundColor: '#3b82f6',
                        pointHoverRadius: 6
                    },
                    {
                        label: 'AI Forecast (GRU)',
                        data: [],
                        borderColor: '#8b5cf6',
                        backgroundColor: gradientPurple,
                        borderWidth: 2,
                        borderDash: [5, 5],
                        fill: true,
                        tension: 0.3,
                        pointRadius: 4,
                        pointBackgroundColor: '#8b5cf6',
                        pointHoverRadius: 6
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false },
                    tooltip: {
                        mode: 'index',
                        intersect: false,
                        backgroundColor: 'rgba(255,255,255,0.95)',
                        titleColor: '#1e293b',
                        bodyColor: '#64748b',
                        borderColor: '#e2e8f0',
                        borderWidth: 1
                    }
                },
                scales: {
                    x: {
                        grid: { color: '#f1f5f9', drawBorder: false },
                        ticks: { color: '#64748b', font: { size: 11, family: 'Inter' } }
                    },
                    y: {
                        suggestedMin: 60,
                        suggestedMax: 200,
                        ticks: {
                            color: '#94a3b8',
                            font: { size: 11, family: 'Inter' },
                            callback: function(v) { return v + ' mg/dL'; }
                        },
                        grid: { color: '#f1f5f9', drawBorder: false }
                    }
                }
            }
        });
    }

    document.addEventListener("DOMContentLoaded", function() {
        initChart();
        
        // 1. Independent Fetch: Health Summary
        fetch('/api/health/summary')
            .then(res => res.json())
            .then(data => {
                if (!data || !data.success) return;
                
                const elCurrent = document.getElementById('dash_current_glucose');
                if (elCurrent && data.current_glucose !== null && data.current_glucose !== undefined) {
                    elCurrent.innerHTML = `${data.current_glucose} <span>mg/dL</span>`;
                } else if (elCurrent) {
                    elCurrent.innerHTML = `-- <span>mg/dL</span>`;
                }

                const elDelta = document.getElementById('dash_gluc_delta');
                if (elDelta) {
                    if (data.glucose_delta !== null && data.glucose_delta !== undefined) {
                        const sign = data.glucose_delta > 0 ? '+' : '';
                        elDelta.innerHTML = `<strong>${sign}${data.glucose_delta} mg/dL</strong> from previous reading`;
                    } else {
                        elDelta.innerText = 'First baseline reading recorded';
                    }
                }

                const elAvg = document.getElementById('dash_today_avg');
                if (elAvg && data.weekly_average_glucose !== null && data.weekly_average_glucose !== undefined) {
                    elAvg.innerHTML = `${data.weekly_average_glucose} <span>mg/dL</span>`;
                }

                const elWell = document.getElementById('dash_wellness');
                if (elWell && data.stress_average !== null && data.stress_average !== undefined) {
                    elWell.innerHTML = data.stress_average <= 4 ? "Good" : (data.stress_average <= 7 ? "Moderate" : "Elevated Stress");
                }
            })
            .catch(err => console.error("Summary API error:", err));

        // 2. Independent Fetch: Recent Records & Last Check-in
        fetch('/api/health-records/recent?limit=5')
            .then(res => res.json())
            .then(data => {
                const list = document.getElementById('dash_recent_records');
                const elTime = document.getElementById('dash_last_checkin');
                const elHeaderTime = document.getElementById('dash_header_last_checkin');
                const elDetail = document.getElementById('dash_last_checkin_detail');

                if (data.records && data.records.length > 0) {
                    const latest = data.records[0];
                    if (elTime) {
                        const t = new Date(latest.timestamp);
                        elTime.innerHTML = t.toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'});
                    }
                    if (elHeaderTime) {
                        const t = new Date(latest.timestamp);
                        elHeaderTime.innerText = `${t.toLocaleDateString()} at ${t.toLocaleTimeString([], {hour:'2-digit', minute:'2-digit'})}`;
                    }
                    if (elDetail) {
                        let parts = [];
                        if (latest.meal_context) parts.push(latest.meal_context);
                        if (latest.glucose) parts.push(`${latest.glucose} mg/dL`);
                        if (latest.stress) parts.push(`Stress ${latest.stress}/10`);
                        elDetail.innerText = parts.join(' · ') || 'Recorded';
                    }

                    if (list) {
                        list.innerHTML = '';
                        data.records.forEach(r => {
                            list.innerHTML += `
                                <div class="record-item" style="display:flex; justify-content:space-between; padding:12px 0; border-bottom:1px solid #f1f5f9;">
                                    <div>
                                        <div style="font-weight:600; color:#1e293b;">${r.glucose} <span style="font-size:12px; color:#64748b;">mg/dL</span></div>
                                        <div style="font-size:12px; color:#64748b; margin-top:4px;">${r.meal_context || 'Random'} • Stress ${r.stress||'?'}/10 • ${r.sleep||'?'}h sleep</div>
                                    </div>
                                    <div style="font-size:12px; color:#94a3b8;">${new Date(r.timestamp).toLocaleDateString()} ${new Date(r.timestamp).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})}</div>
                                </div>
                            `;
                        });
                    }
                } else {
                    if (list) list.innerHTML = `<div style="padding:20px; color:#64748b;">No valid health records yet. <br><br><a href="/monitoring" style="color:#3b82f6;">Add Daily Check-in</a></div>`;
                    if (elTime) elTime.innerHTML = '--';
                    if (elDetail) elDetail.innerHTML = '--';
                }
            })
            .catch(err => console.error("Recent records API error:", err));

        // 3. Independent Fetch: Glucose Chart History
        fetch('/api/glucose/history?days=7')
            .then(res => res.json())
            .then(data => {
                if (data.success && data.labels && data.labels.length > 0 && dashChart) {
                    dashChart.data.labels = data.labels;
                    dashChart.data.datasets[0].data = data.values;
                    dashChart.update();
                    
                    // Update 4-week trend bars dynamically
                    update4WeekBars(data.values);
                }
            })
            .catch(err => console.error("Chart history API error:", err));

        // 4. Independent Fetch: Glucose Trend
        fetch('/api/glucose/trend')
            .then(res => res.json())
            .then(data => {
                const badge = document.getElementById('dash_risk_badge');
                if (badge && data.status) {
                    badge.innerText = data.status;
                    if (data.direction === 'up') {
                        badge.style.background = '#fef3c7';
                        badge.style.color = '#b45309';
                    } else if (data.direction === 'down') {
                        badge.style.background = '#dcfce7';
                        badge.style.color = '#15803d';
                    } else {
                        badge.style.background = '#eff6ff';
                        badge.style.color = '#1d4ed8';
                    }
                }
            })
            .catch(err => console.error("Trend API error:", err));

        // 5. Independent Fetch: Real GRU Forecast
        fetch('/api/forecast/predict')
            .then(res => res.json())
            .then(data => {
                const valEl = document.getElementById('dash_ai_pred_val');
                const trendEl = document.getElementById('dash_ai_pred_trend');
                const badgeEl = document.getElementById('dash_ai_pred_badge');
                
                if (data && data.available) {
                    if (valEl) {
                        valEl.style.color = 'var(--purple)';
                        valEl.innerHTML = `${data.prediction_30min} <span style="font-size:14px; color:var(--text-muted);">mg/dL (30m)</span>`;
                    }
                    if (trendEl) {
                        trendEl.style.color = '#1e293b';
                        trendEl.innerHTML = `60m Forecast: <strong>${data.prediction_60min} mg/dL</strong>`;
                    }
                    if (badgeEl) {
                        badgeEl.style.background = '#dcfce7';
                        badgeEl.style.color = '#15803d';
                        badgeEl.style.borderColor = '#86efac';
                        badgeEl.innerText = 'GRU MODEL ACTIVE';
                    }

                    // Append forecast points to chart if available
                    if (dashChart && dashChart.data.labels.length > 0) {
                        const lastLabel = dashChart.data.labels[dashChart.data.labels.length - 1];
                        const lastVal = dashChart.data.datasets[0].data[dashChart.data.datasets[0].data.length - 1];
                        
                        const forecastArray = Array(dashChart.data.labels.length).fill(null);
                        // Start forecast curve from last actual point
                        forecastArray[forecastArray.length - 1] = lastVal;
                        
                        dashChart.data.labels.push('+30 min');
                        forecastArray.push(data.prediction_30min);
                        dashChart.data.datasets[0].data.push(null);
                        
                        dashChart.data.labels.push('+60 min');
                        forecastArray.push(data.prediction_60min);
                        dashChart.data.datasets[0].data.push(null);
                        
                        dashChart.data.datasets[1].data = forecastArray;
                        dashChart.update();
                    }
                } else {
                    if (valEl) {
                        valEl.style.color = 'var(--text-muted)';
                        valEl.innerText = 'N/A';
                    }
                    if (trendEl) {
                        trendEl.style.color = 'var(--text-muted)';
                        trendEl.innerText = (data && data.message) ? data.message : 'More glucose history needed (minimum 5 readings).';
                    }
                    if (badgeEl) {
                        badgeEl.style.background = '#f1f5f9';
                        badgeEl.style.color = '#64748b';
                        badgeEl.style.borderColor = '#cbd5e1';
                        badgeEl.innerText = 'MORE DATA NEEDED';
                    }
                }
            })
            .catch(err => {
                console.error("Forecast API error:", err);
                const valEl = document.getElementById('dash_ai_pred_val');
                if (valEl) valEl.innerText = 'N/A';
            });
    });

    function update4WeekBars(values) {
        if (!values || values.length === 0) return;
        
        // Chunk into up to 4 segments
        const chunkSize = Math.max(1, Math.ceil(values.length / 4));
        const chunks = [];
        for (let i = 0; i < values.length; i += chunkSize) {
            chunks.push(values.slice(i, i + chunkSize));
        }
        
        const b1 = document.getElementById('bar_w1');
        const b2 = document.getElementById('bar_w2');
        const b3 = document.getElementById('bar_w3');
        const b4 = document.getElementById('bar_w4');
        const bars = [b1, b2, b3, b4];
        
        const descEl = document.getElementById('dash_4w_trend_desc');
        const maxVal = Math.max(...values, 200);
        
        chunks.forEach((chunk, idx) => {
            if (idx < 4 && bars[idx]) {
                const avg = chunk.reduce((a,b)=>a+b, 0) / chunk.length;
                const pct = Math.min(100, Math.max(15, Math.round((avg / maxVal) * 100)));
                bars[idx].style.height = pct + '%';
                bars[idx].style.background = '#3b82f6';
                bars[idx].title = `Avg: ${avg.toFixed(1)} mg/dL`;
            }
        });

        if (descEl) {
            const overallAvg = (values.reduce((a,b)=>a+b,0)/values.length).toFixed(1);
            descEl.innerText = `Average glucose across ${values.length} recorded readings is ${overallAvg} mg/dL.`;
        }
    }
</script>
</body>
</html>"""

with open("templates/dashboard.html", "w", encoding="utf-8") as f:
    f.write(clean_html + new_scripts)

print("dashboard.html successfully patched with independent APIs, dynamic chart and 4-week trend!")
