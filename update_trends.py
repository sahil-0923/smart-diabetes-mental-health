import re
from bs4 import BeautifulSoup

def update_trends():
    with open('templates/health_trends.html', 'r', encoding='utf-8') as f:
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
    if len(stats) >= 4:
        stats[0]['id'] = 'trend_gluc'
        stats[1]['id'] = 'trend_sleep'
        stats[2]['id'] = 'trend_activity'
        stats[3]['id'] = 'trend_stress'
        for i in range(4):
            stats[i].string = '--'

    # Ensure the comparison select exists and has an ID
    selects = soup.select('select')
    for s in selects:
        if 'Glucose vs Sleep' in str(s):
            s['id'] = 'comparisonSelect'

    # Ensure the chart canvas exists and has an ID
    canvases = soup.select('canvas')
    if canvases:
        canvases[0]['id'] = 'chartT'

    # Add fetching script
    script_tag = soup.new_tag('script')
    script_tag.string = """
    document.addEventListener("DOMContentLoaded", function() {
        const timeSelect = document.getElementById('timeRangeSelect');
        if(timeSelect) timeSelect.addEventListener('change', fetchTrendsData);
        
        const compSelect = document.getElementById('comparisonSelect');
        if(compSelect) compSelect.addEventListener('change', renderChart);
        
        fetchTrendsData();
    });

    let trendChart = null;
    let trendDataStore = {};

    function fetchTrendsData() {
        const days = document.getElementById('timeRangeSelect') ? document.getElementById('timeRangeSelect').value : 7;
        
        // Show loading state
        if(!trendChart) {
            const ctx = document.getElementById('chartT');
            if(ctx && ctx.parentNode && !ctx.parentNode.querySelector('.loading-msg')) {
                const msg = document.createElement('div');
                msg.className = 'loading-msg';
                msg.style = 'position:absolute; top:45%; left:50%; transform:translate(-50%, -50%); color:#64748b; font-size:14px;';
                msg.innerText = 'Loading health data...';
                ctx.parentNode.style.position = 'relative';
                ctx.parentNode.appendChild(msg);
            }
        }

        fetch(`/api/health-trends?days=${days}`)
            .then(res => {
                if (res.status === 401) { window.location.href = '/login'; return null; }
                return res.json();
            })
            .then(data => {
                if(!data) return;

                const ctx = document.getElementById('chartT');
                const loadingMsg = ctx?.parentNode?.querySelector('.loading-msg');
                if(loadingMsg) loadingMsg.remove();

                if (data.records && data.records.length === 0) {
                    if(ctx && ctx.parentNode) {
                        ctx.parentNode.innerHTML = '<div style="padding:20px; color:#64748b; text-align:center; position:absolute; top:45%; left:50%; transform:translate(-50%, -50%);">No health trend data yet. <br><br><a href="/monitoring" style="color:#3b82f6;">Add Daily Check-in</a></div>';
                    }
                    return;
                }
                
                trendDataStore = data;
                
                // Update stats (averages)
                const avg = (arr) => arr && arr.length > 0 ? (arr.reduce((a,b)=>a+(parseFloat(b)||0), 0) / arr.length).toFixed(1) : '--';
                document.getElementById('trend_gluc').innerHTML = avg(data.glucose) + ' <span style="font-size:14px; color:var(--text-muted);">mg/dL</span>';
                document.getElementById('trend_sleep').innerHTML = avg(data.sleep) + ' <span style="font-size:14px; color:var(--text-muted);">h</span>';
                document.getElementById('trend_activity').innerHTML = avg(data.steps) + ' <span style="font-size:14px; color:var(--text-muted);">steps</span>';
                document.getElementById('trend_stress').innerHTML = avg(data.stress) + ' <span style="font-size:14px; color:var(--text-muted);">/10</span>';
                
                renderChart();
            })
            .catch(err => {
                const ctx = document.getElementById('chartT');
                if(ctx && ctx.parentNode) ctx.parentNode.innerHTML = '<div style="color:#ef4444; padding:20px; position:absolute; top:45%; left:50%; transform:translate(-50%, -50%);">Unable to load health data. <button onclick="fetchTrendsData()" style="margin-left:10px; cursor:pointer;">Retry</button></div>';
            });
    }

    function renderChart() {
        if (!trendDataStore || !trendDataStore.labels) return;
        
        const ctx = document.getElementById('chartT');
        if(!ctx) return;

        const compSelect = document.getElementById('comparisonSelect');
        const mode = compSelect ? compSelect.value : 'Glucose vs Sleep';

        let secondData = trendDataStore.sleep;
        let secondLabel = 'Sleep (hours)';
        let secondColor = '#8b5cf6';
        let secondMax = 12;

        if(mode.includes('Activity') || mode.includes('Steps')) {
            secondData = trendDataStore.steps;
            secondLabel = 'Steps';
            secondColor = '#10b981';
            secondMax = 15000;
        } else if(mode.includes('Stress')) {
            secondData = trendDataStore.stress;
            secondLabel = 'Stress (0-10)';
            secondColor = '#ef4444';
            secondMax = 10;
        }

        if(trendChart) {
            trendChart.data.labels = trendDataStore.labels;
            trendChart.data.datasets[0].data = trendDataStore.glucose;
            trendChart.data.datasets[1].data = secondData;
            trendChart.data.datasets[1].label = secondLabel;
            trendChart.data.datasets[1].borderColor = secondColor;
            trendChart.options.scales.y1.suggestedMax = secondMax;
            trendChart.update();
        } else {
            trendChart = new Chart(ctx, {
                type: 'line', 
                data: { 
                    labels: trendDataStore.labels, 
                    datasets: [
                        { label: 'Glucose (mg/dL)', data: trendDataStore.glucose, borderColor: '#3b82f6', tension: 0.4, yAxisID: 'y' },
                        { label: secondLabel, data: secondData, borderColor: secondColor, tension: 0.4, yAxisID: 'y1' }
                    ] 
                },
                options: { 
                    responsive: true, 
                    maintainAspectRatio: false,
                    scales: {
                        y: { type: 'linear', display: true, position: 'left', suggestedMin: 70, suggestedMax: 200 },
                        y1: { type: 'linear', display: true, position: 'right', suggestedMin: 0, suggestedMax: secondMax, grid: { drawOnChartArea: false } }
                    }
                }
            });
        }
    }
    """

    for s in soup.find_all('script'):
        if s.string and 'Chart' in s.string:
            s.decompose()

    soup.body.append(script_tag)
    
    with open('templates/health_trends.html', 'w', encoding='utf-8') as f:
        f.write(str(soup))
    print("Updated health_trends.html")

update_trends()
