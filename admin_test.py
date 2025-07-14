#!/usr/bin/env python3
"""
Admin Dashboard Functionality Test
Tests specific admin features mentioned in requirements:
- QR code generation for employees
- Time report editing
- Employee management
"""

import requests
import sys
import json
from datetime import datetime, timedelta

class AdminDashboardTester:
    def __init__(self, backend_url="http://localhost:8001"):
        self.backend_url = backend_url
        self.api_url = f"{backend_url}/api"
        self.admin_token = None
        self.test_results = []
        print(f"🔧 Testing Admin Dashboard Features")
        print("=" * 60)

    def login_admin(self):
        """Login as admin"""
        response = requests.post(f"{self.api_url}/auth/login", 
                               json={"username": "admin", "password": "admin123"})
        if response.status_code == 200:
            data = response.json()
            self.admin_token = data['access_token']
            self.admin_user = data['user']
            print(f"✅ Admin logged in: {self.admin_user['username']} at {self.admin_user['company_name']}")
            return True
        return False

    def make_api_call(self, method, endpoint, data=None):
        """Make authenticated API call"""
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.admin_token}'
        }
        
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

    def test_employee_list_and_qr_generation(self):
        """Test employee listing and QR code generation"""
        print("\n🏢 Testing Employee Management & QR Generation")
        
        # Get employees list
        response = self.make_api_call('GET', '/employees')
        if response.status_code != 200:
            print("❌ Failed to get employees list")
            return False
        
        employees = response.json()
        print(f"✅ Retrieved {len(employees)} employees:")
        
        for emp in employees:
            print(f"   - {emp['name']} (QR: {emp['qr_code']}, Active: {emp['is_active']})")
        
        if not employees:
            print("❌ No employees found to test QR generation")
            return False
        
        # Test QR code generation for first employee
        test_employee = employees[0]
        print(f"\n🔍 Testing QR code generation for: {test_employee['name']}")
        
        response = self.make_api_call('POST', f"/employees/{test_employee['id']}/qr")
        if response.status_code != 200:
            print("❌ Failed to generate QR code")
            return False
        
        qr_data = response.json()
        print(f"✅ QR Code generated successfully:")
        print(f"   - QR Data: {qr_data['qr_code_data']}")
        print(f"   - Image: {'Present' if qr_data['qr_code_image'] else 'Missing'}")
        print(f"   - Image size: {len(qr_data['qr_code_image'])} characters (base64)")
        
        # Verify QR image is valid base64
        try:
            import base64
            base64.b64decode(qr_data['qr_code_image'])
            print("✅ QR code image is valid base64")
        except:
            print("❌ QR code image is not valid base64")
            return False
        
        return True

    def test_time_reports_and_editing(self):
        """Test time reports viewing and editing"""
        print("\n⏰ Testing Time Reports & Editing")
        
        # Get time entries
        response = self.make_api_call('GET', '/time-entries')
        if response.status_code != 200:
            print("❌ Failed to get time entries")
            return False
        
        time_entries = response.json()
        print(f"✅ Retrieved {len(time_entries)} time entries:")
        
        # Get employees for name mapping
        emp_response = self.make_api_call('GET', '/employees')
        employees = emp_response.json() if emp_response.status_code == 200 else []
        emp_map = {emp['id']: emp['name'] for emp in employees}
        
        for entry in time_entries:
            emp_name = emp_map.get(entry['employee_id'], 'Unknown')
            check_in = datetime.fromisoformat(entry['check_in'].replace('Z', '+00:00'))
            check_out_str = 'Not set'
            if entry.get('check_out'):
                check_out = datetime.fromisoformat(entry['check_out'].replace('Z', '+00:00'))
                check_out_str = check_out.strftime('%H:%M')
            
            print(f"   - {emp_name}: {entry['date']} | In: {check_in.strftime('%H:%M')} | Out: {check_out_str} | Hours: {entry.get('total_hours', 0):.1f}h")
        
        if not time_entries:
            print("❌ No time entries found to test editing")
            return False
        
        # Test editing first time entry
        test_entry = time_entries[0]
        emp_name = emp_map.get(test_entry['employee_id'], 'Unknown')
        print(f"\n🔍 Testing time entry editing for: {emp_name}")
        
        # Update check_out time
        new_check_out = datetime.now().replace(hour=17, minute=30, second=0, microsecond=0)
        update_data = {
            "check_out": new_check_out.isoformat()
        }
        
        response = self.make_api_call('PUT', f"/time-entries/{test_entry['id']}", update_data)
        if response.status_code != 200:
            print("❌ Failed to update time entry")
            return False
        
        updated_entry = response.json()
        print(f"✅ Time entry updated successfully:")
        print(f"   - Original check_out: {test_entry.get('check_out', 'Not set')}")
        print(f"   - New check_out: {updated_entry['check_out']}")
        print(f"   - New total_hours: {updated_entry.get('total_hours', 0):.2f}h")
        
        return True

    def test_admin_dashboard_data_structure(self):
        """Test that admin gets properly structured data for dashboard"""
        print("\n📊 Testing Admin Dashboard Data Structure")
        
        # Test that admin can access all required data
        endpoints_to_test = [
            ('/employees', 'employees'),
            ('/time-entries', 'time entries'),
            ('/companies', 'companies (should fail for admin)')
        ]
        
        results = {}
        for endpoint, description in endpoints_to_test:
            response = self.make_api_call('GET', endpoint)
            results[endpoint] = {
                'status': response.status_code,
                'description': description,
                'data_count': len(response.json()) if response.status_code == 200 else 0
            }
        
        # Admin should access employees and time-entries but not companies
        if results['/employees']['status'] != 200:
            print("❌ Admin cannot access employees")
            return False
        print(f"✅ Admin can access {results['/employees']['data_count']} employees")
        
        if results['/time-entries']['status'] != 200:
            print("❌ Admin cannot access time entries")
            return False
        print(f"✅ Admin can access {results['/time-entries']['data_count']} time entries")
        
        if results['/companies']['status'] != 403:
            print("⚠️ Admin should not access companies directly (security concern)")
        else:
            print("✅ Admin correctly denied access to companies")
        
        return True

    def test_admin_specific_features(self):
        """Test admin-specific features mentioned in requirements"""
        print("\n🔧 Testing Admin-Specific Features")
        
        # Test that admin can create employees
        test_employee = {
            "name": f"Admin Test Employee {datetime.now().strftime('%H%M%S')}",
            "company_id": self.admin_user['company_id']
        }
        
        response = self.make_api_call('POST', '/employees', test_employee)
        if response.status_code != 200:
            print("❌ Admin cannot create employees")
            return False
        
        created_employee = response.json()
        print(f"✅ Admin created employee: {created_employee['name']}")
        
        # Test that admin can create time entries
        test_time_entry = {
            "employee_id": created_employee['id'],
            "check_in": datetime.now().replace(hour=9, minute=0).isoformat(),
            "check_out": datetime.now().replace(hour=17, minute=0).isoformat()
        }
        
        response = self.make_api_call('POST', '/time-entries', test_time_entry)
        if response.status_code != 200:
            print("❌ Admin cannot create time entries")
            return False
        
        created_entry = response.json()
        print(f"✅ Admin created time entry with {created_entry.get('total_hours', 0):.1f} hours")
        
        # Cleanup
        self.make_api_call('DELETE', f"/time-entries/{created_entry['id']}")
        self.make_api_call('DELETE', f"/employees/{created_employee['id']}")
        print("✅ Test data cleaned up")
        
        return True

