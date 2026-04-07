"""
Test Settings Feature - Profile, Password, and App Settings endpoints
Tests for: PUT /api/auth/profile, PUT /api/auth/password, GET /api/settings, PUT /api/settings
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')
if not BASE_URL:
    BASE_URL = "https://nuptial-pipeline.preview.emergentagent.com"

# Test credentials from environment
ADMIN_EMAIL = os.environ.get("TEST_ADMIN_EMAIL", "admin@wedus.com")
ADMIN_PASSWORD = os.environ.get("TEST_ADMIN_PASSWORD", "admin123")
TEAM_EMAIL = os.environ.get("TEST_TEAM_EMAIL", "priya@wedus.com")
TEAM_PASSWORD = os.environ.get("TEST_TEAM_PASSWORD", "team123")


class TestAuthProfile:
    """Tests for PUT /api/auth/profile - Update name, email, color"""
    
    @pytest.fixture
    def admin_session(self):
        """Login as admin and return session with cookies"""
        session = requests.Session()
        response = session.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        assert response.status_code == 200, f"Admin login failed: {response.text}"
        return session
    
    @pytest.fixture
    def team_session(self):
        """Login as team member and return session with cookies"""
        session = requests.Session()
        response = session.post(f"{BASE_URL}/api/auth/login", json={
            "email": TEAM_EMAIL,
            "password": TEAM_PASSWORD
        })
        assert response.status_code == 200, f"Team login failed: {response.text}"
        return session
    
    def test_update_profile_name(self, admin_session):
        """Test updating user name"""
        # Get current user info
        me_response = admin_session.get(f"{BASE_URL}/api/auth/me")
        assert me_response.status_code == 200
        original_name = me_response.json().get("name")
        
        # Update name
        new_name = "Admin Updated"
        response = admin_session.put(f"{BASE_URL}/api/auth/profile", json={
            "name": new_name
        })
        assert response.status_code == 200, f"Profile update failed: {response.text}"
        data = response.json()
        assert data.get("name") == new_name
        
        # Verify via GET /api/auth/me
        me_response = admin_session.get(f"{BASE_URL}/api/auth/me")
        assert me_response.status_code == 200
        assert me_response.json().get("name") == new_name
        
        # Restore original name
        admin_session.put(f"{BASE_URL}/api/auth/profile", json={"name": original_name or "Admin"})
        print("✓ Profile name update works correctly")
    
    def test_update_profile_color(self, admin_session):
        """Test updating user display color"""
        new_color = "#3B82F6"
        response = admin_session.put(f"{BASE_URL}/api/auth/profile", json={
            "color": new_color
        })
        assert response.status_code == 200, f"Color update failed: {response.text}"
        data = response.json()
        assert data.get("color") == new_color
        
        # Restore original color
        admin_session.put(f"{BASE_URL}/api/auth/profile", json={"color": "#E8536A"})
        print("✓ Profile color update works correctly")
    
    def test_update_profile_reject_duplicate_email(self, admin_session):
        """Test that duplicate email is rejected"""
        # Try to change admin email to team member's email
        response = admin_session.put(f"{BASE_URL}/api/auth/profile", json={
            "email": TEAM_EMAIL
        })
        assert response.status_code == 400, f"Expected 400 for duplicate email, got {response.status_code}"
        assert "already in use" in response.json().get("detail", "").lower() or "email" in response.json().get("detail", "").lower()
        print("✓ Duplicate email correctly rejected")
    
    def test_update_profile_no_changes(self, admin_session):
        """Test that no changes returns 400"""
        response = admin_session.put(f"{BASE_URL}/api/auth/profile", json={})
        assert response.status_code == 400, f"Expected 400 for no changes, got {response.status_code}"
        print("✓ No changes correctly returns 400")
    
    def test_team_member_can_update_profile(self, team_session):
        """Test that team members can also update their profile"""
        # Get current info
        me_response = team_session.get(f"{BASE_URL}/api/auth/me")
        assert me_response.status_code == 200
        original_name = me_response.json().get("name")
        
        # Update name
        new_name = "Priya Updated"
        response = team_session.put(f"{BASE_URL}/api/auth/profile", json={
            "name": new_name
        })
        assert response.status_code == 200, f"Team profile update failed: {response.text}"
        
        # Restore
        team_session.put(f"{BASE_URL}/api/auth/profile", json={"name": original_name or "Priya Sharma"})
        print("✓ Team member can update profile")


class TestAuthPassword:
    """Tests for PUT /api/auth/password - Change password"""
    
    @pytest.fixture
    def admin_session(self):
        """Login as admin and return session with cookies"""
        session = requests.Session()
        response = session.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        assert response.status_code == 200, f"Admin login failed: {response.text}"
        return session
    
    def test_change_password_wrong_current(self, admin_session):
        """Test that wrong current password is rejected"""
        response = admin_session.put(f"{BASE_URL}/api/auth/password", json={
            "currentPassword": "wrongpassword",
            "newPassword": "newpass123"
        })
        assert response.status_code == 400, f"Expected 400 for wrong password, got {response.status_code}"
        assert "incorrect" in response.json().get("detail", "").lower() or "current" in response.json().get("detail", "").lower()
        print("✓ Wrong current password correctly rejected")
    
    def test_change_password_short_new(self, admin_session):
        """Test that short new password (<6 chars) is rejected"""
        response = admin_session.put(f"{BASE_URL}/api/auth/password", json={
            "currentPassword": ADMIN_PASSWORD,
            "newPassword": "abc"
        })
        assert response.status_code == 400, f"Expected 400 for short password, got {response.status_code}"
        assert "6" in response.json().get("detail", "") or "character" in response.json().get("detail", "").lower()
        print("✓ Short password correctly rejected")
    
    def test_change_password_success(self, admin_session):
        """Test successful password change and revert"""
        new_password = "newadmin123"
        
        # Change password
        response = admin_session.put(f"{BASE_URL}/api/auth/password", json={
            "currentPassword": ADMIN_PASSWORD,
            "newPassword": new_password
        })
        assert response.status_code == 200, f"Password change failed: {response.text}"
        
        # Verify new password works by logging in again
        new_session = requests.Session()
        login_response = new_session.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": new_password
        })
        assert login_response.status_code == 200, "Login with new password failed"
        
        # Revert password back
        revert_response = new_session.put(f"{BASE_URL}/api/auth/password", json={
            "currentPassword": new_password,
            "newPassword": ADMIN_PASSWORD
        })
        assert revert_response.status_code == 200, "Password revert failed"
        print("✓ Password change and revert works correctly")


class TestAppSettings:
    """Tests for GET/PUT /api/settings - App settings (duplicate detection toggle)"""
    
    @pytest.fixture
    def admin_session(self):
        """Login as admin and return session with cookies"""
        session = requests.Session()
        response = session.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        assert response.status_code == 200, f"Admin login failed: {response.text}"
        return session
    
    @pytest.fixture
    def team_session(self):
        """Login as team member and return session with cookies"""
        session = requests.Session()
        response = session.post(f"{BASE_URL}/api/auth/login", json={
            "email": TEAM_EMAIL,
            "password": TEAM_PASSWORD
        })
        assert response.status_code == 200, f"Team login failed: {response.text}"
        return session
    
    def test_get_settings(self, admin_session):
        """Test GET /api/settings returns duplicateDetectionEnabled"""
        response = admin_session.get(f"{BASE_URL}/api/settings")
        assert response.status_code == 200, f"Get settings failed: {response.text}"
        data = response.json()
        assert "duplicateDetectionEnabled" in data
        assert isinstance(data["duplicateDetectionEnabled"], bool)
        print(f"✓ GET /api/settings returns duplicateDetectionEnabled: {data['duplicateDetectionEnabled']}")
    
    def test_team_member_can_get_settings(self, team_session):
        """Test that team members can read settings"""
        response = team_session.get(f"{BASE_URL}/api/settings")
        assert response.status_code == 200, f"Team get settings failed: {response.text}"
        data = response.json()
        assert "duplicateDetectionEnabled" in data
        print("✓ Team member can read settings")
    
    def test_admin_can_toggle_duplicate_detection(self, admin_session):
        """Test admin can toggle duplicate detection on/off"""
        # Get current value
        get_response = admin_session.get(f"{BASE_URL}/api/settings")
        original_value = get_response.json().get("duplicateDetectionEnabled", True)
        
        # Toggle to opposite
        new_value = not original_value
        response = admin_session.put(f"{BASE_URL}/api/settings", json={
            "duplicateDetectionEnabled": new_value
        })
        assert response.status_code == 200, f"Settings update failed: {response.text}"
        
        # Verify change
        verify_response = admin_session.get(f"{BASE_URL}/api/settings")
        assert verify_response.json().get("duplicateDetectionEnabled") == new_value
        
        # Restore original
        admin_session.put(f"{BASE_URL}/api/settings", json={
            "duplicateDetectionEnabled": original_value
        })
        print("✓ Admin can toggle duplicate detection")
    
    def test_team_member_cannot_update_settings(self, team_session):
        """Test that team members get 403 when trying to update settings"""
        response = team_session.put(f"{BASE_URL}/api/settings", json={
            "duplicateDetectionEnabled": False
        })
        assert response.status_code == 403, f"Expected 403 for team member, got {response.status_code}"
        print("✓ Team member correctly gets 403 on settings update")
    
    def test_unauthenticated_cannot_access_settings(self):
        """Test that unauthenticated users cannot access settings"""
        session = requests.Session()
        response = session.get(f"{BASE_URL}/api/settings")
        assert response.status_code == 401, f"Expected 401 for unauthenticated, got {response.status_code}"
        print("✓ Unauthenticated user correctly gets 401")


class TestDeploymentFiles:
    """Tests for deployment configuration files"""
    
    def test_vercel_json_exists(self):
        """Test vercel.json exists at /app/frontend/vercel.json"""
        assert os.path.exists("/app/frontend/vercel.json"), "vercel.json not found"
        with open("/app/frontend/vercel.json") as f:
            import json
            data = json.load(f)
            assert "rewrites" in data
        print("✓ vercel.json exists and has rewrites")
    
    def test_railway_json_exists(self):
        """Test railway.json exists at /app/backend/railway.json"""
        assert os.path.exists("/app/backend/railway.json"), "railway.json not found"
        with open("/app/backend/railway.json") as f:
            import json
            data = json.load(f)
            assert "deploy" in data
            assert "startCommand" in data["deploy"]
        print("✓ railway.json exists with deploy config")
    
    def test_procfile_exists(self):
        """Test Procfile exists at /app/backend/Procfile"""
        assert os.path.exists("/app/backend/Procfile"), "Procfile not found"
        with open("/app/backend/Procfile") as f:
            content = f.read()
            assert "uvicorn" in content
            assert "main:app" in content
        print("✓ Procfile exists with uvicorn command")
    
    def test_main_py_imports_app(self):
        """Test main.py imports app from server correctly"""
        assert os.path.exists("/app/backend/main.py"), "main.py not found"
        with open("/app/backend/main.py") as f:
            content = f.read()
            assert "from server import app" in content
        print("✓ main.py imports app from server")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
