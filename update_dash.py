import re
from bs4 import BeautifulSoup
import os

def update_dashboard():
    with open('templates/dashboard.html', 'r', encoding='utf-8') as f:
        soup = BeautifulSoup(f.read(), 'html.parser')
    
    # 1. Update Current Glucose stat
    cards = soup.select('.card-value')
    if len(cards) >= 1:
        cards[0]['id'] = 'dash_current_glucose'
        cards[0].string = '-- '
        span = soup.new_tag('span')
        span.string = 'mg/dL'
        cards[0].append(span)

    # Update 7-day AVG Glucose
    if len(cards) >= 3:
        cards[2]['id'] = 'dash_today_avg'
        cards[2].string = '-- '
        span = soup.new_tag('span')
        span.string = 'mg/dL'
        cards[2].append(span)

    # 2. Update Recent Records list
    records_list = soup.select_one('.records-list')
    if records_list:
        records_list['id'] = 'dash_recent_records'
        records_list.clear()
        loading_div = soup.new_tag('div')
        loading_div.string = 'Loading health data...'
        loading_div['style'] = 'padding: 20px; color: var(--text-muted);'
        records_list.append(loading_div)

    # 3. Add script at the end to fetch data
    script_tag = soup.new_tag('script')
    script_tag.string = """
    document.addEventListener("DOMContentLoaded", function() {
        // Fetch summary
        fetch('/api/health/summary')
            .then(res => {
                if (res.status === 401) { window.location.href = '/login'; return null; }
                return res.json();
            })
            .then(data => {
                if (!data) return;
                if(data.success && data.current_glucose !== undefined) {
                    const elCurrent = document.getElementById('dash_current_glucose');
                    if (elCurrent) elCurrent.innerHTML = (data.current_glucose || '--') + ' <span>mg/dL</span>';
                    const elAvg = document.getElementById('dash_today_avg');
                    if (elAvg) elAvg.innerHTML = (data.today_average_glucose || '--') + ' <span>mg/dL</span>';
                }
            })
            .catch(err => console.error(err));

        // Fetch recent
        fetch('/api/health-records/recent?limit=5')
            .then(res => res.json())
            .then(data => {
                const list = document.getElementById('dash_recent_records');
                if(!list) return;
                list.innerHTML = '';
                if(data.records && data.records.length > 0) {
                    data.records.forEach(r => {
                        list.innerHTML += `
                            <div class="record-item" style="display:flex; justify-content:space-between; padding:12px 0; border-bottom:1px solid #f1f5f9;">
                                <div>
                                    <div style="font-weight:600; color:#1e293b;">${r.glucose} <span style="font-size:12px; color:#64748b;">mg/dL</span></div>
                                    <div style="font-size:12px; color:#64748b; margin-top:4px;">${r.meal_context || 'Random'} • Stress ${r.stress||'?'}/10 • ${r.sleep||'?'}h sleep</div>
                                </div>
                                <div style="font-size:12px; color:#94a3b8;">${new Date(r.timestamp).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})}</div>
                            </div>
                        `;
                    });
                } else {
                    list.innerHTML = `<div style="padding:20px; color:#64748b;">No health records yet. <a href="/monitoring" style="color:#3b82f6;">Add Daily Check-in</a></div>`;
                }
            });

        // Fetch chart data
        fetch('/api/glucose/history?days=7')
            .then(res => res.json())
            .then(data => {
                if(data.records && data.records.length > 0) {
                    window.actualData = data.values;
                    window.chartLabels = data.labels;
                    updateDashboardChart();
                } else {
                    window.actualData = [];
                    window.chartLabels = [];
                    updateDashboardChart();
                }
            });
    });
    
    function updateDashboardChart() {
        if(!window.dashChart) return;
        window.dashChart.data.labels = window.chartLabels;
        window.dashChart.data.datasets[0].data = window.actualData;
        window.dashChart.update();
    }
    """
    
    # 4. Modify existing chart script
    for s in soup.find_all('script'):
        if s.string and 'glucoseTimelineChart' in s.string:
            # Replace mock data
            s.string = s.string.replace(
                "const mockActual = [135, 133, 195, 155, 140, 125, 195, 150, 125, 120, 145, 175, 140, 125, null, null, null, null];",
                "const mockActual = window.actualData || [];"
            ).replace(
                "const mockLabels = ['8/20 00:20', '', '', '', '8/20 21:20', '', '', '', '8/21 18:20', '', '', '', '8/22 15:20', '', '8/23 09:00', '', '', ''];",
                "const mockLabels = window.chartLabels || [];"
            )
            s.string = s.string.replace(
                "new Chart(ctx, {",
                "window.dashChart = new Chart(ctx, {"
            )

    soup.body.append(script_tag)
    
    with open('templates/dashboard.html', 'w', encoding='utf-8') as f:
        f.write(str(soup))
    print("Updated dashboard.html")

update_dashboard()