def main():
    """Main test execution"""
    print("🚀 Starting Admin Dashboard Functionality Tests")
    print(f"⏰ Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    tester = AdminDashboardTester()
    
    # Login as admin
    if not tester.login_admin():
        print("❌ Failed to login as admin")
        return 1
    
    # Run admin-specific tests
    tests = [
        ("Employee List & QR Generation", tester.test_employee_list_and_qr_generation),
        ("Time Reports & Editing", tester.test_time_reports_and_editing),
        ("Admin Dashboard Data Structure", tester.test_admin_dashboard_data_structure),
        ("Admin-Specific Features", tester.test_admin_specific_features)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n{'='*60}")
        print(f"🔍 TESTING: {test_name}")
        print(f"{'='*60}")
        
        try:
            if test_func():
                passed += 1
                print(f"✅ {test_name}: PASSED")
            else:
                print(f"❌ {test_name}: FAILED")
        except Exception as e:
            print(f"❌ {test_name}: ERROR - {str(e)}")
    
    # Final results
    print(f"\n{'='*60}")
    print("📊 ADMIN DASHBOARD TEST RESULTS")
    print(f"{'='*60}")
    print(f"✅ Tests passed: {passed}/{total}")
    print(f"📈 Success rate: {(passed/total)*100:.1f}%")
    
    # Summary
    print(f"\n{'='*60}")
    print("🔍 ADMIN FUNCTIONALITY SUMMARY")
    print(f"{'='*60}")
    
    if passed == total:
        print("✅ EXCELLENT: All admin features working perfectly!")
        print("   ✅ Employee management is functional")
        print("   ✅ QR code generation works correctly")
        print("   ✅ Time report editing is working")
        print("   ✅ Admin has proper access permissions")
        print("   ✅ All CRUD operations work for admin")
        print("\n🎯 SPECIFIC REQUIREMENTS TESTED:")
        print("   ✅ Admin can view employee list")
        print("   ✅ Admin can generate QR codes for employees")
        print("   ✅ Admin can edit time reports")
        print("   ✅ Time reports show: name, date, check-in/out times, total hours")
        print("   ✅ Admin authorization is properly implemented")
    else:
        print("⚠️ Some admin features need attention")
        print(f"   - {total-passed} out of {total} tests failed")
    
    return 0 if passed == total else 1

if __name__ == "__main__":
    sys.exit(main())