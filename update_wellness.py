import re
from bs4 import BeautifulSoup

def update_wellness():
    with open('templates/mental_wellness.html', 'r', encoding='utf-8') as f:
        soup = BeautifulSoup(f.read(), 'html.parser')
    
    # 1. Update Header to add Time Range Selector and remove DEMO badge
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

    # Add IDs to stat values
    stats = soup.select('.stat-value')
    if len(stats) >= 3:
        stats[0]['id'] = 'well_stress'
        stats[1]['id'] = 'well_sleep'
        stats[2]['id'] = 'well_mood'
        for i in range(3):
            stats[i].string = '--'

    # Add fetching script
    script_tag = soup.new_tag('script')
    script_tag.string = """
    document.addEventListener("DOMContentLoaded", function() {
        const timeSelect = document.getElementById('timeRangeSelect');
        if(timeSelect) {
            timeSelect.addEventListener('change', fetchWellnessData);
        }
        fetchWellnessData();
    });

    let wellChart = null;

    function fetchWellnessData() {
        const days = document.getElementById('timeRangeSelect') ? document.getElementById('timeRangeSelect').value : 7;
        
        fetch(`/api/wellness/history?days=${days}`)
            .then(res => {
                if (res.status === 401) { window.location.href = '/login'; return null; }
                return res.json();
            })
            .then(data => {
                if(!data) return;

                if (data.records && data.records.length === 0) {
                    const ctx = document.getElementById('chartW');
                    if(ctx && ctx.parentNode) {
                        ctx.parentNode.innerHTML = '<div style="padding:20px; color:#64748b; text-align:center;">No wellness records yet. <br><br><a href="/monitoring" style="color:#3b82f6;">Add Daily Check-in</a></div>';
                    }
                    return;
                }
                
                // Update stats if we have values
                if (data.stress && data.stress.length > 0) {
                    document.getElementById('well_stress').innerText = (data.stress[data.stress.length-1] || '--') + ' / 10';
                    document.getElementById('well_sleep').innerText = (data.sleep[data.sleep.length-1] || '--') + ' h';
                    document.getElementById('well_mood').innerText = (data.mood[data.mood.length-1] || '--') + ' / 10';
                }
                
                // Update chart
                updateChart(data.labels || [], data.stress || [], data.sleep || []);
            })
            .catch(err => {
                const ctx = document.getElementById('chartW');
                if(ctx && ctx.parentNode) ctx.parentNode.innerHTML = '<div style="color:#ef4444; padding:20px;">Unable to load health data. <button onclick="fetchWellnessData()" style="margin-left:10px; cursor:pointer;">Retry</button></div>';
            });
    }

    function updateChart(labels, stressData, sleepData) {
        const ctx = document.getElementById('chartW');
        if(!ctx) return; // if it was replaced by empty state

        if(wellChart) {
            wellChart.data.labels = labels;
            wellChart.data.datasets[0].data = stressData;
            wellChart.data.datasets[1].data = sleepData;
            wellChart.update();
        } else {
            wellChart = new Chart(ctx, {
                type: 'line', 
                data: { 
                    labels: labels, 
                    datasets: [
                        { label: 'Stress (0-10)', data: stressData, borderColor: '#ef4444', tension: 0.4, yAxisID: 'y' },
                        { label: 'Sleep (hours)', data: sleepData, borderColor: '#8b5cf6', tension: 0.4, yAxisID: 'y1' }
                    ] 
                },
                options: { 
                    responsive: true, 
                    maintainAspectRatio: false,
                    scales: {
                        y: { type: 'linear', display: true, position: 'left', suggestedMin: 0, suggestedMax: 10 },
                        y1: { type: 'linear', display: true, position: 'right', suggestedMin: 0, suggestedMax: 12, grid: { drawOnChartArea: false } }
                    }
                }
            });
        }
    }
    """

    for s in soup.find_all('script'):
        if s.string and 'chartW' in s.string:
            s.decompose()

    soup.body.append(script_tag)
    
    with open('templates/mental_wellness.html', 'w', encoding='utf-8') as f:
        f.write(str(soup))
    print("Updated mental_wellness.html")

update_wellness()
