import re
from bs4 import BeautifulSoup

def update_glucose():
    with open('templates/glucose.html', 'r', encoding='utf-8') as f:
        soup = BeautifulSoup(f.read(), 'html.parser')
    
    # 1. Update Header to add Time Range Selector and remove DEMO badge from active pages
    header_title = soup.select_one('.header-title')
    if header_title:
        demo_badge = header_title.find('span', class_='demo-badge')
        if demo_badge: demo_badge.decompose()
        header_div = header_title.parent
        parent_div = header_div.parent
        parent_div['style'] = 'display:flex; justify-content:space-between; align-items:center;'
        
        select_html = BeautifulSoup('<select id="timeRangeSelect" class="input-std" style="width:auto;"><option value="7">Last 7 Days</option><option value="14">Last 14 Days</option><option value="30">Last 30 Days</option><option value="90">Last 90 Days</option></select>', 'html.parser')
        parent_div.append(select_html)

    # Remove info-box demo warning
    info_box = soup.select_one('.info-box')
    if info_box: info_box.decompose()

    # 2. Add IDs to stat values
    stats = soup.select('.stat-value')
    if len(stats) >= 4:
        stats[0]['id'] = 'gluc_current'
        stats[1]['id'] = 'gluc_avg'
        stats[2]['id'] = 'gluc_highest'
        stats[3]['id'] = 'gluc_lowest'
        for i in range(4):
            stats[i].string = '-- '
            sp = soup.new_tag('span')
            sp.string = 'mg/dL'
            sp['style'] = 'font-size:14px; color:var(--text-muted);'
            stats[i].append(sp)

    # Trend box
    trend_box = soup.find(lambda t: t.name == 'h3' and 'Glucose Trend' in t.text)
    if trend_box:
        tdiv = trend_box.find_next_sibling('div')
        if tdiv: tdiv['id'] = 'gluc_trend'
        pdiv = tdiv.find_next_sibling('p')
        if pdiv: pdiv['id'] = 'gluc_trend_desc'

    # Recent Table
    table = soup.select_one('.table')
    if table:
        table['id'] = 'gluc_recent_table'
        table.clear()
        loading_row = soup.new_tag('tr')
        loading_td = soup.new_tag('td')
        loading_td['colspan'] = '3'
        loading_td.string = 'Loading health data...'
        loading_row.append(loading_td)
        table.append(loading_row)

    # 3. Add fetching script
    script_tag = soup.new_tag('script')
    script_tag.string = """
    document.addEventListener("DOMContentLoaded", function() {
        const timeSelect = document.getElementById('timeRangeSelect');
        if(timeSelect) {
            timeSelect.addEventListener('change', fetchGlucoseData);
        }
        fetchGlucoseData();
        fetchRecentReadings();
    });

    function fetchGlucoseData() {
        const days = document.getElementById('timeRangeSelect') ? document.getElementById('timeRangeSelect').value : 7;
        
        // Fetch history
        fetch(`/api/glucose/history?days=${days}`)
            .then(res => {
                if (res.status === 401) { window.location.href = '/login'; return null; }
                return res.json();
            })
            .then(data => {
                if(!data) return;
                
                // Update stats
                document.getElementById('gluc_current').innerHTML = (data.statistics?.current || '--') + ' <span style="font-size:14px; color:var(--text-muted);">mg/dL</span>';
                document.getElementById('gluc_avg').innerHTML = (data.statistics?.average || '--') + ' <span style="font-size:14px; color:var(--text-muted);">mg/dL</span>';
                document.getElementById('gluc_highest').innerHTML = (data.statistics?.highest || '--') + ' <span style="font-size:14px; color:var(--text-muted);">mg/dL</span>';
                document.getElementById('gluc_lowest').innerHTML = (data.statistics?.lowest || '--') + ' <span style="font-size:14px; color:var(--text-muted);">mg/dL</span>';
                
                // Update chart
                updateChart(data.labels || [], data.values || []);
            });

        // Fetch trend
        fetch(`/api/glucose/trend?days=${days}`)
            .then(res => res.json())
            .then(data => {
                const elTrend = document.getElementById('gluc_trend');
                const elDesc = document.getElementById('gluc_trend_desc');
                if(!elTrend || !elDesc) return;
                if(data.records_used < 2) {
                    elTrend.innerHTML = 'Insufficient Data';
                    elTrend.style.color = 'var(--text-muted)';
                    elDesc.innerText = 'Log more check-ins to see your trend.';
                    return;
                }
                if(data.trend === 'increasing') {
                    elTrend.innerHTML = '↑ Increasing';
                    elTrend.style.color = '#ef4444';
                    elDesc.innerText = `Your glucose is trending higher by approx ${Math.abs(data.change)} mg/dL on average over this period.`;
                } else if(data.trend === 'decreasing') {
                    elTrend.innerHTML = '↓ Decreasing';
                    elTrend.style.color = '#10b981';
                    elDesc.innerText = `Your glucose is trending lower by approx ${Math.abs(data.change)} mg/dL on average over this period.`;
                } else {
                    elTrend.innerHTML = '→ Stable';
                    elTrend.style.color = '#f59e0b';
                    elDesc.innerText = `Your glucose is relatively stable over this period.`;
                }
            });
    }

    function fetchRecentReadings() {
        fetch('/api/health-records/recent?limit=5')
            .then(res => res.json())
            .then(data => {
                const table = document.getElementById('gluc_recent_table');
                if(!table) return;
                table.innerHTML = '<tr><th>Time</th><th>Glucose</th><th>Context</th></tr>';
                if(data.records && data.records.length > 0) {
                    data.records.forEach(r => {
                        table.innerHTML += `
                            <tr>
                                <td>${new Date(r.timestamp).toLocaleString([], {month:'short', day:'numeric', hour: '2-digit', minute:'2-digit'})}</td>
                                <td style="font-weight:600;">${r.glucose}</td>
                                <td><span style="color:#64748b;">${r.meal_context || 'Random'}</span></td>
                            </tr>
                        `;
                    });
                } else {
                    table.innerHTML += `<tr><td colspan="3" style="text-align:center; color:#64748b;">No glucose records yet.</td></tr>`;
                }
            });
    }

    let glucChart = null;
    function updateChart(labels, data) {
        const ctx = document.getElementById('chartG');
        if(glucChart) {
            glucChart.data.labels = labels;
            glucChart.data.datasets[0].data = data;
            glucChart.update();
        } else {
            glucChart = new Chart(ctx, {
                type: 'line', 
                data: { 
                    labels: labels, 
                    datasets: [{ 
                        label: 'Glucose (mg/dL)', 
                        data: data, 
                        borderColor: '#3b82f6', 
                        tension: 0.4, 
                        fill: true, 
                        backgroundColor: 'rgba(59,130,246,0.1)' 
                    }] 
                },
                options: { 
                    responsive: true, 
                    maintainAspectRatio: false, 
                    plugins: { legend: { display: false } },
                    scales: { y: { suggestedMin: 70, suggestedMax: 200 } }
                }
            });
        }
    }
    """

    for s in soup.find_all('script'):
        if s.string and 'chartG' in s.string:
            s.decompose()

    soup.body.append(script_tag)
    
    with open('templates/glucose.html', 'w', encoding='utf-8') as f:
        f.write(str(soup))
    print("Updated glucose.html")

update_glucose()
