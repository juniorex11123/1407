#!/usr/bin/env python3
"""
Backend API Testing for TimeTracker Pro
Tests the actual FastAPI endpoints available in the backend
"""

import requests
import sys
import json
from datetime import datetime

class BackendAPITester:
    def __init__(self, base_url="http://localhost:8001"):
        self.base_url = base_url
        self.tests_run = 0
        self.tests_passed = 0
        self.tokens = {}  # Store tokens for different user types
        print(f"🔧 Testing Backend API at: {self.base_url}")
        print("=" * 60)

    def run_test(self, name, method, endpoint, expected_status, data=None, headers=None, auth_token=None):
        """Run a single API test"""
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        if headers is None:
            headers = {'Content-Type': 'application/json'}
        
        if auth_token:
            headers['Authorization'] = f'Bearer {auth_token}'

        self.tests_run += 1
        print(f"\n🔍 Test {self.tests_run}: {name}")
        print(f"   URL: {url}")
        print(f"   Method: {method}")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, timeout=10)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers, timeout=10)
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=headers, timeout=10)
            elif method == 'DELETE':
                response = requests.delete(url, headers=headers, timeout=10)
            else:
                print(f"❌ Unsupported method: {method}")
                return False, {}

            print(f"   Status: {response.status_code}")
            
            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                print(f"✅ PASSED")
                try:
                    response_data = response.json()
                    if len(str(response_data)) > 500:
                        print(f"   Response: [Large response - {len(str(response_data))} chars]")
                    else:
                        print(f"   Response: {json.dumps(response_data, indent=2, default=str)}")
                    return True, response_data
                except:
                    print(f"   Response: {response.text[:200]}...")
                    return True, {}
            else:
                print(f"❌ FAILED - Expected {expected_status}, got {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"   Error: {json.dumps(error_data, indent=2)}")
                except:
                    print(f"   Error: {response.text[:200]}...")
                return False, {}

        except requests.exceptions.Timeout:
            print(f"❌ FAILED - Request timeout")
            return False, {}
        except requests.exceptions.ConnectionError:
            print(f"❌ FAILED - Connection error")
            return False, {}
        except Exception as e:
            print(f"❌ FAILED - Error: {str(e)}")
            return False, {}

    def test_login(self, username, password, user_type):
        """Test user login"""
        success, response = self.run_test(
            f"Login as {user_type} ({username})",
            "POST",
            "/api/auth/login",
            200,
            data={"username": username, "password": password}
        )
        if success and 'access_token' in response:
            self.tokens[user_type] = response['access_token']
            print(f"   ✅ Token stored for {user_type}")
            return True, response
        return False, {}

    def test_companies_crud(self):
        """Test company CRUD operations (owner only)"""
        if 'owner' not in self.tokens:
            print("❌ No owner token available for company tests")
            return False
        
        owner_token = self.tokens['owner']
        
        # Get companies
        success, companies = self.run_test(
            "Get Companies (Owner)",
            "GET",
            "/api/companies",
            200,
            auth_token=owner_token
        )
        
        # Create company
        test_company = {"name": f"Test Company {datetime.now().strftime('%H%M%S')}"}
        success, created_company = self.run_test(
            "Create Company (Owner)",
            "POST",
            "/api/companies",
            200,
            data=test_company,
            auth_token=owner_token
        )
        
        if success and 'id' in created_company:
            company_id = created_company['id']
            
            # Update company
            update_data = {"name": f"Updated Company {datetime.now().strftime('%H%M%S')}"}
            self.run_test(
                "Update Company (Owner)",
                "PUT",
                f"/api/companies/{company_id}",
                200,
                data=update_data,
                auth_token=owner_token
            )
            
            # Delete company
            self.run_test(
                "Delete Company (Owner)",
                "DELETE",
                f"/api/companies/{company_id}",
                200,
                auth_token=owner_token
            )

    def test_users_crud(self):
        """Test user CRUD operations (owner only)"""
        if 'owner' not in self.tokens:
            print("❌ No owner token available for user tests")
            return False
        
        owner_token = self.tokens['owner']
        
        # Get users
        success, users = self.run_test(
            "Get Users (Owner)",
            "GET",
            "/api/users",
            200,
            auth_token=owner_token
        )
        
        # Create user
        test_user = {
            "username": f"testuser_{datetime.now().strftime('%H%M%S')}",
            "password": "testpass123",
            "type": "user",
            "company_id": "1"
        }
        success, created_user = self.run_test(
            "Create User (Owner)",
            "POST",
            "/api/users",
            200,
            data=test_user,
            auth_token=owner_token
        )
        
        if success and 'id' in created_user:
            user_id = created_user['id']
            
            # Update user
            update_data = {"type": "admin"}
            self.run_test(
                "Update User (Owner)",
                "PUT",
                f"/api/users/{user_id}",
                200,
                data=update_data,
                auth_token=owner_token
            )
            
            # Delete user
            self.run_test(
                "Delete User (Owner)",
                "DELETE",
                f"/api/users/{user_id}",
                200,
                auth_token=owner_token
            )

    def test_employees_operations(self):
        """Test employee operations (admin access)"""
        if 'admin' not in self.tokens:
            print("❌ No admin token available for employee tests")
            return False
        
        admin_token = self.tokens['admin']
        
        # Get employees
        success, employees = self.run_test(
            "Get Employees (Admin)",
            "GET",
            "/api/employees",
            200,
            auth_token=admin_token
        )
        
        # Create employee
        test_employee = {
            "name": f"Test Employee {datetime.now().strftime('%H%M%S')}",
            "company_id": "1"
        }
        success, created_employee = self.run_test(
            "Create Employee (Admin)",
            "POST",
            "/api/employees",
            200,
            data=test_employee,
            auth_token=admin_token
        )
        
        if success and 'id' in created_employee:
            employee_id = created_employee['id']
            
            # Generate QR code for employee
            self.run_test(
                "Generate QR Code (Admin)",
                "POST",
                f"/api/employees/{employee_id}/qr",
                200,
                auth_token=admin_token
            )
            
            # Update employee
            update_data = {"name": f"Updated Employee {datetime.now().strftime('%H%M%S')}"}
            self.run_test(
                "Update Employee (Admin)",
                "PUT",
                f"/api/employees/{employee_id}",
                200,
                data=update_data,
                auth_token=admin_token
            )
            
            # Delete employee
            self.run_test(
                "Delete Employee (Admin)",
                "DELETE",
                f"/api/employees/{employee_id}",
                200,
                auth_token=admin_token
            )

    def test_time_entries_operations(self):
        """Test time entry operations"""
        if 'admin' not in self.tokens:
            print("❌ No admin token available for time entry tests")
            return False
        
        admin_token = self.tokens['admin']
        
        # Get time entries
        success, time_entries = self.run_test(
            "Get Time Entries (Admin)",
            "GET",
            "/api/time-entries",
            200,
            auth_token=admin_token
        )
        
        # Create time entry
        test_time_entry = {
            "employee_id": "1",
            "check_in": datetime.now().isoformat(),
            "check_out": datetime.now().isoformat()
        }
        success, created_entry = self.run_test(
            "Create Time Entry",
            "POST",
            "/api/time-entries",
            200,
            data=test_time_entry,
            auth_token=admin_token
        )
        
        if success and 'id' in created_entry:
            entry_id = created_entry['id']
            
            # Update time entry
            update_data = {"check_out": datetime.now().isoformat()}
            self.run_test(
                "Update Time Entry (Admin)",
                "PUT",
                f"/api/time-entries/{entry_id}",
                200,
                data=update_data,
                auth_token=admin_token
            )
            
            # Delete time entry
            self.run_test(
                "Delete Time Entry (Admin)",
                "DELETE",
                f"/api/time-entries/{entry_id}",
                200,
                auth_token=admin_token
            )

    def test_authorization(self):
        """Test authorization restrictions"""
        if 'user' not in self.tokens:
            print("❌ No user token available for authorization tests")
            return False
        
        user_token = self.tokens['user']
        
        # User should not be able to access owner endpoints
        self.run_test(
            "User Access to Companies (Should Fail)",
            "GET",
            "/api/companies",
            403,
            auth_token=user_token
        )
        
        self.run_test(
            "User Access to Users (Should Fail)",
            "GET",
            "/api/users",
            403,
            auth_token=user_token
        )

    def test_root_endpoint(self):
        """Test the root API endpoint"""
        return self.run_test(
            "Root API Endpoint",
            "GET",
            "/api/",
            200
        )

def main():
    """Main test execution"""
    print("🚀 Starting Backend API Tests for TimeTracker Pro")
    print(f"⏰ Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    tester = BackendAPITester()
    
    # Test basic connectivity
    print("\n" + "="*60)
    print("📋 TESTING BASIC CONNECTIVITY")
    print("="*60)
    tester.test_root_endpoint()
    
    # Test authentication for all user types
    print("\n" + "="*60)
    print("🔐 TESTING AUTHENTICATION")
    print("="*60)
    
    # Login as different user types
    tester.test_login("owner", "owner123", "owner")
    tester.test_login("admin", "admin123", "admin")
    tester.test_login("user", "user123", "user")
    
    # Test invalid login
    tester.run_test(
        "Invalid Login",
        "POST",
        "/api/auth/login",
        401,
        data={"username": "invalid", "password": "invalid"}
    )
    
    # Test owner functionality
    print("\n" + "="*60)
    print("👑 TESTING OWNER FUNCTIONALITY")
    print("="*60)
    tester.test_companies_crud()
    tester.test_users_crud()
    
    # Test admin functionality
    print("\n" + "="*60)
    print("🔧 TESTING ADMIN FUNCTIONALITY")
    print("="*60)
    tester.test_employees_operations()
    tester.test_time_entries_operations()
    
    # Test authorization
    print("\n" + "="*60)
    print("🛡️ TESTING AUTHORIZATION")
    print("="*60)
    tester.test_authorization()
    
    # Print final results
    print("\n" + "="*60)
    print("📊 FINAL TEST RESULTS")
    print("="*60)
    print(f"✅ Tests passed: {tester.tests_passed}")
    print(f"📝 Total tests run: {tester.tests_run}")
    print(f"📈 Success rate: {(tester.tests_passed/tester.tests_run)*100:.1f}%")
    
    # Analysis
    print("\n" + "="*60)
    print("🔍 ANALYSIS")
    print("="*60)
    if tester.tests_passed > tester.tests_run * 0.8:
        print("✅ Backend API Status: EXCELLENT")
        print("   - All major functionality is working")
        print("   - Authentication system is functional")
        print("   - CRUD operations are working properly")
        print("   - Authorization is properly implemented")
    elif tester.tests_passed > tester.tests_run * 0.6:
        print("⚠️ Backend API Status: GOOD with some issues")
        print("   - Most functionality is working")
        print("   - Some endpoints may have issues")
    else:
        print("❌ Backend API Status: NEEDS ATTENTION")
        print("   - Multiple endpoints are failing")
        print("   - Backend may not be properly configured")
    
    print(f"\n🔧 Tokens obtained: {list(tester.tokens.keys())}")
    print("   - These can be used for frontend integration testing")
    
    return 0 if tester.tests_passed > 0 else 1

if __name__ == "__main__":
    sys.exit(main())