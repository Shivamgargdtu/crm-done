"""
Backend tests for new features:
1. WhatsApp Templates CRUD
2. Calendar API
3. Reminders API
"""
import pytest
import requests
import os
from datetime import datetime, timedelta

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://nuptial-pipeline.preview.emergentagent.com')

# Test credentials from environment
ADMIN_EMAIL = os.environ.get("TEST_ADMIN_EMAIL", "admin@wedus.com")
ADMIN_PASSWORD = os.environ.get("TEST_ADMIN_PASSWORD", "admin123")
TEAM_EMAIL = os.environ.get("TEST_TEAM_EMAIL", "priya@wedus.com")
TEAM_PASSWORD = os.environ.get("TEST_TEAM_PASSWORD", "team123")


class TestAuth:
    """Helper class for authentication"""
    
    @staticmethod
    def login(email, password):
        """Login and return session with cookies"""
        session = requests.Session()
        response = session.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": email, "password": password}
        )
        return session, response


class TestTemplatesAPI:
    """Tests for WhatsApp Templates CRUD endpoints"""
    
    def test_get_templates_returns_seeded_templates(self):
        """GET /api/templates - Returns list of seeded templates"""
        session, login_resp = TestAuth.login(ADMIN_EMAIL, ADMIN_PASSWORD)
        assert login_resp.status_code == 200, f"Login failed: {login_resp.text}"
        
        response = session.get(f"{BASE_URL}/api/templates")
        assert response.status_code == 200, f"Failed to get templates: {response.text}"
        
        templates = response.json()
        assert isinstance(templates, list), "Templates should be a list"
        assert len(templates) >= 8, f"Expected at least 8 seeded templates, got {len(templates)}"
        
        # Verify template structure
        for tmpl in templates:
            assert "id" in tmpl, "Template should have id"
            assert "name" in tmpl, "Template should have name"
            assert "message" in tmpl, "Template should have message"
            assert "category" in tmpl, "Template should have category"
        
        print(f"SUCCESS: GET /api/templates returned {len(templates)} templates")
    
    def test_get_templates_requires_auth(self):
        """GET /api/templates - Requires authentication"""
        response = requests.get(f"{BASE_URL}/api/templates")
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
        print("SUCCESS: GET /api/templates requires authentication")
    
    def test_admin_can_create_template(self):
        """POST /api/templates - Admin can create template"""
        session, login_resp = TestAuth.login(ADMIN_EMAIL, ADMIN_PASSWORD)
        assert login_resp.status_code == 200
        
        new_template = {
            "name": "TEST_Template_Create",
            "message": "Hello {company}! This is a test template.",
            "category": "General"
        }
        
        response = session.post(f"{BASE_URL}/api/templates", json=new_template)
        assert response.status_code == 200, f"Failed to create template: {response.text}"
        
        created = response.json()
        assert created["name"] == new_template["name"]
        assert created["message"] == new_template["message"]
        assert created["category"] == new_template["category"]
        assert "id" in created
        
        # Cleanup
        session.delete(f"{BASE_URL}/api/templates/{created['id']}")
        
        print("SUCCESS: Admin can create template")
    
    def test_team_member_cannot_create_template(self):
        """POST /api/templates - Team member gets 403"""
        session, login_resp = TestAuth.login(TEAM_EMAIL, TEAM_PASSWORD)
        assert login_resp.status_code == 200
        
        new_template = {
            "name": "TEST_Unauthorized_Template",
            "message": "This should fail",
            "category": "General"
        }
        
        response = session.post(f"{BASE_URL}/api/templates", json=new_template)
        assert response.status_code == 403, f"Expected 403, got {response.status_code}: {response.text}"
        
        print("SUCCESS: Team member cannot create template (403)")
    
    def test_admin_can_update_template(self):
        """PUT /api/templates/{id} - Admin can edit template"""
        session, login_resp = TestAuth.login(ADMIN_EMAIL, ADMIN_PASSWORD)
        assert login_resp.status_code == 200
        
        # Create a template first
        new_template = {
            "name": "TEST_Template_Update",
            "message": "Original message",
            "category": "General"
        }
        create_resp = session.post(f"{BASE_URL}/api/templates", json=new_template)
        assert create_resp.status_code == 200
        template_id = create_resp.json()["id"]
        
        # Update it
        update_data = {
            "name": "TEST_Template_Updated",
            "message": "Updated message with {company}",
            "category": "Follow-up"
        }
        update_resp = session.put(f"{BASE_URL}/api/templates/{template_id}", json=update_data)
        assert update_resp.status_code == 200, f"Failed to update: {update_resp.text}"
        
        updated = update_resp.json()
        assert updated["name"] == update_data["name"]
        assert updated["message"] == update_data["message"]
        assert updated["category"] == update_data["category"]
        
        # Cleanup
        session.delete(f"{BASE_URL}/api/templates/{template_id}")
        
        print("SUCCESS: Admin can update template")
    
    def test_admin_can_delete_template(self):
        """DELETE /api/templates/{id} - Admin can delete template"""
        session, login_resp = TestAuth.login(ADMIN_EMAIL, ADMIN_PASSWORD)
        assert login_resp.status_code == 200
        
        # Create a template first
        new_template = {
            "name": "TEST_Template_Delete",
            "message": "To be deleted",
            "category": "General"
        }
        create_resp = session.post(f"{BASE_URL}/api/templates", json=new_template)
        assert create_resp.status_code == 200
        template_id = create_resp.json()["id"]
        
        # Delete it
        delete_resp = session.delete(f"{BASE_URL}/api/templates/{template_id}")
        assert delete_resp.status_code == 200, f"Failed to delete: {delete_resp.text}"
        
        # Verify it's gone
        get_resp = session.get(f"{BASE_URL}/api/templates")
        templates = get_resp.json()
        template_ids = [t["id"] for t in templates]
        assert template_id not in template_ids, "Template should be deleted"
        
        print("SUCCESS: Admin can delete template")
    
    def test_team_member_cannot_delete_template(self):
        """DELETE /api/templates/{id} - Team member gets 403"""
        # First create a template as admin
        admin_session, _ = TestAuth.login(ADMIN_EMAIL, ADMIN_PASSWORD)
        create_resp = admin_session.post(f"{BASE_URL}/api/templates", json={
            "name": "TEST_NoDelete",
            "message": "Team cannot delete",
            "category": "General"
        })
        template_id = create_resp.json()["id"]
        
        # Try to delete as team member
        team_session, _ = TestAuth.login(TEAM_EMAIL, TEAM_PASSWORD)
        delete_resp = team_session.delete(f"{BASE_URL}/api/templates/{template_id}")
        assert delete_resp.status_code == 403, f"Expected 403, got {delete_resp.status_code}"
        
        # Cleanup as admin
        admin_session.delete(f"{BASE_URL}/api/templates/{template_id}")
        
        print("SUCCESS: Team member cannot delete template (403)")


