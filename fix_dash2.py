import re
from bs4 import BeautifulSoup

def fix_dash():
    with open('templates/dashboard.html', 'r', encoding='utf-8') as f:
        soup = BeautifulSoup(f.read(), 'html.parser')

    # 1. Fix "Good morning, Maria"
    h2 = soup.find('h2')
    if h2 and 'Good morning' in h2.text:
        h2.string = 'Good morning, {{ current_user.name.split()[0] if current_user.name else "User" }}'

    # 2. Fix DEMO badges
    # We want to remove DEMO DATA badges from real API-connected sections
    for badge in soup.find_all(class_='demo-badge'):
        text = badge.text.strip().upper()
        if text == 'DEMO DATA' or text == 'DEMO PATIENT':
            parent = badge.parent
            if parent:
                # keep DEMO DATA on "Overall Risk Indicator" if it's there
                if 'OVERALL RISK INDICATOR' not in parent.text and 'comp-header' not in parent.get('class', []):
                    badge.decompose()
    
    # Wait, the cards are:
    # 0: CURRENT GLUCOSE (real)
    # 1: AI PREDICTED (demo)
    # 2: 7-DAY AVG GLUCOSE (real)
    # 3: MENTAL WELLNESS (real)
    # 4: OVERALL RISK INDICATOR (demo)
    # 5: LAST CHECK-IN (real)
    
    # 3. Add proper IDs and remove static values
    cards = soup.select('.card-value')
    if len(cards) >= 6:
        # Current Glucose
        cards[0]['id'] = 'dash_current_glucose'
        cards[0].string = '-- '
        sp = soup.new_tag('span')
        sp.string = 'mg/dL'
        cards[0].append(sp)
        
        # 7-day Avg
        cards[2]['id'] = 'dash_today_avg'
        cards[2].string = '-- '
        sp = soup.new_tag('span')
        sp.string = 'mg/dL'
        cards[2].append(sp)

        # Mental Wellness
        cards[3]['id'] = 'dash_wellness'
        cards[3].string = '--'
        
        # Last checkin
        cards[5]['id'] = 'dash_last_checkin'
        cards[5].string = '--'

    # 4. Remove DEMO DATA from chart headers
    for chart_header in soup.find_all(class_='chart-title'):
        # wait, my layout might use different classes
        pass
        
    for h3 in soup.find_all('h3'):
        if h3.text and 'Glucose Timeline' in h3.text:
            badge = h3.parent.find(class_='demo-badge')
            if badge: badge.decompose()
        if h3.text and 'Recent Activity' in h3.text:
            badge = h3.parent.find(class_='demo-badge')
            if badge: badge.decompose()
            
    # Fix the JS logic for updating the other fields
    script = """
    document.addEventListener("DOMContentLoaded", function() {
        // Fetch summary
        fetch('/api/health/summary')
            .then(res => {
                if (res.status === 401) { window.location.href = '/login'; return null; }
                if (!res.ok) throw new Error('API Error');
                return res.json();
            })
            .then(data => {
                if (!data || !data.success) throw new Error('Invalid Data');
                
                const elCurrent = document.getElementById('dash_current_glucose');
                if (elCurrent && data.current_glucose !== null && data.current_glucose !== undefined) {
                    elCurrent.innerHTML = data.current_glucose + ' <span>mg/dL</span>';
                }
                
                const elAvg = document.getElementById('dash_today_avg');
                if (elAvg && data.weekly_average_glucose !== null && data.weekly_average_glucose !== undefined) {
                    elAvg.innerHTML = data.weekly_average_glucose + ' <span>mg/dL</span>';
                }

                const elWell = document.getElementById('dash_wellness');
                if (elWell && data.latest_mood) {
                    elWell.innerHTML = data.latest_stress < 5 ? "Stable" : "Elevated Stress";
                }
            })
            .catch(err => {
                const elCurrent = document.getElementById('dash_current_glucose');
                if (elCurrent) elCurrent.innerHTML = '<span style="font-size:14px; color:#ef4444;">Unable to load health data.</span>';
            });

        // Fetch recent
        fetch('/api/health-records/recent?limit=5')
            .then(res => {
                if(!res.ok) throw new Error('API error');
                return res.json();
            })
            .then(data => {
                const list = document.getElementById('dash_recent_records');
                if(!list) return;
                list.innerHTML = '';
                if(data.records && data.records.length > 0) {
                    const latest = data.records[0];
                    const elTime = document.getElementById('dash_last_checkin');
                    if(elTime) {
                        const t = new Date(latest.timestamp);
                        elTime.innerHTML = t.toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'}) + ' <span>today</span>';
                    }

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
                    list.innerHTML = `<div style="padding:20px; color:#64748b;">No health records yet. <br><br><a href="/monitoring" style="color:#3b82f6;">Add Daily Check-in</a></div>`;
                    const elTime = document.getElementById('dash_last_checkin');
                    if(elTime) elTime.innerHTML = '--';
                }
            })
            .catch(err => {
                const list = document.getElementById('dash_recent_records');
                if (list) list.innerHTML = '<div style="padding:20px; color:#ef4444;">Unable to load health data.</div>';
            });

        // Fetch chart data
        fetch('/api/glucose/history?days=7')
            .then(res => {
                if(!res.ok) throw new Error('API error');
                return res.json();
            })
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
            })
            .catch(err => {
                // handle chart error silently or gracefully
            });
    });
    
    function updateDashboardChart() {
        if(!window.dashChart) return;
        window.dashChart.data.labels = window.chartLabels;
        window.dashChart.data.datasets[0].data = window.actualData;
        window.dashChart.update();
    }
    """

    # We replace the old fetch logic block completely to fix the "Unable to load health data" and logic.
    # We can just remove the old script block that was injected and append the new one.
    old_scripts = soup.find_all('script')
    for s in old_scripts:
        if s.string and 'fetch(\'/api/health/summary\')' in s.string:
            s.decompose()
            
    new_script = soup.new_tag('script')
    new_script.string = script
    soup.body.append(new_script)
    
    with open('templates/dashboard.html', 'w', encoding='utf-8') as f:
        f.write(str(soup))

fix_dash()
print("Fixed dashboard.html")
