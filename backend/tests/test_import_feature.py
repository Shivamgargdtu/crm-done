"""Tests for the new import feature with duplicate detection and resolution.

This module tests:
- POST /api/leads/import/analyze - Parse CSV, detect duplicates
- POST /api/leads/import/batch - Import non-duplicate leads
- POST /api/leads/import/resolve - Process duplicate resolutions
- POST /api/leads/import/preview - File preview
"""
import pytest
import requests
import os
import io

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test CSV content with duplicates (matching existing phone numbers)
CSV_WITH_DUPLICATES = """Company Name,Phone,City,Category,Notes
Weddings By Evensia,6659345559,Mumbai,Interested,Test duplicate by phone
Karmaa Events Entertainment,9899990552,Delhi,Call Back,Test duplicate by phone
New Company ABC,9876543210,Bangalore,Needs Review,Fresh lead no duplicate
Another Fresh Lead,8765432109,Chennai,Interested,Fresh lead no duplicate
Tailormade Experiences,9830094866,Kolkata,Meeting Done,Test duplicate by phone"""

# Test CSV content without duplicates
CSV_NO_DUPLICATES = """Company Name,Phone,City,Category,Notes
Brand New Company 1,1111111111,Mumbai,Interested,Fresh lead
Brand New Company 2,2222222222,Delhi,Call Back,Fresh lead
Brand New Company 3,3333333333,Bangalore,Needs Review,Fresh lead
Brand New Company 4,4444444444,Chennai,Interested,Fresh lead
Brand New Company 5,5555555555,Kolkata,Meeting Done,Fresh lead"""

# Test CSV with missing company name (should error)
CSV_WITH_ERRORS = """Company Name,Phone,City,Category,Notes
,1234567890,Mumbai,Interested,Missing company name
Valid Company,0987654321,Delhi,Call Back,Valid row"""


class TestImportFeature:
    """Test suite for the new import feature with duplicate detection."""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test session with authentication."""
        self.session = requests.Session()
        
        # Login as admin
        login_response = self.session.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": "admin@wedus.com", "password": "admin123"},
            headers={'Content-Type': 'application/json'}
        )
        if login_response.status_code != 200:
            pytest.skip("Authentication failed - skipping import tests")
        
        # Store cookies for file upload requests
        self.cookies = self.session.cookies.get_dict()
        
        yield
        
        # Cleanup: Delete test leads created during tests
        self._cleanup_test_leads()

    def _cleanup_test_leads(self):
        """Remove test leads created during testing."""
        try:
            # Get leads with test prefixes
            response = self.session.get(f"{BASE_URL}/api/leads?search=Brand%20New%20Company&limit=100")
            if response.status_code == 200:
                leads = response.json().get('leads', [])
                for lead in leads:
                    if 'Brand New Company' in lead.get('companyName', ''):
                        self.session.delete(f"{BASE_URL}/api/leads/{lead['id']}")
            
            # Also cleanup other test leads
            for search_term in ['New Company ABC', 'Another Fresh Lead', 'TEST_IMPORT']:
                response = self.session.get(f"{BASE_URL}/api/leads?search={search_term}&limit=100")
                if response.status_code == 200:
                    leads = response.json().get('leads', [])
                    for lead in leads:
                        self.session.delete(f"{BASE_URL}/api/leads/{lead['id']}")
        except Exception as e:
            print(f"Cleanup warning: {e}")

    # ============== PREVIEW ENDPOINT TESTS ==============

    def test_preview_import_csv(self):
        """Test POST /api/leads/import/preview - Preview CSV file."""
        # Use fresh request for file upload (no Content-Type header)
        files = {'file': ('test.csv', io.BytesIO(CSV_NO_DUPLICATES.encode()), 'text/csv')}
        response = requests.post(
            f"{BASE_URL}/api/leads/import/preview",
            files=files,
            cookies=self.cookies
        )
        
        assert response.status_code == 200, f"Preview failed: {response.text}"
        data = response.json()
        
        # Verify response structure
        assert 'columns' in data, "Missing 'columns' in response"
        assert 'columnMapping' in data, "Missing 'columnMapping' in response"
        assert 'preview' in data, "Missing 'preview' in response"
        assert 'totalRows' in data, "Missing 'totalRows' in response"
        
        # Verify column mapping
        assert data['totalRows'] == 5, f"Expected 5 rows, got {data['totalRows']}"
        assert 'companyName' in data['columnMapping'].values(), "Company name not mapped"
        assert 'phone' in data['columnMapping'].values(), "Phone not mapped"
        
        print(f"Preview successful: {data['totalRows']} rows, columns mapped: {list(data['columnMapping'].values())}")

    def test_preview_import_returns_unmapped_columns(self):
        """Test that preview returns unmapped columns."""
        csv_with_extra = """Company Name,Phone,City,RandomColumn,AnotherExtra
