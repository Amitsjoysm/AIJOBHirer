#!/usr/bin/env python3
"""
HireFlow AI Backend API Testing Suite - Simplified Version
Tests all backend endpoints comprehensively
"""

import asyncio
import aiohttp
import json
import sys
from typing import Dict, Any, Optional
from datetime import datetime

# Backend URL from frontend/.env
BACKEND_URL = "https://hireflow-app-1.preview.emergentagent.com/api"

# Test credentials from seed data
TEST_CREDENTIALS = [
    {"email": "admin@techcorp.com", "password": "password123", "role": "admin"},
    {"email": "hr@innovateai.com", "password": "password123", "role": "hiring_manager"},
    {"email": "recruiter@greenventures.com", "password": "password123", "role": "recruiter"}
]

class APITester:
    def __init__(self):
        self.session = None
        self.tokens = {}
        self.test_results = {}
        self.companies = {}
        self.jobs = {}
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def login_user(self, email: str, password: str) -> Optional[str]:
        """Login user and return access token"""
        form_data = aiohttp.FormData()
        form_data.add_field('username', email)
        form_data.add_field('password', password)
        
        try:
            url = f"{BACKEND_URL}/auth/login"
            async with self.session.post(url, data=form_data) as response:
                if response.status == 200:
                    token_data = await response.json()
                    return token_data['access_token']
                else:
                    print(f"Login failed for {email}: {response.status}")
                    return None
        except Exception as e:
            print(f"Login error for {email}: {str(e)}")
            return None
    
    async def make_authenticated_request(self, method: str, endpoint: str, token: str, 
                                       data: Dict = None, params: Dict = None) -> Dict[str, Any]:
        """Make authenticated HTTP request"""
        headers = {"Authorization": f"Bearer {token}"}
        
        # Specific endpoints that need trailing slash to avoid redirects
        endpoints_needing_slash = ["/companies", "/candidates", "/email-config", "/jobs", "/applications"]
        
        if any(endpoint.startswith(ep) and endpoint == ep for ep in endpoints_needing_slash):
            endpoint = endpoint + '/'
        
        url = f"{BACKEND_URL}{endpoint}"
        
        try:
            async with self.session.request(
                method, url, json=data, headers=headers, params=params
            ) as response:
                try:
                    response_data = await response.json()
                except:
                    response_data = {"text": await response.text()}
                
                return {
                    "status": response.status,
                    "data": response_data,
                    "success": 200 <= response.status < 300
                }
        except Exception as e:
            return {
                "status": 0,
                "data": {"error": str(e)},
                "success": False
            }
    
    async def make_public_request(self, method: str, endpoint: str, data: Dict = None) -> Dict[str, Any]:
        """Make public HTTP request"""
        # Specific endpoints that need trailing slash to avoid redirects
        endpoints_needing_slash = ["/applications"]
        
        if any(endpoint.startswith(ep) and endpoint == ep for ep in endpoints_needing_slash):
            endpoint = endpoint + '/'
        
        url = f"{BACKEND_URL}{endpoint}"
        
        try:
            async with self.session.request(method, url, json=data) as response:
                try:
                    response_data = await response.json()
                except:
                    response_data = {"text": await response.text()}
                
                return {
                    "status": response.status,
                    "data": response_data,
                    "success": 200 <= response.status < 300
                }
        except Exception as e:
            return {
                "status": 0,
                "data": {"error": str(e)},
                "success": False
            }
    
    async def test_authentication(self):
        """Test authentication endpoints"""
        print("\n🔐 Testing Authentication...")
        auth_success = True
        
        # Test login for all users
        for cred in TEST_CREDENTIALS:
            print(f"  Testing login for {cred['email']}...")
            token = await self.login_user(cred['email'], cred['password'])
            
            if token:
                self.tokens[cred['email']] = token
                print(f"  ✅ Login successful for {cred['email']}")
                
                # Test /me endpoint
                result = await self.make_authenticated_request("GET", "/auth/me", token)
                if result["success"]:
                    print(f"  ✅ /me endpoint working for {cred['email']}")
                else:
                    print(f"  ❌ /me endpoint failed for {cred['email']}: {result['data']}")
                    auth_success = False
            else:
                print(f"  ❌ Login failed for {cred['email']}")
                auth_success = False
        
        # Test registration with a unique email
        print("  Testing user registration...")
        unique_email = f"test_user_{datetime.now().strftime('%Y%m%d%H%M%S')}@example.com"
        register_data = {
            "email": unique_email,
            "password": "testpass123",
            "full_name": "Test User",
            "role": "hiring_manager"
        }
        
        result = await self.make_public_request("POST", "/auth/register", register_data)
        if result["success"]:
            print("  ✅ User registration successful")
        else:
            print(f"  ❌ User registration failed: {result['data']}")
            auth_success = False
        
        self.test_results["authentication"] = auth_success
        return auth_success
    
    async def test_company_management(self):
        """Test company management endpoints"""
        print("\n🏢 Testing Company Management...")
        company_success = True
        
        if not self.tokens:
            print("  ❌ No authenticated users available")
            self.test_results["company_management"] = False
            return False
        
        # Use first authenticated user
        test_email = list(self.tokens.keys())[0]
        token = self.tokens[test_email]
        
        # Test get companies
        print("  Testing GET /companies...")
        result = await self.make_authenticated_request("GET", "/companies", token)
        if result["success"]:
            print(f"  ✅ GET /companies successful - found {len(result['data'])} companies")
            if result["data"]:
                self.companies[test_email] = result["data"][0]["id"]
        else:
            print(f"  ❌ GET /companies failed: {result['data']}")
            company_success = False
        
        # Test create company
        print("  Testing POST /companies...")
        company_data = {
            "name": "Test Company Ltd",
            "slug": f"test-company-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "industry": "Technology",
            "description": "A test company for API testing",
            "website": "https://testcompany.com"
        }
        
        result = await self.make_authenticated_request("POST", "/companies", token, company_data)
        if result["success"]:
            print("  ✅ POST /companies successful")
            company_id = result["data"]["id"]
            self.companies[test_email] = company_id
            
            # Test get specific company
            print(f"  Testing GET /companies/{company_id}...")
            result = await self.make_authenticated_request("GET", f"/companies/{company_id}", token)
            if result["success"]:
                print("  ✅ GET /companies/{id} successful")
            else:
                print(f"  ❌ GET /companies/{company_id} failed: {result['data']}")
                company_success = False
        else:
            print(f"  ❌ POST /companies failed: {result['data']}")
            company_success = False
        
        self.test_results["company_management"] = company_success
        return company_success
    
    async def test_job_management(self):
        """Test job management endpoints"""
        print("\n💼 Testing Job Management...")
        job_success = True
        
        if not self.companies:
            print("  ❌ No companies available for job testing")
            self.test_results["job_management"] = False
            return False
        
        test_email = list(self.companies.keys())[0]
        token = self.tokens[test_email]
        company_id = self.companies[test_email]
        
        # Test get my jobs
        print("  Testing GET /jobs/my-jobs...")
        result = await self.make_authenticated_request("GET", "/jobs/my-jobs", token)
        if result["success"]:
            print(f"  ✅ GET /jobs/my-jobs successful - found {len(result['data'])} jobs")
        else:
            print(f"  ❌ GET /jobs/my-jobs failed: {result['data']}")
            job_success = False
        
        # Test create job
        print("  Testing POST /jobs...")
        job_data = {
            "title": "Senior Python Developer",
            "department": "Engineering",
            "description": "We are looking for a senior Python developer",
            "requirements": ["5+ years Python experience", "FastAPI knowledge"],
            "nice_to_have": ["AWS experience"],
            "job_type": "full_time",
            "location_type": "remote",
            "location": "Remote",
            "experience_level": "senior",
            "salary_min": 80000,
            "salary_max": 120000,
            "salary_currency": "USD",
            "screening_questions": [
                {"question": "Years of Python experience?", "required": True}
            ],
            "use_ai_generation": False
        }
        
        result = await self.make_authenticated_request("POST", "/jobs", token, job_data)
        if result["success"]:
            print("  ✅ POST /jobs successful")
            job_id = result["data"]["id"]
            self.jobs[test_email] = job_id
            
            # Test get specific job (public)
            print(f"  Testing GET /jobs/{job_id}...")
            result = await self.make_public_request("GET", f"/jobs/{job_id}")
            if result["success"]:
                print("  ✅ GET /jobs/{id} successful")
            else:
                print(f"  ❌ GET /jobs/{job_id} failed: {result['data']}")
                job_success = False
            
            # Update job to active status for application testing
            print(f"  Testing PATCH /jobs/{job_id} (activate)...")
            update_data = {"status": "active"}
            result = await self.make_authenticated_request("PATCH", f"/jobs/{job_id}", token, update_data)
            if result["success"]:
                print("  ✅ PATCH /jobs/{id} successful (job activated)")
            else:
                print(f"  ❌ PATCH /jobs/{job_id} failed: {result['data']}")
                job_success = False
        else:
            print(f"  ❌ POST /jobs failed: {result['data']}")
            job_success = False
        
        # Test get company jobs (public)
        print(f"  Testing GET /jobs/company/{company_id}...")
        result = await self.make_public_request("GET", f"/jobs/company/{company_id}")
        if result["success"]:
            print(f"  ✅ GET /jobs/company/{company_id} successful - found {len(result['data'])} jobs")
        else:
            print(f"  ❌ GET /jobs/company/{company_id} failed: {result['data']}")
            job_success = False
        
        self.test_results["job_management"] = job_success
        return job_success
    
    async def test_application_management(self):
        """Test application management endpoints"""
        print("\n📝 Testing Application Management...")
        app_success = True
        
        if not self.jobs:
            print("  ❌ No jobs available for application testing")
            self.test_results["application_management"] = False
            return False
        
        test_email = list(self.jobs.keys())[0]
        token = self.tokens[test_email]
        job_id = self.jobs[test_email]
        
        # Test submit application (public)
        print("  Testing POST /applications (public)...")
        app_data = {
            "job_id": job_id,
            "candidate_email": "john.doe@example.com",
            "candidate_name": "John Doe",
            "candidate_phone": "+1234567890",
            "candidate_linkedin": "https://linkedin.com/in/johndoe",
            "resume_url": "https://example.com/resume.pdf",
            "questionnaire_answers": [
                {"question": "Years of experience?", "answer": "5 years"}
            ]
        }
        
        result = await self.make_public_request("POST", "/applications", app_data)
        if result["success"]:
            print("  ✅ POST /applications successful")
            
            # Test get applications for job
            print(f"  Testing GET /applications/job/{job_id}...")
            result = await self.make_authenticated_request("GET", f"/applications/job/{job_id}", token)
            if result["success"]:
                print(f"  ✅ GET /applications/job/{job_id} successful - found {len(result['data'])} applications")
                
                if result["data"]:
                    app_id = result["data"][0]["id"]
                    
                    # Test get specific application
                    print(f"  Testing GET /applications/{app_id}...")
                    result = await self.make_authenticated_request("GET", f"/applications/{app_id}", token)
                    if result["success"]:
                        print("  ✅ GET /applications/{id} successful")
                    else:
                        print(f"  ❌ GET /applications/{app_id} failed: {result['data']}")
                        app_success = False
            else:
                print(f"  ❌ GET /applications/job/{job_id} failed: {result['data']}")
                app_success = False
        else:
            print(f"  ❌ POST /applications failed: {result['data']}")
            app_success = False
        
        self.test_results["application_management"] = app_success
        return app_success
    
    async def test_candidate_management(self):
        """Test candidate management endpoints"""
        print("\n👥 Testing Candidate Management...")
        candidate_success = True
        
        if not self.tokens:
            print("  ❌ No authenticated users available")
            self.test_results["candidate_management"] = False
            return False
        
        test_email = list(self.tokens.keys())[0]
        token = self.tokens[test_email]
        
        # Test get candidates
        print("  Testing GET /candidates...")
        result = await self.make_authenticated_request("GET", "/candidates", token)
        if result["success"]:
            print(f"  ✅ GET /candidates successful - found {len(result['data'])} candidates")
            
            if result["data"]:
                candidate_id = result["data"][0]["id"]
                print(f"  Testing GET /candidates/{candidate_id}...")
                result = await self.make_authenticated_request("GET", f"/candidates/{candidate_id}", token)
                if result["success"]:
                    print("  ✅ GET /candidates/{id} successful")
                else:
                    print(f"  ❌ GET /candidates/{candidate_id} failed: {result['data']}")
                    candidate_success = False
        else:
            print(f"  ❌ GET /candidates failed: {result['data']}")
            candidate_success = False
        
        self.test_results["candidate_management"] = candidate_success
        return candidate_success
    
    async def test_analytics(self):
        """Test analytics endpoints"""
        print("\n📊 Testing Analytics...")
        analytics_success = True
        
        if not self.tokens:
            print("  ❌ No authenticated users available")
            self.test_results["analytics"] = False
            return False
        
        test_email = list(self.tokens.keys())[0]
        token = self.tokens[test_email]
        
        # Test dashboard analytics
        print("  Testing GET /analytics/dashboard...")
        result = await self.make_authenticated_request("GET", "/analytics/dashboard", token)
        if result["success"]:
            print("  ✅ GET /analytics/dashboard successful")
        else:
            print(f"  ❌ GET /analytics/dashboard failed: {result['data']}")
            analytics_success = False
        
        self.test_results["analytics"] = analytics_success
        return analytics_success
    
    async def run_all_tests(self):
        """Run all backend tests"""
        print("🚀 Starting HireFlow AI Backend API Tests")
        print(f"Backend URL: {BACKEND_URL}")
        print("=" * 60)
        
        # Run tests in order
        await self.test_authentication()
        await self.test_company_management()
        await self.test_job_management()
        await self.test_application_management()
        await self.test_candidate_management()
        await self.test_analytics()
        
        # Print summary
        print("\n" + "=" * 60)
        print("📋 TEST SUMMARY")
        print("=" * 60)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results.values() if result)
        
        for test_name, result in self.test_results.items():
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"{status} {test_name.replace('_', ' ').title()}")
        
        print(f"\nOverall: {passed_tests}/{total_tests} tests passed")
        
        if passed_tests == total_tests:
            print("🎉 All tests passed!")
            return True
        else:
            print("⚠️ Some tests failed - check logs above")
            return False

async def main():
    """Main test runner"""
    async with APITester() as tester:
        success = await tester.run_all_tests()
        return 0 if success else 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)