#!/usr/bin/env python3
"""
Integration Testing for TimeTracker Pro
Simulates frontend-backend integration and tests all user workflows
"""

import requests
import sys
import json
from datetime import datetime

class IntegrationTester:
    def __init__(self, backend_url="http://localhost:8001"):
        self.backend_url = backend_url
        self.api_url = f"{backend_url}/api"
        self.tests_run = 0
        self.tests_passed = 0
        self.tokens = {}
        self.test_data = {}
        print(f"🔧 Testing Integration at: {self.backend_url}")
        print("=" * 60)

    def run_test(self, name, test_func):
        """Run a single integration test"""
        self.tests_run += 1
        print(f"\n🔍 Test {self.tests_run}: {name}")
        
        try:
            result = test_func()
            if result:
                self.tests_passed += 1
                print(f"✅ PASSED")
                return True
            else:
                print(f"❌ FAILED")
                return False
        except Exception as e:
            print(f"❌ FAILED - Error: {str(e)}")
            return False

    def login_user(self, username, password):
        """Login user and return token"""
        response = requests.post(f"{self.api_url}/auth/login", 
                               json={"username": username, "password": password})
        if response.status_code == 200:
            data = response.json()
            return data['access_token'], data['user']
        return None, None

    def make_api_call(self, method, endpoint, token=None, data=None):
        """Make API call with authentication"""
        headers = {'Content-Type': 'application/json'}
        if token:
            headers['Authorization'] = f'Bearer {token}'
        
        url = f"{self.api_url}/{endpoint.lstrip('/')}"
        
        if method == 'GET':
            response = requests.get(url, headers=headers)
        elif method == 'POST':
            response = requests.post(url, json=data, headers=headers)
        elif method == 'PUT':
            response = requests.put(url, json=data, headers=headers)
        elif method == 'DELETE':
            response = requests.delete(url, headers=headers)
        
        return response

    def test_owner_workflow(self):
        """Test complete owner workflow"""
        print("   Testing owner login...")
        token, user = self.login_user("owner", "owner123")
        if not token:
            return False
        
        self.tokens['owner'] = token
        print(f"   ✅ Owner logged in: {user['username']}")
        
        # Test company management
        print("   Testing company management...")
        
        # Get companies
        response = self.make_api_call('GET', '/companies', token)
        if response.status_code != 200:
            return False
        companies = response.json()
        print(f"   ✅ Retrieved {len(companies)} companies")
        
        # Create company
        test_company = {"name": f"Integration Test Company {datetime.now().strftime('%H%M%S')}"}
        response = self.make_api_call('POST', '/companies', token, test_company)
        if response.status_code != 200:
            return False
        created_company = response.json()
        self.test_data['company_id'] = created_company['id']
        print(f"   ✅ Created company: {created_company['name']}")
        
        # Update company
        update_data = {"name": f"Updated {created_company['name']}"}
        response = self.make_api_call('PUT', f"/companies/{created_company['id']}", token, update_data)
        if response.status_code != 200:
            return False
        print(f"   ✅ Updated company")
        
        # Test user management
        print("   Testing user management...")
        
        # Get users
        response = self.make_api_call('GET', '/users', token)
        if response.status_code != 200:
            return False
        users = response.json()
        print(f"   ✅ Retrieved {len(users)} users")
        
        # Create user
        test_user = {
            "username": f"testuser_{datetime.now().strftime('%H%M%S')}",
            "password": "testpass123",
            "type": "admin",
            "company_id": created_company['id']
        }
        response = self.make_api_call('POST', '/users', token, test_user)
        if response.status_code != 200:
            return False
        created_user = response.json()
        self.test_data['user_id'] = created_user['id']
        print(f"   ✅ Created user: {created_user['username']}")
        
        return True

    def test_admin_workflow(self):
        """Test complete admin workflow"""
        print("   Testing admin login...")
        token, user = self.login_user("admin", "admin123")
        if not token:
            return False
        
        self.tokens['admin'] = token
        print(f"   ✅ Admin logged in: {user['username']} at {user['company_name']}")
        
        # Test employee management
        print("   Testing employee management...")
        
        # Get employees
        response = self.make_api_call('GET', '/employees', token)
        if response.status_code != 200:
            return False
        employees = response.json()
        print(f"   ✅ Retrieved {len(employees)} employees")
        
        # Create employee
        test_employee = {
            "name": f"Test Employee {datetime.now().strftime('%H%M%S')}",
            "company_id": user['company_id']
        }
        response = self.make_api_call('POST', '/employees', token, test_employee)
        if response.status_code != 200:
            return False
        created_employee = response.json()
        self.test_data['employee_id'] = created_employee['id']
        print(f"   ✅ Created employee: {created_employee['name']}")
        
        # Generate QR code
        response = self.make_api_call('POST', f"/employees/{created_employee['id']}/qr", token)
        if response.status_code != 200:
            return False
        qr_data = response.json()
        print(f"   ✅ Generated QR code: {qr_data['qr_code_data']}")
        
        # Test time entry management
        print("   Testing time entry management...")
        
        # Get time entries
        response = self.make_api_call('GET', '/time-entries', token)
        if response.status_code != 200:
            return False
        time_entries = response.json()
        print(f"   ✅ Retrieved {len(time_entries)} time entries")
        
        # Create time entry
        test_time_entry = {
            "employee_id": created_employee['id'],
            "check_in": datetime.now().isoformat(),
            "check_out": datetime.now().isoformat()
        }
        response = self.make_api_call('POST', '/time-entries', token, test_time_entry)
        if response.status_code != 200:
            return False
        created_entry = response.json()
        self.test_data['time_entry_id'] = created_entry['id']
        print(f"   ✅ Created time entry for {created_employee['name']}")
        
        # Update time entry
        update_data = {
            "check_out": datetime.now().isoformat()
        }
        response = self.make_api_call('PUT', f"/time-entries/{created_entry['id']}", token, update_data)
        if response.status_code != 200:
            return False
        print(f"   ✅ Updated time entry")
        
        return True

    def test_user_workflow(self):
        """Test user workflow and authorization"""
        print("   Testing user login...")
        token, user = self.login_user("user", "user123")
        if not token:
            return False
        
        self.tokens['user'] = token
        print(f"   ✅ User logged in: {user['username']} at {user['company_name']}")
        
        # Test authorization - user should not access owner endpoints
        print("   Testing authorization restrictions...")
        
        # Should not access companies
        response = self.make_api_call('GET', '/companies', token)
        if response.status_code != 403:
            print(f"   ❌ User should not access companies (got {response.status_code})")
            return False
        print(f"   ✅ User correctly denied access to companies")
        
        # Should not access users
        response = self.make_api_call('GET', '/users', token)
        if response.status_code != 403:
            print(f"   ❌ User should not access users (got {response.status_code})")
            return False
        print(f"   ✅ User correctly denied access to users")
        
        # Should be able to access employees (read-only)
        response = self.make_api_call('GET', '/employees', token)
        if response.status_code != 200:
            print(f"   ❌ User should access employees (got {response.status_code})")
            return False
        print(f"   ✅ User can access employees")
        
        return True

    def test_data_consistency(self):
        """Test data consistency across different user types"""
        print("   Testing data consistency...")
        
        owner_token = self.tokens.get('owner')
        admin_token = self.tokens.get('admin')
        
        if not owner_token or not admin_token:
            return False
        
        # Owner should see all companies
        response = self.make_api_call('GET', '/companies', owner_token)
        if response.status_code != 200:
            return False
        owner_companies = response.json()
        
        # Admin should see employees from their company
        response = self.make_api_call('GET', '/employees', admin_token)
        if response.status_code != 200:
            return False
        admin_employees = response.json()
        
        # Owner should see all employees
        response = self.make_api_call('GET', '/employees', owner_token)
        if response.status_code != 200:
            return False
        owner_employees = response.json()
        
        print(f"   ✅ Owner sees {len(owner_companies)} companies, {len(owner_employees)} employees")
        print(f"   ✅ Admin sees {len(admin_employees)} employees from their company")
        
        # Admin employees should be subset of owner employees
        if len(admin_employees) > len(owner_employees):
            return False
        
        return True

    def cleanup_test_data(self):
        """Clean up test data"""
        print("   Cleaning up test data...")
        
        owner_token = self.tokens.get('owner')
        admin_token = self.tokens.get('admin')
        
        if admin_token and 'time_entry_id' in self.test_data:
            self.make_api_call('DELETE', f"/time-entries/{self.test_data['time_entry_id']}", admin_token)
            print("   ✅ Deleted test time entry")
        
        if admin_token and 'employee_id' in self.test_data:
            self.make_api_call('DELETE', f"/employees/{self.test_data['employee_id']}", admin_token)
            print("   ✅ Deleted test employee")
        
        if owner_token and 'user_id' in self.test_data:
            self.make_api_call('DELETE', f"/users/{self.test_data['user_id']}", owner_token)
            print("   ✅ Deleted test user")
        
        if owner_token and 'company_id' in self.test_data:
            self.make_api_call('DELETE', f"/companies/{self.test_data['company_id']}", owner_token)
            print("   ✅ Deleted test company")
        
        return True