Test Co,1234567890,Mumbai,extra1,extra2"""
        files = {'file': ('test.csv', io.BytesIO(csv_with_extra.encode()), 'text/csv')}
        response = requests.post(
            f"{BASE_URL}/api/leads/import/preview",
            files=files,
            cookies=self.cookies
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert 'unmappedColumns' in data, "Missing 'unmappedColumns' in response"
        assert 'RandomColumn' in data['unmappedColumns'] or 'AnotherExtra' in data['unmappedColumns']
        print(f"Unmapped columns detected: {data['unmappedColumns']}")

    # ============== ANALYZE ENDPOINT TESTS ==============

    def test_analyze_import_with_duplicates(self):
        """Test POST /api/leads/import/analyze - Detect duplicates in CSV."""
        files = {'file': ('test.csv', io.BytesIO(CSV_WITH_DUPLICATES.encode()), 'text/csv')}
        response = requests.post(
            f"{BASE_URL}/api/leads/import/analyze",
            files=files,
            cookies=self.cookies
        )
        
        assert response.status_code == 200, f"Analyze failed: {response.text}"
        data = response.json()
        
        # Verify response structure
        assert 'nonDuplicates' in data, "Missing 'nonDuplicates' in response"
        assert 'duplicates' in data, "Missing 'duplicates' in response"
        assert 'errors' in data, "Missing 'errors' in response"
        
        # Should have some duplicates (matching existing phone numbers)
        print(f"Analyze result: {len(data['nonDuplicates'])} non-duplicates, {len(data['duplicates'])} duplicates, {len(data['errors'])} errors")
        
        # Verify duplicate structure if any found
        if data['duplicates']:
            dup = data['duplicates'][0]
            assert 'incoming' in dup, "Duplicate missing 'incoming' data"
            assert 'existing' in dup, "Duplicate missing 'existing' data"
            assert 'matchReason' in dup, "Duplicate missing 'matchReason'"
            assert 'rowIndex' in dup, "Duplicate missing 'rowIndex'"
            print(f"First duplicate match reason: {dup['matchReason']}")

    def test_analyze_import_no_duplicates(self):
        """Test POST /api/leads/import/analyze - No duplicates found."""
        # Use unique phone numbers that don't exist in DB
        unique_csv = """Company Name,Phone,City,Category
