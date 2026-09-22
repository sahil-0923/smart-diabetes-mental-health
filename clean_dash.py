import re
from bs4 import BeautifulSoup

def clean_dashboard():
    with open('templates/dashboard.html', 'r', encoding='utf-8') as f:
        soup = BeautifulSoup(f.read(), 'html.parser')

    # Find the AI Forecast card
    # In my previous script, I knew it was card index 1 for AI, card index 4 for Risk
    cards = soup.select('.card-value')
    if len(cards) >= 6:
        ai_card = cards[1]
        if ai_card:
            ai_card.string = 'N/A'
            ai_card['style'] = 'color: var(--text-muted); font-size: 24px;'
            parent = ai_card.parent
            if parent:
                header = parent.find(class_='card-title')
                if header: header.string = 'AI FORECAST'
                badge = parent.find(class_='demo-badge')
                if badge: 
                    badge.string = 'NOT CONNECTED'
                    badge['style'] = 'background:#f1f5f9; color:#64748b; border-color:#cbd5e1;'
                
                # Find trend/subtext
                trend = parent.find(class_='card-trend')
                if trend:
                    trend.string = 'Model not connected yet.'
                    trend['style'] = 'color: var(--text-muted); font-size: 12px; margin-top: 4px;'
                
                footer = parent.find(class_='card-footer')
                if footer:
                    footer.string = 'Forecasting will become available after the GRU model is deployed.'

        risk_card = cards[4]
        if risk_card:
            risk_card.string = 'N/A'
            risk_card['style'] = 'color: var(--text-muted); font-size: 24px;'
            parent = risk_card.parent
            if parent:
                header = parent.find(class_='card-title')
                if header: header.string = 'RISK INDICATOR'
                badge = parent.find(class_='demo-badge')
                if badge: 
                    badge.string = 'NOT CONNECTED'
                    badge['style'] = 'background:#f1f5f9; color:#64748b; border-color:#cbd5e1;'
                
                footer = parent.find(class_='card-footer')
                if footer:
                    footer.string = 'Requires sufficient clinical data and validated models.'
                # Some other structural elements like card-trend might be in there, clear them if present
                trend = parent.find(class_='card-trend')
                if trend: trend.decompose()

    with open('templates/dashboard.html', 'w', encoding='utf-8') as f:
        f.write(str(soup))

clean_dashboard()
print("Dashboard cleaned of AI demo fallbacks.")