class TestCalendarAPI:
    """Tests for Calendar endpoint"""
    
    def test_get_calendar_events_current_month(self):
        """GET /api/calendar?month=M&year=YYYY - Returns events for month"""
        session, login_resp = TestAuth.login(ADMIN_EMAIL, ADMIN_PASSWORD)
        assert login_resp.status_code == 200
        
        now = datetime.now()
        response = session.get(f"{BASE_URL}/api/calendar?month={now.month}&year={now.year}")
        assert response.status_code == 200, f"Failed: {response.text}"
        
        events = response.json()
        assert isinstance(events, list), "Events should be a list"
        
        # Verify event structure if any exist
        for event in events:
            assert "id" in event, "Event should have id"
            assert "eventType" in event, "Event should have eventType"
            assert "eventDate" in event, "Event should have eventDate"
            assert event["eventType"] in ["followup", "meeting"], f"Invalid eventType: {event['eventType']}"
        
        print(f"SUCCESS: GET /api/calendar returned {len(events)} events for {now.month}/{now.year}")
    
    def test_get_calendar_events_specific_month(self):
        """GET /api/calendar?month=4&year=2026 - Returns events for April 2026"""
        session, login_resp = TestAuth.login(ADMIN_EMAIL, ADMIN_PASSWORD)
        assert login_resp.status_code == 200
        
        response = session.get(f"{BASE_URL}/api/calendar?month=4&year=2026")
        assert response.status_code == 200, f"Failed: {response.text}"
        
        events = response.json()
        assert isinstance(events, list)
        
        print(f"SUCCESS: GET /api/calendar?month=4&year=2026 returned {len(events)} events")
    
    def test_calendar_requires_auth(self):
        """GET /api/calendar - Requires authentication"""
        response = requests.get(f"{BASE_URL}/api/calendar?month=4&year=2026")
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
        print("SUCCESS: GET /api/calendar requires authentication")
    
    def test_calendar_validates_month_range(self):
        """GET /api/calendar - Validates month parameter"""
        session, login_resp = TestAuth.login(ADMIN_EMAIL, ADMIN_PASSWORD)
        assert login_resp.status_code == 200
        
        # Invalid month (13)
        response = session.get(f"{BASE_URL}/api/calendar?month=13&year=2026")
        assert response.status_code == 422, f"Expected 422 for invalid month, got {response.status_code}"
        
        # Invalid month (0)
        response = session.get(f"{BASE_URL}/api/calendar?month=0&year=2026")
        assert response.status_code == 422, f"Expected 422 for month=0, got {response.status_code}"
        
        print("SUCCESS: Calendar validates month range")


