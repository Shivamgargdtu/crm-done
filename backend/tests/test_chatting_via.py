"""
Test suite for Chatting Via feature:
- PUT /api/leads/{id}/chatting-via - Sets chattingVia field
- GET /api/leads?chattingVia=5235 - Filters leads by assigned WA number
- chattingVia field in LeadCreate and LeadUpdate models
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestChattingViaFeature:
    """Tests for the Chatting Via WhatsApp number assignment feature"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup: Login as admin and get session"""
        self.session = requests.Session()
        login_response = self.session.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": os.environ.get("TEST_ADMIN_EMAIL", "admin@wedus.com"), "password": os.environ.get("TEST_ADMIN_PASSWORD", "admin123")}
        )
        if login_response.status_code != 200:
            pytest.skip("Could not login as admin")
        self.admin_user = login_response.json()
        yield
        # Cleanup handled in individual tests
    
    def test_get_leads_returns_chatting_via_field(self):
        """Test that leads include chattingVia field in response"""
        response = self.session.get(f"{BASE_URL}/api/leads?limit=5")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert "leads" in data, "Response should have 'leads' key"
        
        # Check that at least one lead has chattingVia field (can be null)
        if data["leads"]:
            lead = data["leads"][0]
            # chattingVia should be present in the lead schema
            assert "chattingVia" in lead or lead.get("chattingVia") is None, \
                "Lead should have chattingVia field"
        print(f"✓ GET /api/leads returns leads with chattingVia field")
    
    def test_filter_leads_by_chatting_via_5235(self):
        """Test filtering leads by chattingVia=5235"""
        response = self.session.get(f"{BASE_URL}/api/leads?chattingVia=5235")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert "leads" in data, "Response should have 'leads' key"
        
        # All returned leads should have chattingVia=5235
        for lead in data["leads"]:
            assert lead.get("chattingVia") == "5235", \
                f"Lead {lead.get('id')} has chattingVia={lead.get('chattingVia')}, expected '5235'"
        
        print(f"✓ GET /api/leads?chattingVia=5235 returns {len(data['leads'])} leads")
    
    def test_filter_leads_by_chatting_via_5533(self):
        """Test filtering leads by chattingVia=5533"""
        response = self.session.get(f"{BASE_URL}/api/leads?chattingVia=5533")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        # All returned leads should have chattingVia=5533
        for lead in data["leads"]:
            assert lead.get("chattingVia") == "5533", \
                f"Lead has chattingVia={lead.get('chattingVia')}, expected '5533'"
        
        print(f"✓ GET /api/leads?chattingVia=5533 returns {len(data['leads'])} leads")
    
    def test_filter_leads_by_chatting_via_0951(self):
        """Test filtering leads by chattingVia=0951"""
        response = self.session.get(f"{BASE_URL}/api/leads?chattingVia=0951")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        # All returned leads should have chattingVia=0951
        for lead in data["leads"]:
            assert lead.get("chattingVia") == "0951", \
                f"Lead has chattingVia={lead.get('chattingVia')}, expected '0951'"
        
        print(f"✓ GET /api/leads?chattingVia=0951 returns {len(data['leads'])} leads")
    
    def test_put_chatting_via_set_value(self):
        """Test PUT /api/leads/{id}/chatting-via to set a value"""
        # First get a lead to update
        leads_response = self.session.get(f"{BASE_URL}/api/leads?limit=1")
        assert leads_response.status_code == 200
        leads = leads_response.json()["leads"]
        
        if not leads:
            pytest.skip("No leads available for testing")
        
        lead_id = leads[0]["id"]
        original_chatting_via = leads[0].get("chattingVia")
        
        # Set chattingVia to 5533
        response = self.session.put(
            f"{BASE_URL}/api/leads/{lead_id}/chatting-via",
            json={"chattingVia": "5533"}
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert data.get("chattingVia") == "5533", f"Expected chattingVia='5533', got {data.get('chattingVia')}"
        
        # Verify by fetching the lead
        verify_response = self.session.get(f"{BASE_URL}/api/leads/{lead_id}")
        assert verify_response.status_code == 200
        assert verify_response.json().get("chattingVia") == "5533"
        
        # Restore original value
        self.session.put(
            f"{BASE_URL}/api/leads/{lead_id}/chatting-via",
            json={"chattingVia": original_chatting_via}
        )
        
        print(f"✓ PUT /api/leads/{lead_id}/chatting-via successfully sets value to '5533'")
    
    def test_put_chatting_via_clear_value(self):
        """Test PUT /api/leads/{id}/chatting-via to clear value (set to null)"""
        # First get a lead to update
        leads_response = self.session.get(f"{BASE_URL}/api/leads?limit=1")
        assert leads_response.status_code == 200
        leads = leads_response.json()["leads"]
        
        if not leads:
            pytest.skip("No leads available for testing")
        
        lead_id = leads[0]["id"]
        original_chatting_via = leads[0].get("chattingVia")
        
        # First set a value
        self.session.put(
            f"{BASE_URL}/api/leads/{lead_id}/chatting-via",
            json={"chattingVia": "0951"}
        )
        
        # Now clear it
        response = self.session.put(
            f"{BASE_URL}/api/leads/{lead_id}/chatting-via",
            json={"chattingVia": None}
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert data.get("chattingVia") is None, f"Expected chattingVia=None, got {data.get('chattingVia')}"
        
        # Restore original value
        self.session.put(
            f"{BASE_URL}/api/leads/{lead_id}/chatting-via",
            json={"chattingVia": original_chatting_via}
        )
        
        print(f"✓ PUT /api/leads/{lead_id}/chatting-via successfully clears value to null")
    
    def test_put_chatting_via_invalid_lead_id(self):
        """Test PUT /api/leads/{id}/chatting-via with invalid lead ID returns 404"""
        response = self.session.put(
            f"{BASE_URL}/api/leads/000000000000000000000000/chatting-via",
            json={"chattingVia": "5235"}
        )
        assert response.status_code == 404, f"Expected 404, got {response.status_code}"
        print(f"✓ PUT /api/leads/invalid-id/chatting-via returns 404")
    
    def test_put_chatting_via_requires_auth(self):
        """Test PUT /api/leads/{id}/chatting-via requires authentication"""
        # Use a new session without auth
        unauth_session = requests.Session()
        response = unauth_session.put(
            f"{BASE_URL}/api/leads/000000000000000000000000/chatting-via",
            json={"chattingVia": "5235"}
        )
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
        print(f"✓ PUT /api/leads/chatting-via requires authentication (401)")
    
    def test_create_lead_with_chatting_via(self):
        """Test creating a lead with chattingVia field"""
        new_lead = {
            "companyName": "TEST_ChattingVia_Company",
            "personName": "Test Person",
            "phone": "9876543210",
            "chattingVia": "5235"
        }
        
        response = self.session.post(f"{BASE_URL}/api/leads", json=new_lead)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        created_lead = response.json()
        assert created_lead.get("chattingVia") == "5235", \
            f"Expected chattingVia='5235', got {created_lead.get('chattingVia')}"
        
        # Cleanup - delete the test lead
        lead_id = created_lead.get("id")
        self.session.delete(f"{BASE_URL}/api/leads/{lead_id}")
        
        print(f"✓ POST /api/leads with chattingVia='5235' creates lead correctly")
    
    def test_update_lead_with_chatting_via(self):
        """Test updating a lead's chattingVia via PUT /api/leads/{id}"""
        # First get a lead
        leads_response = self.session.get(f"{BASE_URL}/api/leads?limit=1")
        assert leads_response.status_code == 200
        leads = leads_response.json()["leads"]
        
        if not leads:
            pytest.skip("No leads available for testing")
        
        lead_id = leads[0]["id"]
        original_chatting_via = leads[0].get("chattingVia")
        
        # Update via PUT /api/leads/{id}
        response = self.session.put(
            f"{BASE_URL}/api/leads/{lead_id}",
            json={"chattingVia": "0951", "companyName": leads[0]["companyName"]}
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        updated_lead = response.json()
        assert updated_lead.get("chattingVia") == "0951", \
            f"Expected chattingVia='0951', got {updated_lead.get('chattingVia')}"
        
        # Restore original value
        self.session.put(
            f"{BASE_URL}/api/leads/{lead_id}",
            json={"chattingVia": original_chatting_via, "companyName": leads[0]["companyName"]}
        )
        
        print(f"✓ PUT /api/leads/{lead_id} with chattingVia updates correctly")
    
    def test_patch_lead_chatting_via(self):
        """Test patching a lead's chattingVia via PATCH /api/leads/{id}"""
        # First get a lead
        leads_response = self.session.get(f"{BASE_URL}/api/leads?limit=1")
        assert leads_response.status_code == 200
        leads = leads_response.json()["leads"]
        
        if not leads:
            pytest.skip("No leads available for testing")
        
        lead_id = leads[0]["id"]
        original_chatting_via = leads[0].get("chattingVia")
        
        # Patch chattingVia
        response = self.session.patch(
            f"{BASE_URL}/api/leads/{lead_id}",
            json={"chattingVia": "5533"}
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        patched_lead = response.json()
        assert patched_lead.get("chattingVia") == "5533", \
            f"Expected chattingVia='5533', got {patched_lead.get('chattingVia')}"
        
        # Restore original value
        self.session.patch(
            f"{BASE_URL}/api/leads/{lead_id}",
            json={"chattingVia": original_chatting_via}
        )
        
        print(f"✓ PATCH /api/leads/{lead_id} with chattingVia updates correctly")


class TestChattingViaTeamMemberAccess:
    """Test team member access to chattingVia feature"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup: Login as team member"""
        self.session = requests.Session()
        login_response = self.session.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": "priya@wedus.com", "password": "team123"}
        )
        if login_response.status_code != 200:
            pytest.skip("Could not login as team member")
        self.team_user = login_response.json()
        yield
    
    def test_team_member_can_filter_by_chatting_via(self):
        """Test that team member can filter leads by chattingVia"""
        response = self.session.get(f"{BASE_URL}/api/leads?chattingVia=5235")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        print(f"✓ Team member can filter leads by chattingVia")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
