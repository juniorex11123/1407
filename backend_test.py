#!/usr/bin/env python3

import requests
import sys
import json
from datetime import datetime, timedelta

class TimeTrackerAPITester:
    def __init__(self, base_url="https://1ece32d4-e477-4330-968e-4ff479ed65b7.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.tokens = {}  # Store tokens for different users
        self.tests_run = 0
        self.tests_passed = 0
        self.created_resources = {
            'companies': [],
            'users': [],
            'employees': [],
            'time_entries': []
        }

    def log(self, message):
        print(f"[{datetime.now().strftime('%H:%M:%S')}] {message}")

    def run_test(self, name, method, endpoint, expected_status, data=None, token=None, description=""):
        """Run a single API test"""
        url = f"{self.api_url}/{endpoint}"
        headers = {'Content-Type': 'application/json'}
        if token:
            headers['Authorization'] = f'Bearer {token}'

        self.tests_run += 1
        self.log(f"🔍 Testing {name}... {description}")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, timeout=10)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers, timeout=10)
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=headers, timeout=10)
            elif method == 'DELETE':
                response = requests.delete(url, headers=headers, timeout=10)

            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                self.log(f"✅ {name} - Status: {response.status_code}")
                try:
                    return True, response.json() if response.content else {}
                except:
                    return True, {}
            else:
                self.log(f"❌ {name} - Expected {expected_status}, got {response.status_code}")
                try:
                    error_data = response.json()
                    self.log(f"   Error details: {error_data}")
                except:
                    self.log(f"   Response text: {response.text}")
                return False, {}

        except Exception as e:
            self.log(f"❌ {name} - Error: {str(e)}")
            return False, {}

    def test_authentication(self):
        """Test authentication endpoints"""
        self.log("\n=== AUTHENTICATION TESTS ===")
        
        # Test owner login
        success, response = self.run_test(
            "Owner Login",
            "POST",
            "auth/login",
            200,
            data={"username": "owner", "password": "owner123"},
            description="Login as system owner"
        )
        if success and 'access_token' in response:
            self.tokens['owner'] = response['access_token']
            self.log(f"   Owner user info: {response.get('user', {})}")

        # Test admin login
        success, response = self.run_test(
            "Admin Login",
            "POST",
            "auth/login",
            200,
            data={"username": "admin", "password": "admin123"},
            description="Login as company admin"
        )
        if success and 'access_token' in response:
            self.tokens['admin'] = response['access_token']
            self.log(f"   Admin user info: {response.get('user', {})}")

        # Test user login
        success, response = self.run_test(
            "User Login",
            "POST",
            "auth/login",
            200,
            data={"username": "user", "password": "user123"},
            description="Login as regular user"
        )
        if success and 'access_token' in response:
            self.tokens['user'] = response['access_token']
            self.log(f"   User info: {response.get('user', {})}")

        # Test invalid login
        self.run_test(
            "Invalid Login",
            "POST",
            "auth/login",
            401,
            data={"username": "invalid", "password": "invalid"},
            description="Test invalid credentials"
        )

    def test_companies_api(self):
        """Test companies CRUD operations"""
        self.log("\n=== COMPANIES API TESTS ===")
        
        if 'owner' not in self.tokens:
            self.log("❌ Skipping companies tests - no owner token")
            return

        owner_token = self.tokens['owner']

        # Get all companies
        success, companies = self.run_test(
            "Get Companies",
            "GET",
            "companies",
            200,
            token=owner_token,
            description="Fetch all companies"
        )
        if success:
            self.log(f"   Found {len(companies)} companies")

        # Create new company
        new_company_data = {"name": "Test Company Ltd"}
        success, company = self.run_test(
            "Create Company",
            "POST",
            "companies",
            200,
            data=new_company_data,
            token=owner_token,
            description="Create new company"
        )
        if success and 'id' in company:
            self.created_resources['companies'].append(company['id'])
            self.log(f"   Created company with ID: {company['id']}")

            # Update company
            update_data = {"name": "Updated Test Company Ltd"}
            self.run_test(
                "Update Company",
                "PUT",
                f"companies/{company['id']}",
                200,
                data=update_data,
                token=owner_token,
                description="Update company name"
            )

        # Test unauthorized access (admin trying to access companies)
        if 'admin' in self.tokens:
            self.run_test(
                "Unauthorized Company Access",
                "GET",
                "companies",
                403,
                token=self.tokens['admin'],
                description="Admin should not access companies"
            )

    def test_users_api(self):
        """Test users CRUD operations"""
        self.log("\n=== USERS API TESTS ===")
        
        if 'owner' not in self.tokens:
            self.log("❌ Skipping users tests - no owner token")
            return

        owner_token = self.tokens['owner']

        # Get all users
        success, users = self.run_test(
            "Get Users",
            "GET",
            "users",
            200,
            token=owner_token,
            description="Fetch all users"
        )
        if success:
            self.log(f"   Found {len(users)} users")

        # Create new user
        new_user_data = {
            "username": f"testuser_{datetime.now().strftime('%H%M%S')}",
            "password": "testpass123",
            "type": "user",
            "company_id": "1"
        }
        success, user = self.run_test(
            "Create User",
            "POST",
            "users",
            200,
            data=new_user_data,
            token=owner_token,
            description="Create new user"
        )
        if success and 'id' in user:
            self.created_resources['users'].append(user['id'])
            self.log(f"   Created user with ID: {user['id']}")

            # Update user
            update_data = {"type": "admin"}
            self.run_test(
                "Update User",
                "PUT",
                f"users/{user['id']}",
                200,
                data=update_data,
                token=owner_token,
                description="Update user role to admin"
            )

        # Test duplicate username
        self.run_test(
            "Duplicate Username",
            "POST",
            "users",
            400,
            data={"username": "owner", "password": "test", "type": "user"},
            token=owner_token,
            description="Should reject duplicate username"
        )

    def test_employees_api(self):
        """Test employees CRUD operations"""
        self.log("\n=== EMPLOYEES API TESTS ===")
        
        if 'admin' not in self.tokens:
            self.log("❌ Skipping employees tests - no admin token")
            return

        admin_token = self.tokens['admin']

        # Get all employees
        success, employees = self.run_test(
            "Get Employees",
            "GET",
            "employees",
            200,
            token=admin_token,
            description="Fetch all employees"
        )
        if success:
            self.log(f"   Found {len(employees)} employees")

        # Create new employee
        new_employee_data = {
            "name": f"Test Employee {datetime.now().strftime('%H%M%S')}",
            "company_id": "1"
        }
        success, employee = self.run_test(
            "Create Employee",
            "POST",
            "employees",
            200,
            data=new_employee_data,
            token=admin_token,
            description="Create new employee"
        )
        if success and 'id' in employee:
            self.created_resources['employees'].append(employee['id'])
            self.log(f"   Created employee with ID: {employee['id']}")

            # Generate QR code for employee
            self.run_test(
                "Generate QR Code",
                "POST",
                f"employees/{employee['id']}/qr",
                200,
                token=admin_token,
                description="Generate QR code for employee"
            )

            # Update employee
            update_data = {"name": "Updated Test Employee", "is_active": False}
            self.run_test(
                "Update Employee",
                "PUT",
                f"employees/{employee['id']}",
                200,
                data=update_data,
                token=admin_token,
                description="Update employee details"
            )

        # Test unauthorized access (user trying to create employee)
        if 'user' in self.tokens:
            self.run_test(
                "Unauthorized Employee Creation",
                "POST",
                "employees",
                403,
                data=new_employee_data,
                token=self.tokens['user'],
                description="User should not create employees"
            )

    def test_time_entries_api(self):
        """Test time entries CRUD operations"""
        self.log("\n=== TIME ENTRIES API TESTS ===")
        
        if 'admin' not in self.tokens:
            self.log("❌ Skipping time entries tests - no admin token")
            return

        admin_token = self.tokens['admin']

        # Get all time entries
        success, time_entries = self.run_test(
            "Get Time Entries",
            "GET",
            "time-entries",
            200,
            token=admin_token,
            description="Fetch all time entries"
        )
        if success:
            self.log(f"   Found {len(time_entries)} time entries")

        # Create new time entry
        check_in_time = datetime.utcnow().replace(hour=9, minute=0, second=0, microsecond=0)
        check_out_time = check_in_time + timedelta(hours=8)
        
        new_time_entry_data = {
            "employee_id": "1",  # Using default employee
            "check_in": check_in_time.isoformat(),
            "check_out": check_out_time.isoformat()
        }
        success, time_entry = self.run_test(
            "Create Time Entry",
            "POST",
            "time-entries",
            200,
            data=new_time_entry_data,
            token=admin_token,
            description="Create new time entry"
        )
        if success and 'id' in time_entry:
            self.created_resources['time_entries'].append(time_entry['id'])
            self.log(f"   Created time entry with ID: {time_entry['id']}")
            self.log(f"   Total hours calculated: {time_entry.get('total_hours', 'N/A')}")

            # Update time entry
            new_check_out = check_in_time + timedelta(hours=7, minutes=30)
            update_data = {"check_out": new_check_out.isoformat()}
            self.run_test(
                "Update Time Entry",
                "PUT",
                f"time-entries/{time_entry['id']}",
                200,
                data=update_data,
                token=admin_token,
                description="Update time entry check-out time"
            )

        # Test unauthorized access (user trying to update time entry)
        if 'user' in self.tokens and time_entries:
            self.run_test(
                "Unauthorized Time Entry Update",
                "PUT",
                f"time-entries/{time_entries[0]['id']}",
                403,
                data={"check_out": datetime.utcnow().isoformat()},
                token=self.tokens['user'],
                description="User should not update time entries"
            )

    def test_role_based_access(self):
        """Test role-based access control"""
        self.log("\n=== ROLE-BASED ACCESS CONTROL TESTS ===")
        
        # Test owner accessing everything
        if 'owner' in self.tokens:
            self.run_test(
                "Owner Access Companies",
                "GET",
                "companies",
                200,
                token=self.tokens['owner'],
                description="Owner should access companies"
            )
            
            self.run_test(
                "Owner Access Users",
                "GET",
                "users",
                200,
                token=self.tokens['owner'],
                description="Owner should access users"
            )

        # Test admin restrictions
        if 'admin' in self.tokens:
            self.run_test(
                "Admin Blocked from Companies",
                "GET",
                "companies",
                403,
                token=self.tokens['admin'],
                description="Admin should not access companies"
            )
            
            self.run_test(
                "Admin Blocked from Users",
                "GET",
                "users",
                403,
                token=self.tokens['admin'],
                description="Admin should not access users"
            )

        # Test user restrictions
        if 'user' in self.tokens:
            self.run_test(
                "User Blocked from Companies",
                "GET",
                "companies",
                403,
                token=self.tokens['user'],
                description="User should not access companies"
            )

    def cleanup_created_resources(self):
        """Clean up resources created during testing"""
        self.log("\n=== CLEANUP ===")
        
        if 'owner' not in self.tokens and 'admin' not in self.tokens:
            self.log("❌ No tokens available for cleanup")
            return

        # Delete created time entries
        admin_token = self.tokens.get('admin')
        if admin_token:
            for entry_id in self.created_resources['time_entries']:
                self.run_test(
                    f"Delete Time Entry {entry_id}",
                    "DELETE",
                    f"time-entries/{entry_id}",
                    200,
                    token=admin_token,
                    description="Cleanup time entry"
                )

            # Delete created employees
            for employee_id in self.created_resources['employees']:
                self.run_test(
                    f"Delete Employee {employee_id}",
                    "DELETE",
                    f"employees/{employee_id}",
                    200,
                    token=admin_token,
                    description="Cleanup employee"
                )

        # Delete created users and companies (owner only)
        owner_token = self.tokens.get('owner')
        if owner_token:
            for user_id in self.created_resources['users']:
                self.run_test(
                    f"Delete User {user_id}",
                    "DELETE",
                    f"users/{user_id}",
                    200,
                    token=owner_token,
                    description="Cleanup user"
                )

            for company_id in self.created_resources['companies']:
                self.run_test(
                    f"Delete Company {company_id}",
                    "DELETE",
                    f"companies/{company_id}",
                    200,
                    token=owner_token,
                    description="Cleanup company"
                )

    def run_all_tests(self):
        """Run all API tests"""
        self.log("🚀 Starting TimeTracker Pro API Tests")
        self.log(f"   Base URL: {self.base_url}")
        self.log(f"   API URL: {self.api_url}")
        
        try:
            # Test authentication first
            self.test_authentication()
            
            # Test all API endpoints
            self.test_companies_api()
            self.test_users_api()
            self.test_employees_api()
            self.test_time_entries_api()
            self.test_role_based_access()
            
            # Cleanup
            self.cleanup_created_resources()
            
        except KeyboardInterrupt:
            self.log("\n⚠️ Tests interrupted by user")
        except Exception as e:
            self.log(f"\n💥 Unexpected error: {str(e)}")
        
        # Print final results
        self.log(f"\n📊 FINAL RESULTS:")
        self.log(f"   Tests run: {self.tests_run}")
        self.log(f"   Tests passed: {self.tests_passed}")
        self.log(f"   Tests failed: {self.tests_run - self.tests_passed}")
        self.log(f"   Success rate: {(self.tests_passed/self.tests_run*100):.1f}%" if self.tests_run > 0 else "   Success rate: 0%")
        
        if self.tests_passed == self.tests_run:
            self.log("🎉 All tests passed!")
            return 0
        else:
            self.log("❌ Some tests failed!")
            return 1

def main():
    tester = TimeTrackerAPITester()
    return tester.run_all_tests()

if __name__ == "__main__":
    sys.exit(main())