class TestRemindersAPI:
    """Tests for Reminders endpoint"""
    
    def test_get_reminders_returns_structure(self):
        """GET /api/reminders - Returns overdue/today/tomorrow/thisWeek arrays"""
        session, login_resp = TestAuth.login(ADMIN_EMAIL, ADMIN_PASSWORD)
        assert login_resp.status_code == 200
        
        response = session.get(f"{BASE_URL}/api/reminders")
        assert response.status_code == 200, f"Failed: {response.text}"
        
        data = response.json()
        
        # Verify structure
        assert "overdue" in data, "Response should have 'overdue' array"
        assert "today" in data, "Response should have 'today' array"
        assert "tomorrow" in data, "Response should have 'tomorrow' array"
        assert "thisWeek" in data, "Response should have 'thisWeek' array"
        assert "counts" in data, "Response should have 'counts' object"
        
        # Verify counts structure
        counts = data["counts"]
        assert "overdue" in counts, "Counts should have 'overdue'"
        assert "today" in counts, "Counts should have 'today'"
        assert "tomorrow" in counts, "Counts should have 'tomorrow'"
        assert "thisWeek" in counts, "Counts should have 'thisWeek'"
        
        # Verify arrays are lists
        assert isinstance(data["overdue"], list)
        assert isinstance(data["today"], list)
        assert isinstance(data["tomorrow"], list)
        assert isinstance(data["thisWeek"], list)
        
        # Verify counts match array lengths
        assert counts["overdue"] == len(data["overdue"])
        assert counts["today"] == len(data["today"])
        assert counts["tomorrow"] == len(data["tomorrow"])
        assert counts["thisWeek"] == len(data["thisWeek"])
        
        print(f"SUCCESS: GET /api/reminders - overdue:{counts['overdue']}, today:{counts['today']}, tomorrow:{counts['tomorrow']}, thisWeek:{counts['thisWeek']}")
    
    def test_reminders_requires_auth(self):
        """GET /api/reminders - Requires authentication"""
        response = requests.get(f"{BASE_URL}/api/reminders")
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
        print("SUCCESS: GET /api/reminders requires authentication")
    
    def test_reminders_lead_structure(self):
        """GET /api/reminders - Leads have required fields"""
        session, login_resp = TestAuth.login(ADMIN_EMAIL, ADMIN_PASSWORD)
        assert login_resp.status_code == 200
        
        response = session.get(f"{BASE_URL}/api/reminders")
        assert response.status_code == 200
        
        data = response.json()
        
        # Check any leads in any category
        all_leads = data["overdue"] + data["today"] + data["tomorrow"] + data["thisWeek"]
        
        for lead in all_leads:
            assert "id" in lead, "Lead should have id"
            assert "companyName" in lead or lead.get("companyName") is None, "Lead should have companyName field"
            assert "nextFollowupDate" in lead, "Lead should have nextFollowupDate"
        
        print(f"SUCCESS: Reminders leads have correct structure ({len(all_leads)} total leads)")


class TestTeamMemberAccess:
    """Tests for team member access restrictions"""
    
    def test_team_member_can_view_templates(self):
        """Team member can view templates (read-only)"""
        session, login_resp = TestAuth.login(TEAM_EMAIL, TEAM_PASSWORD)
        assert login_resp.status_code == 200
        
        response = session.get(f"{BASE_URL}/api/templates")
        assert response.status_code == 200, f"Team member should be able to view templates: {response.text}"
        
        templates = response.json()
        assert len(templates) >= 8
        
        print("SUCCESS: Team member can view templates")
    
    def test_team_member_can_view_calendar(self):
        """Team member can view calendar"""
        session, login_resp = TestAuth.login(TEAM_EMAIL, TEAM_PASSWORD)
        assert login_resp.status_code == 200
        
        now = datetime.now()
        response = session.get(f"{BASE_URL}/api/calendar?month={now.month}&year={now.year}")
        assert response.status_code == 200, f"Team member should be able to view calendar: {response.text}"
        
        print("SUCCESS: Team member can view calendar")
    
    def test_team_member_can_view_reminders(self):
        """Team member can view reminders"""
        session, login_resp = TestAuth.login(TEAM_EMAIL, TEAM_PASSWORD)
        assert login_resp.status_code == 200
        
        response = session.get(f"{BASE_URL}/api/reminders")
        assert response.status_code == 200, f"Team member should be able to view reminders: {response.text}"
        
        print("SUCCESS: Team member can view reminders")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
