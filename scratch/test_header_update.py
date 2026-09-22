import os
import sys
sys.path.insert(0, os.path.abspath("."))
from bs4 import BeautifulSoup
from app import app, db, User

def test_headers():
    print("=" * 80)
    print("TESTING HEADER UI UPDATE & ACCOUNT DROPDOWN")
    print("=" * 80)

    client = app.test_client()

    with app.app_context():
        user = User.query.filter_by(name="Rahul Kumar").first()
        if not user:
            print("Creating test user Rahul Kumar")
            user = User(
                name="Rahul Kumar",
                email="rahul.kumar@diabetesai.org",
                password="secure_password",
                age=42,
                profile_completed=True,
                onboarding_completed=True
            )
            db.session.add(user)
            db.session.commit()
            db.session.refresh(user)

        user_id = user.id
        user_name = user.name
        user_email = user.email

    with client.session_transaction() as sess:
        sess["user_id"] = user_id

    routes_to_test = [
        "/dashboard",
        "/glucose",
        "/monitoring",
        "/ai-forecast",
        "/simulator",
        "/risk-trends",
        "/health-trends",
        "/mental-wellness"
    ]

    for route in routes_to_test:
        resp = client.get(route)
        assert resp.status_code == 200, f"Failed on {route} with status {resp.status_code}"
        html = resp.data.decode("utf-8")
        soup = BeautifulSoup(html, "html.parser")

        # 1. Search Bar Removed
        assert "search-box" not in html, f"Found 'search-box' in {route}"
        assert "Search... ⌘K" not in html, f"Found 'Search...' in {route}"

        # 2. Emergency Button Removed
        assert "emergency-btn" not in html, f"Found 'emergency-btn' in {route}"
        assert "Emergency" not in [t.text.strip() for t in soup.find_all(class_="emergency-btn")], f"Found emergency text in {route}"

        # 3. Account Avatar Present
        avatar_btn = soup.find(id="accountAvatarBtn")
        assert avatar_btn is not None, f"Missing #accountAvatarBtn in {route}"
        assert avatar_btn.text.strip() == "RA", f"Avatar initials expected 'RA', got '{avatar_btn.text.strip()}' in {route}"

        # 4. Account Dropdown Present with exact user details
        dropdown = soup.find(id="accountDropdown")
        assert dropdown is not None, f"Missing #accountDropdown in {route}"
        
        user_name_el = dropdown.find(class_="dropdown-user-name")
        assert user_name_el is not None and user_name_el.text.strip() == user_name, f"Expected '{user_name}', got '{user_name_el.text.strip() if user_name_el else None}' in {route}"
        
        user_email_el = dropdown.find(class_="dropdown-user-email")
        assert user_email_el is not None and user_email_el.text.strip() == user_email, f"Expected '{user_email}', got '{user_email_el.text.strip() if user_email_el else None}' in {route}"

        # 5. Logout Link present inside dropdown
        logout_link = dropdown.find("a", href="/logout")
        assert logout_link is not None, f"Missing logout link in dropdown on {route}"

        print(f"[PASS] Route {route:<18}: Search=GONE, Emergency=GONE, Avatar='{avatar_btn.text.strip()}', User='{user_name_el.text.strip()}', Email='{user_email_el.text.strip()}'")

    print("\n" + "=" * 80)
    print("ALL 8 APPLICATION PAGES VERIFIED: CLEAN HEADER WITH ACCOUNT DROPDOWN")
    print("=" * 80)

if __name__ == "__main__":
    test_headers()