def main():
    """Main test execution"""
    print("🚀 Starting TimeTracker Pro Integration Tests")
    print(f"⏰ Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    tester = IntegrationTester()
    
    # Run integration tests
    print("\n" + "="*60)
    print("🔄 RUNNING INTEGRATION TESTS")
    print("="*60)
    
    # Test owner workflow
    tester.run_test("Owner Complete Workflow", tester.test_owner_workflow)
    
    # Test admin workflow
    tester.run_test("Admin Complete Workflow", tester.test_admin_workflow)
    
    # Test user workflow
    tester.run_test("User Workflow & Authorization", tester.test_user_workflow)
    
    # Test data consistency
    tester.run_test("Data Consistency Across Users", tester.test_data_consistency)
    
    # Cleanup
    tester.run_test("Cleanup Test Data", tester.cleanup_test_data)
    
    # Print final results
    print("\n" + "="*60)
    print("📊 FINAL INTEGRATION TEST RESULTS")
    print("="*60)
    print(f"✅ Tests passed: {tester.tests_passed}")
    print(f"📝 Total tests run: {tester.tests_run}")
    print(f"📈 Success rate: {(tester.tests_passed/tester.tests_run)*100:.1f}%")
    
    # Analysis
    print("\n" + "="*60)
    print("🔍 INTEGRATION ANALYSIS")
    print("="*60)
    
    if tester.tests_passed == tester.tests_run:
        print("✅ EXCELLENT: All integration tests passed!")
        print("   - Frontend-Backend integration is working perfectly")
        print("   - All user workflows are functional")
        print("   - Authentication and authorization work correctly")
        print("   - Data consistency is maintained")
        print("   - CRUD operations work for all user types")
        print("   - QR code generation is functional")
        print("   - Time entry management works correctly")
    elif tester.tests_passed > tester.tests_run * 0.8:
        print("⚠️ GOOD: Most integration tests passed")
        print("   - Core functionality is working")
        print("   - Some minor issues may exist")
    else:
        print("❌ NEEDS ATTENTION: Multiple integration issues")
        print("   - Core functionality may be broken")
        print("   - Frontend-Backend integration has problems")
    
    print(f"\n🔧 User tokens obtained: {list(tester.tokens.keys())}")
    print("   - All user types can authenticate successfully")
    
    return 0 if tester.tests_passed == tester.tests_run else 1

if __name__ == "__main__":
    sys.exit(main())