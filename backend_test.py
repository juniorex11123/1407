#!/usr/bin/env python3
"""
Comprehensive Backend API Testing for TimeTracker Pro
Tests all endpoints with focus on QR code functionality
"""

import requests
import sys
import json
from datetime import datetime
import base64

class TimeTrackerAPITester:
    def __init__(self, base_url="https://aa8c76e2-207c-4829-8cfd-90e128411a1d.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.tokens = {}  # Store tokens for different users
        self.users = {}   # Store user data
        self.employees = []  # Store employee data
        self.tests_run = 0
        self.tests_passed = 0

    def run_test(self, name, method, endpoint, expected_status, data=None, user_type=None, headers=None):
        """Run a single API test"""
        url = f"{self.api_url}/{endpoint}"
        test_headers = {'Content-Type': 'application/json'}
        
        # Add auth token if user_type specified
        if user_type and user_type in self.tokens:
            test_headers['Authorization'] = f'Bearer {self.tokens[user_type]}'
        
        # Add custom headers
        if headers:
            test_headers.update(headers)

        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        print(f"   URL: {url}")
        print(f"   Method: {method}")
        if data:
            print(f"   Data: {json.dumps(data, indent=2)}")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=test_headers)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=test_headers)
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=test_headers)
            elif method == 'DELETE':
                response = requests.delete(url, headers=test_headers)

            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                try:
                    response_data = response.json()
                    print(f"   Response: {json.dumps(response_data, indent=2)[:200]}...")
                    return True, response_data
                except:
                    return True, {}
            else:
                print(f"❌ Failed - Expected {expected_status}, got {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"   Error: {json.dumps(error_data, indent=2)}")
                except:
                    print(f"   Error: {response.text}")
                return False, {}

        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            return False, {}

    def test_login(self, username, password, user_type):
        """Test login and store token"""
        success, response = self.run_test(
            f"Login as {user_type} ({username})",
            "POST",
            "auth/login",
            200,
            data={"username": username, "password": password}
        )
        if success and 'access_token' in response:
            self.tokens[user_type] = response['access_token']
            self.users[user_type] = response['user']
            print(f"   ✅ Token stored for {user_type}")
            return True
        return False

    def test_employees_crud(self):
        """Test employee CRUD operations"""
        print("\n" + "="*50)
        print("TESTING EMPLOYEE CRUD OPERATIONS")
        print("="*50)
        
        # Get employees as admin
        success, employees_data = self.run_test(
            "Get all employees (admin)",
            "GET",
            "employees",
            200,
            user_type="admin"
        )
        if success:
            self.employees = employees_data
            print(f"   Found {len(self.employees)} employees")

        # Create new employee as admin
        new_employee_data = {
            "name": "Test Employee",
            "company_id": "1"
        }
        success, created_employee = self.run_test(
            "Create new employee (admin)",
            "POST",
            "employees",
            201,
            data=new_employee_data,
            user_type="admin"
        )
        if success:
            test_employee_id = created_employee.get('id')
            print(f"   Created employee with ID: {test_employee_id}")
            
            # Update employee
            update_data = {
                "name": "Updated Test Employee",
                "is_active": False
            }
            self.run_test(
                "Update employee (admin)",
                "PUT",
                f"employees/{test_employee_id}",
                200,
                data=update_data,
                user_type="admin"
            )
            
            # Delete employee
            self.run_test(
                "Delete employee (admin)",
                "DELETE",
                f"employees/{test_employee_id}",
                200,
                user_type="admin"
            )

    def test_qr_functionality(self):
        """Test QR code generation and PDF download - MAIN FOCUS"""
        print("\n" + "="*50)
        print("TESTING QR CODE FUNCTIONALITY (MAIN FOCUS)")
        print("="*50)
        
        if not self.employees:
            print("❌ No employees found for QR testing")
            return
        
        # Test with first employee
        employee = self.employees[0]
        employee_id = employee['id']
        employee_name = employee['name']
        
        print(f"Testing QR functionality for employee: {employee_name} (ID: {employee_id})")
        
        # Test QR code generation
        success, qr_data = self.run_test(
            f"Generate QR code for {employee_name}",
            "GET",
            f"employees/{employee_id}/qr",
            200,
            user_type="admin"
        )
        
        if success:
            print(f"   QR Code Data: {qr_data.get('qr_code_data', 'N/A')}")
            qr_image = qr_data.get('qr_code_image', '')
            if qr_image:
                print(f"   QR Image (base64): {qr_image[:50]}... (length: {len(qr_image)})")
                
                # Validate base64 image
                try:
                    decoded = base64.b64decode(qr_image)
                    print(f"   ✅ QR image is valid base64 (decoded size: {len(decoded)} bytes)")
                except Exception as e:
                    print(f"   ❌ QR image base64 validation failed: {e}")
            else:
                print("   ❌ No QR image data received")
        
        # Test QR PDF download
        print(f"\n🔍 Testing QR PDF download for {employee_name}...")
        try:
            url = f"{self.api_url}/employees/{employee_id}/qr-pdf"
            headers = {
                'Authorization': f'Bearer {self.tokens["admin"]}'
            }
            
            response = requests.get(url, headers=headers)
            
            if response.status_code == 200:
                self.tests_passed += 1
                print(f"✅ PDF download successful - Status: {response.status_code}")
                print(f"   Content-Type: {response.headers.get('content-type', 'N/A')}")
                print(f"   Content-Length: {len(response.content)} bytes")
                
                # Check if it's actually a PDF
                if response.content.startswith(b'%PDF'):
                    print("   ✅ Response is valid PDF format")
                else:
                    print("   ❌ Response is not valid PDF format")
                    
                # Check Content-Disposition header
                content_disposition = response.headers.get('content-disposition', '')
                if 'attachment' in content_disposition:
                    print(f"   ✅ Proper download headers: {content_disposition}")
                else:
                    print(f"   ⚠️  Missing download headers: {content_disposition}")
                    
            else:
                print(f"❌ PDF download failed - Status: {response.status_code}")
                print(f"   Error: {response.text}")
                
            self.tests_run += 1
            
        except Exception as e:
            print(f"❌ PDF download error: {str(e)}")
            self.tests_run += 1

    def test_time_entries(self):
        """Test time entries functionality"""
        print("\n" + "="*50)
        print("TESTING TIME ENTRIES")
        print("="*50)
        
        # Get time entries
        success, time_entries = self.run_test(
            "Get all time entries (admin)",
            "GET",
            "time-entries",
            200,
            user_type="admin"
        )
        if success:
            print(f"   Found {len(time_entries)} time entries")

    def test_employee_summary(self):
        """Test employee summary endpoints"""
        print("\n" + "="*50)
        print("TESTING EMPLOYEE SUMMARY")
        print("="*50)
        
        # Get employee summary
        success, summary = self.run_test(
            "Get employee summary (admin)",
            "GET",
            "employee-summary",
            200,
            user_type="admin"
        )
        if success and summary:
            print(f"   Found summary for {len(summary)} employees")
            
            # Test employee months for first employee
            if summary:
                employee_id = summary[0]['employee_id']
                self.run_test(
                    f"Get employee months for {employee_id}",
                    "GET",
                    f"employee-months/{employee_id}",
                    200,
                    user_type="admin"
                )

    def test_access_control(self):
        """Test access control for different user types"""
        print("\n" + "="*50)
        print("TESTING ACCESS CONTROL")
        print("="*50)
        
        # Test user access to admin endpoints (should fail)
        self.run_test(
            "User trying to access employees (should fail)",
            "GET",
            "employees",
            403,
            user_type="user"
        )
        
        # Test admin access to owner endpoints (should fail)
        self.run_test(
            "Admin trying to access companies (should fail)",
            "GET",
            "companies",
            403,
            user_type="admin"
        )
        
        # Test owner access to companies (should succeed)
        self.run_test(
            "Owner accessing companies (should succeed)",
            "GET",
            "companies",
            200,
            user_type="owner"
        )

    def test_basic_endpoints(self):
        """Test basic endpoints"""
        print("\n" + "="*50)
        print("TESTING BASIC ENDPOINTS")
        print("="*50)
        
        # Test root endpoint
        self.run_test(
            "Root endpoint",
            "GET",
            "",
            200
        )
        
        # Test status endpoint
        status_data = {"client_name": "test_client"}
        self.run_test(
            "Create status check",
            "POST",
            "status",
            200,
            data=status_data
        )
        
        self.run_test(
            "Get status checks",
            "GET",
            "status",
            200
        )

def main():
    print("🚀 Starting TimeTracker Pro API Testing")
    print("="*60)
    
    tester = TimeTrackerAPITester()
    
    # Test authentication for all user types
    print("\n" + "="*50)
    print("TESTING AUTHENTICATION")
    print("="*50)
    
    auth_tests = [
        ("admin", "admin123", "admin"),
        ("owner", "owner123", "owner"),
        ("user", "user123", "user")
    ]
    
    login_success = True
    for username, password, user_type in auth_tests:
        if not tester.test_login(username, password, user_type):
            print(f"❌ Login failed for {user_type}, stopping tests")
            login_success = False
    
    if not login_success:
        print("\n❌ Authentication failed, cannot continue with API tests")
        return 1
    
    # Run all tests
    tester.test_basic_endpoints()
    tester.test_employees_crud()
    tester.test_qr_functionality()  # MAIN FOCUS
    tester.test_time_entries()
    tester.test_employee_summary()
    tester.test_access_control()
    
    # Print final results
    print("\n" + "="*60)
    print("📊 FINAL TEST RESULTS")
    print("="*60)
    print(f"Tests run: {tester.tests_run}")
    print(f"Tests passed: {tester.tests_passed}")
    print(f"Tests failed: {tester.tests_run - tester.tests_passed}")
    print(f"Success rate: {(tester.tests_passed/tester.tests_run)*100:.1f}%")
    
    if tester.tests_passed == tester.tests_run:
        print("\n🎉 ALL TESTS PASSED!")
        return 0
    else:
        print(f"\n⚠️  {tester.tests_run - tester.tests_passed} TESTS FAILED")
        return 1

if __name__ == "__main__":
    sys.exit(main())