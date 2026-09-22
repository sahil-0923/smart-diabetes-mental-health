import os
import sys
sys.path.insert(0, os.path.abspath("."))
from bs4 import BeautifulSoup
from app import app, db, User

def test_sidebar_and_top_account():
    print("=" * 80)
    print("TESTING CONSISTENT TOPBAR & SIDEBAR ACCOUNT MENUS")
    print("=" * 80)

    client = app.test_client()

    with app.app_context():
        user = User.query.filter_by(name="Rahul Kumar").first()
        if not user:
            print("Creating test user Rahul Kumar")
            user = User(
                name="Rahul Kumar",
                email="rahul.test2026@example.com",
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

        # 1. Top-Right Avatar & Dropdown Check
        top_btn = soup.find(id="accountAvatarBtn")
        assert top_btn is not None, f"Missing #accountAvatarBtn in {route}"
        assert top_btn.text.strip() == "RA", f"Top avatar expected 'RA', got '{top_btn.text.strip()}' in {route}"

        top_dd = soup.find(id="accountDropdown")
        assert top_dd is not None, f"Missing #accountDropdown in {route}"
        top_name = top_dd.find(class_="dropdown-user-name").text.strip()
        top_email = top_dd.find(class_="dropdown-user-email").text.strip()
        assert top_name == user_name, f"Top dropdown expected '{user_name}', got '{top_name}' in {route}"
        assert top_email == user_email, f"Top dropdown expected '{user_email}', got '{top_email}' in {route}"
        assert top_dd.find("a", href="/logout") is not None, f"Missing logout in top dropdown on {route}"

        # 2. Sidebar Avatar & Dropdown Check
        side_btn = soup.find(id="sidebarAccountBtn")
        assert side_btn is not None, f"Missing #sidebarAccountBtn in {route}"
        side_avatar = side_btn.find(class_="avatar")
        assert side_avatar is not None, f"Missing .avatar in sidebar in {route}"
        assert side_avatar.text.strip() == "RA", f"Sidebar avatar expected 'RA', got '{side_avatar.text.strip()}' in {route}"
        assert "MA" not in side_avatar.text.strip(), f"Found hardcoded 'MA' in sidebar on {route}"

        side_dd = soup.find(id="sidebarAccountDropdown")
        assert side_dd is not None, f"Missing #sidebarAccountDropdown in {route}"
        side_name = side_dd.find(class_="dropdown-user-name").text.strip()
        side_email = side_dd.find(class_="dropdown-user-email").text.strip()
        assert side_name == user_name, f"Sidebar dropdown expected '{user_name}', got '{side_name}' in {route}"
        assert side_email == user_email, f"Sidebar dropdown expected '{user_email}', got '{side_email}' in {route}"
        assert side_dd.find("a", href="/logout") is not None, f"Missing logout in sidebar dropdown on {route}"

        print(f"[PASS] Route {route:<18}: Top Avatar='{top_btn.text.strip()}', Sidebar Avatar='{side_avatar.text.strip()}', Name='{side_name}', Email='{side_email}', Logout=OK")

    print("\n" + "=" * 80)
    print("ALL 8 APPLICATION PAGES VERIFIED: 100% CONSISTENT TOP & SIDEBAR ACCOUNT UI")
    print("=" * 80)

if __name__ == "__main__":
    test_sidebar_and_top_account()