TEST_IMPORT_Unique1,9999888877,TestCity1,Interested
TEST_IMPORT_Unique2,9999888866,TestCity2,Call Back"""
        
        files = {'file': ('test.csv', io.BytesIO(unique_csv.encode()), 'text/csv')}
        response = requests.post(
            f"{BASE_URL}/api/leads/import/analyze",
            files=files,
            cookies=self.cookies
        )
        
        assert response.status_code == 200, f"Analyze failed: {response.text}"
        data = response.json()
        
        # Should have no duplicates with unique phone numbers
        assert len(data['nonDuplicates']) == 2, f"Expected 2 non-duplicates, got {len(data['nonDuplicates'])}"
        print(f"No duplicates found as expected: {len(data['nonDuplicates'])} fresh leads")

    def test_analyze_import_with_errors(self):
        """Test POST /api/leads/import/analyze - Handle rows with errors."""
        files = {'file': ('test.csv', io.BytesIO(CSV_WITH_ERRORS.encode()), 'text/csv')}
        response = requests.post(
            f"{BASE_URL}/api/leads/import/analyze",
            files=files,
            cookies=self.cookies
        )
        
        assert response.status_code == 200, f"Analyze failed: {response.text}"
        data = response.json()
        
        # Should have at least one error for missing company name
        assert len(data['errors']) >= 1, "Expected at least 1 error for missing company name"
        print(f"Errors detected: {data['errors']}")

    # ============== BATCH IMPORT ENDPOINT TESTS ==============

    def test_batch_import_leads(self):
        """Test POST /api/leads/import/batch - Import pre-parsed leads."""
        leads_to_import = [
            {
                "companyName": "TEST_IMPORT_Batch1",
                "phone": "7777666655",
                "city": "TestCity",
                "category": "Interested",
                "priority": "High",
                "pipelineStage": "New Contact",
                "dateAdded": "2026-01-15T10:00:00Z",
                "responseHistory": [],
                "callCount": 0,
                "isDuplicate": False,
                "duplicateDismissed": False,
                "status": "active"
            },
            {
                "companyName": "TEST_IMPORT_Batch2",
                "phone": "7777666644",
                "city": "TestCity2",
                "category": "Call Back",
                "priority": "Medium",
                "pipelineStage": "Interested",
                "dateAdded": "2026-01-15T10:00:00Z",
                "responseHistory": [],
                "callCount": 0,
                "isDuplicate": False,
                "duplicateDismissed": False,
                "status": "active"
            }
        ]
        
        response = self.session.post(
            f"{BASE_URL}/api/leads/import/batch",
            json={"leads": leads_to_import}
        )
        
        assert response.status_code == 200, f"Batch import failed: {response.text}"
        data = response.json()
        
        assert 'imported' in data, "Missing 'imported' count in response"
        assert data['imported'] == 2, f"Expected 2 imported, got {data['imported']}"
        assert 'errors' in data, "Missing 'errors' in response"
        
        print(f"Batch import successful: {data['imported']} leads imported")
        
        # Verify leads were actually created
        verify_response = self.session.get(f"{BASE_URL}/api/leads?search=TEST_IMPORT_Batch&limit=10")
        assert verify_response.status_code == 200
        verify_data = verify_response.json()
        assert verify_data['total'] >= 2, "Imported leads not found in database"

    def test_batch_import_empty_list(self):
        """Test POST /api/leads/import/batch - Empty leads list."""
        response = self.session.post(
            f"{BASE_URL}/api/leads/import/batch",
            json={"leads": []}
        )
        
        assert response.status_code == 200, f"Batch import failed: {response.text}"
        data = response.json()
        assert data['imported'] == 0, "Expected 0 imported for empty list"

    # ============== RESOLVE DUPLICATES ENDPOINT TESTS ==============

    def test_resolve_duplicates_skip(self):
        """Test POST /api/leads/import/resolve - Skip action."""
        # First, create a test lead to use as duplicate target
        create_response = self.session.post(
            f"{BASE_URL}/api/leads",
            json={
                "companyName": "TEST_SKIP_Target",
                "phone": "9999111122",
                "city": "TestCity",
                "category": "Needs Review"
            }
        )
        assert create_response.status_code == 200, f"Failed to create test lead: {create_response.text}"
        existing_lead = create_response.json()
        
        resolutions = [
            {
                "action": "skip",
                "incoming": {
                    "companyName": "TEST_SKIP_Lead",
                    "phone": "1234567890",
                    "city": "TestCity"
                },
                "existingId": existing_lead['id']
            }
        ]
        
        response = self.session.post(
            f"{BASE_URL}/api/leads/import/resolve",
            json={"resolutions": resolutions}
        )
        
        assert response.status_code == 200, f"Resolve failed: {response.text}"
        data = response.json()
        
        assert data['skipped'] == 1, f"Expected 1 skipped, got {data['skipped']}"
        print(f"Skip action successful: {data}")

    def test_resolve_duplicates_overwrite(self):
        """Test POST /api/leads/import/resolve - Overwrite action."""
        # Create a test lead to overwrite
        create_response = self.session.post(
            f"{BASE_URL}/api/leads",
            json={
                "companyName": "TEST_OVERWRITE_Original",
                "phone": "5555444433",
                "city": "OriginalCity",
                "category": "Needs Review"
            }
        )
        assert create_response.status_code == 200
        original_lead = create_response.json()
        
        resolutions = [
            {
                "action": "overwrite",
                "incoming": {
                    "companyName": "TEST_OVERWRITE_Updated",
                    "phone": "5555444433",
                    "city": "UpdatedCity",
                    "category": "Interested",
                    "priority": "High",
                    "pipelineStage": "Interested",
                    "dateAdded": "2026-01-15T10:00:00Z",
                    "responseHistory": [],
                    "callCount": 0,
                    "status": "active"
                },
                "existingId": original_lead['id']
            }
        ]
        
        response = self.session.post(
            f"{BASE_URL}/api/leads/import/resolve",
            json={"resolutions": resolutions}
        )
        
        assert response.status_code == 200, f"Resolve failed: {response.text}"
        data = response.json()
        
        assert data['overwritten'] == 1, f"Expected 1 overwritten, got {data['overwritten']}"
        
        # Verify the lead was actually overwritten
        verify_response = self.session.get(f"{BASE_URL}/api/leads/{original_lead['id']}")
        assert verify_response.status_code == 200
        updated_lead = verify_response.json()
        assert updated_lead['companyName'] == "TEST_OVERWRITE_Updated", "Lead was not overwritten"
        assert updated_lead['city'] == "UpdatedCity", "City was not updated"
        print(f"Overwrite action successful: {data}")

    def test_resolve_duplicates_import_anyway(self):
        """Test POST /api/leads/import/resolve - Import Anyway action."""
        # Get an existing lead
        leads_response = self.session.get(f"{BASE_URL}/api/leads?limit=1")
        assert leads_response.status_code == 200
        existing_lead = leads_response.json()['leads'][0]
        
        resolutions = [
            {
                "action": "import_anyway",
                "incoming": {
                    "companyName": "TEST_IMPORT_ANYWAY_Lead",
                    "phone": "6666555544",
                    "city": "TestCity",
                    "category": "Interested",
                    "priority": "Medium",
                    "pipelineStage": "New Contact",
                    "dateAdded": "2026-01-15T10:00:00Z",
                    "responseHistory": [],
                    "callCount": 0,
                    "status": "active"
                },
                "existingId": existing_lead['id']
            }
        ]
        
        response = self.session.post(
            f"{BASE_URL}/api/leads/import/resolve",
            json={"resolutions": resolutions}
        )
        
        assert response.status_code == 200, f"Resolve failed: {response.text}"
        data = response.json()
        
        assert data['importedAnyway'] == 1, f"Expected 1 importedAnyway, got {data['importedAnyway']}"
        
        # Verify the new lead was created with isDuplicate=True
        verify_response = self.session.get(f"{BASE_URL}/api/leads?search=TEST_IMPORT_ANYWAY&limit=10")
        assert verify_response.status_code == 200
        verify_data = verify_response.json()
        assert verify_data['total'] >= 1, "Import anyway lead not found"
        
        new_lead = verify_data['leads'][0]
        assert new_lead['isDuplicate'] == True, "Lead should be marked as duplicate"
        assert new_lead['duplicateOf'] == existing_lead['id'], "duplicateOf should reference existing lead"
        print(f"Import anyway action successful: {data}")

    def test_resolve_duplicates_merge(self):
        """Test POST /api/leads/import/resolve - Merge action."""
        # Create a test lead to merge into
        create_response = self.session.post(
            f"{BASE_URL}/api/leads",
            json={
                "companyName": "TEST_MERGE_Original",
                "phone": "4444333322",
                "city": "",  # Empty city to test merge
                "category": "Needs Review",
                "notes": "Original notes"
            }
        )
        assert create_response.status_code == 200
        original_lead = create_response.json()
        
        resolutions = [
            {
                "action": "merge",
                "incoming": {
                    "companyName": "TEST_MERGE_Incoming",
                    "phone": "4444333322",
                    "city": "MergedCity",  # Should fill empty city
                    "category": "Interested",  # Should update category
                    "notes": "Incoming notes",
                    "priority": "High",
                    "pipelineStage": "Interested",
                    "dateAdded": "2026-01-15T10:00:00Z",
                    "responseHistory": [{"response": "Interested", "timestamp": "2026-01-15T10:00:00Z"}],
                    "callCount": 1,
                    "status": "active"
                },
                "existingId": original_lead['id']
            }
        ]
        
        response = self.session.post(
            f"{BASE_URL}/api/leads/import/resolve",
            json={"resolutions": resolutions}
        )
        
        assert response.status_code == 200, f"Resolve failed: {response.text}"
        data = response.json()
        
        assert data['merged'] == 1, f"Expected 1 merged, got {data['merged']}"
        
        # Verify the lead was merged
        verify_response = self.session.get(f"{BASE_URL}/api/leads/{original_lead['id']}")
        assert verify_response.status_code == 200
        merged_lead = verify_response.json()
        
        # City should be filled from incoming
        assert merged_lead['city'] == "MergedCity", f"City not merged: {merged_lead['city']}"
        # Category should be updated from incoming (non-Needs Review)
        assert merged_lead['category'] == "Interested", f"Category not merged: {merged_lead['category']}"
        print(f"Merge action successful: {data}")

    def test_resolve_duplicates_mixed_actions(self):
        """Test POST /api/leads/import/resolve - Multiple actions at once."""
        # Create test leads
        lead1 = self.session.post(f"{BASE_URL}/api/leads", json={
            "companyName": "TEST_MIXED_1", "phone": "1111222233", "category": "Needs Review"
        }).json()
        lead2 = self.session.post(f"{BASE_URL}/api/leads", json={
            "companyName": "TEST_MIXED_2", "phone": "1111222244", "category": "Needs Review"
        }).json()
        
        resolutions = [
            {
                "action": "skip",
                "incoming": {"companyName": "Skip This", "phone": "0000000001"},
                "existingId": lead1['id']
            },
            {
                "action": "overwrite",
                "incoming": {
                    "companyName": "TEST_MIXED_2_Overwritten",
                    "phone": "1111222244",
                    "city": "NewCity",
                    "category": "Interested",
                    "priority": "High",
                    "pipelineStage": "Interested",
                    "dateAdded": "2026-01-15T10:00:00Z",
                    "responseHistory": [],
                    "callCount": 0,
                    "status": "active"
                },
                "existingId": lead2['id']
            }
        ]
        
        response = self.session.post(
            f"{BASE_URL}/api/leads/import/resolve",
            json={"resolutions": resolutions}
        )
        
        assert response.status_code == 200, f"Resolve failed: {response.text}"
        data = response.json()
        
        assert data['skipped'] == 1, f"Expected 1 skipped, got {data['skipped']}"
        assert data['overwritten'] == 1, f"Expected 1 overwritten, got {data['overwritten']}"
        print(f"Mixed actions successful: {data}")

    # ============== LEGACY IMPORT ENDPOINT TEST ==============

    def test_legacy_import_still_works(self):
        """Test POST /api/leads/import - Legacy import auto-skips duplicates."""
        unique_csv = """Company Name,Phone,City,Category
TEST_LEGACY_Import1,8888777766,LegacyCity,Interested
TEST_LEGACY_Import2,8888777755,LegacyCity2,Call Back"""
        
        files = {'file': ('test.csv', io.BytesIO(unique_csv.encode()), 'text/csv')}
        response = requests.post(
            f"{BASE_URL}/api/leads/import",
            files=files,
            cookies=self.cookies
        )
        
        assert response.status_code == 200, f"Legacy import failed: {response.text}"
        data = response.json()
        
        assert 'imported' in data, "Missing 'imported' in response"
        assert 'duplicatesSkipped' in data, "Missing 'duplicatesSkipped' in response"
        print(f"Legacy import successful: {data['imported']} imported, {data['duplicatesSkipped']} skipped")

    # ============== ERROR HANDLING TESTS ==============

    def test_analyze_import_invalid_file(self):
        """Test POST /api/leads/import/analyze - Invalid file format."""
        invalid_content = b"This is not a valid CSV file content \x00\x01\x02"
        files = {'file': ('test.txt', io.BytesIO(invalid_content), 'text/plain')}
        response = requests.post(
            f"{BASE_URL}/api/leads/import/analyze",
            files=files,
            cookies=self.cookies
        )
        
        # Should either return 400 or 200 with errors
        assert response.status_code in [200, 400], f"Unexpected status: {response.status_code}"
        print(f"Invalid file handled: status {response.status_code}")

    def test_resolve_with_invalid_existing_id(self):
        """Test POST /api/leads/import/resolve - Invalid existing ID."""
        resolutions = [
            {
                "action": "merge",
                "incoming": {"companyName": "Test", "phone": "1234567890"},
                "existingId": "000000000000000000000000"  # Non-existent ID
            }
        ]
        
        response = self.session.post(
            f"{BASE_URL}/api/leads/import/resolve",
            json={"resolutions": resolutions}
        )
        
        assert response.status_code == 200, f"Resolve failed: {response.text}"
        data = response.json()
        
        # Should have an error for the invalid ID
        assert len(data['errors']) >= 1, "Expected error for invalid existing ID"
        print(f"Invalid ID handled: {data['errors']}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
