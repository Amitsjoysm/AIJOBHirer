#!/usr/bin/env python3
"""
HireFlow AI Backend API Testing Suite
Tests all backend endpoints comprehensively
"""

import asyncio
import aiohttp
import json
import sys
from typing import Dict, Any, Optional
from datetime import datetime

# Backend URL from frontend/.env
BACKEND_URL = "https://deploy-prep-13.preview.emergentagent.com/api"

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
    
    async def make_request(self, method: str, endpoint: str, data: Dict = None, 
                         headers: Dict = None, params: Dict = None) -> Dict[str, Any]:
        """Make HTTP request and return response data"""
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
    
    def get_auth_headers(self, user_email: str) -> Dict[str, str]:
        """Get authorization headers for user"""
        token = self.tokens.get(user_email)
        if token:
            return {"Authorization": f"Bearer {token}"}
        return {}
    
    async def test_health_check(self):
        """Test health endpoint"""
        print("🔍 Testing Health Check...")
        result = await self.make_request("GET", "/health")
        
        if result["success"]:
            print("✅ Health check passed")
            self.test_results["health_check"] = True
        else:
            print(f"❌ Health check failed: {result['data']}")
            self.test_results["health_check"] = False
        
        return result["success"]
    
    async def test_authentication(self):
        """Test authentication endpoints"""
        print("\n🔐 Testing Authentication...")
        auth_success = True
        
        # Test registration (create new user)
        print("  Testing user registration...")
        register_data = {
            "email": "test_user@example.com",
            "password": "testpass123",
            "full_name": "Test User",
            "role": "hiring_manager"
        }
        
        result = await self.make_request("POST", "/auth/register", register_data)
        if result["success"]:
            print("  ✅ User registration successful")
            # Store token for new user
            if "access_token" in result["data"]:
                self.tokens["test_user@example.com"] = result["data"]["access_token"]
        else:
            print(f"  ❌ User registration failed: {result['data']}")
            auth_success = False
        
        # Test login with existing users
        for cred in TEST_CREDENTIALS:
            print(f"  Testing login for {cred['email']}...")
            
            # Use form data for OAuth2PasswordRequestForm
            form_data = aiohttp.FormData()
            form_data.add_field('username', cred['email'])
            form_data.add_field('password', cred['password'])
            
            try:
                url = f"{BACKEND_URL}/auth/login"
                async with self.session.post(url, data=form_data) as response:
                    if response.status == 200:
                        token_data = await response.json()
                        self.tokens[cred['email']] = token_data['access_token']
                        print(f"  ✅ Login successful for {cred['email']}")
                    else:
                        error_data = await response.text()
                        print(f"  ❌ Login failed for {cred['email']}: {error_data}")
                        auth_success = False
            except Exception as e:
                print(f"  ❌ Login error for {cred['email']}: {str(e)}")
                auth_success = False
        
        # Test /me endpoint for each logged in user
        for email in self.tokens:
            print(f"  Testing /me endpoint for {email}...")
            headers = self.get_auth_headers(email)
            result = await self.make_request("GET", "/auth/me", headers=headers)
            
            if result["success"]:
                print(f"  ✅ /me endpoint working for {email}")
            else:
                print(f"  ❌ /me endpoint failed for {email}: {result['data']}")
                auth_success = False
        
        self.test_results["authentication"] = auth_success
        return auth_success
    
    async def test_company_management(self):
        """Test company management endpoints"""
        print("\n🏢 Testing Company Management...")
        company_success = True
        
        # Use first authenticated user
        test_email = list(self.tokens.keys())[0] if self.tokens else None
        if not test_email:
            print("  ❌ No authenticated users available")
            self.test_results["company_management"] = False
            return False
        
        headers = self.get_auth_headers(test_email)
        
        # Test get companies
        print("  Testing GET /companies...")
        result = await self.make_request("GET", "/companies", headers=headers)
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
        
        result = await self.make_request("POST", "/companies", company_data, headers=headers)
        if result["success"]:
            print("  ✅ POST /companies successful")
            company_id = result["data"]["id"]
            self.companies[test_email] = company_id
            
            # Test get specific company
            print(f"  Testing GET /companies/{company_id}...")
            result = await self.make_request("GET", f"/companies/{company_id}", headers=headers)
            if result["success"]:
                print("  ✅ GET /companies/{id} successful")
            else:
                print(f"  ❌ GET /companies/{company_id} failed: {result['data']}")
                company_success = False
            
            # Test update company
            print(f"  Testing PATCH /companies/{company_id}...")
            update_data = {"description": "Updated test company description"}
            result = await self.make_request("PATCH", f"/companies/{company_id}", update_data, headers=headers)
            if result["success"]:
                print("  ✅ PATCH /companies/{id} successful")
            else:
                print(f"  ❌ PATCH /companies/{company_id} failed: {result['data']}")
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
        
        # Use first authenticated user with company
        test_email = list(self.companies.keys())[0] if self.companies else None
        if not test_email:
            print("  ❌ No companies available for job testing")
            self.test_results["job_management"] = False
            return False
        
        headers = self.get_auth_headers(test_email)
        company_id = self.companies[test_email]
        
        # Test get my jobs
        print("  Testing GET /jobs/my-jobs...")
        result = await self.make_request("GET", "/jobs/my-jobs", headers=headers)
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
        
        result = await self.make_request("POST", "/jobs", job_data, headers=headers)
        if result["success"]:
            print("  ✅ POST /jobs successful")
            job_id = result["data"]["id"]
            self.jobs[test_email] = job_id
            
            # Test get specific job
            print(f"  Testing GET /jobs/{job_id}...")
            result = await self.make_request("GET", f"/jobs/{job_id}")
            if result["success"]:
                print("  ✅ GET /jobs/{id} successful")
            else:
                print(f"  ❌ GET /jobs/{job_id} failed: {result['data']}")
                job_success = False
            
            # Test update job
            print(f"  Testing PATCH /jobs/{job_id}...")
            update_data = {"status": "active"}
            result = await self.make_request("PATCH", f"/jobs/{job_id}", update_data, headers=headers)
            if result["success"]:
                print("  ✅ PATCH /jobs/{id} successful")
            else:
                print(f"  ❌ PATCH /jobs/{job_id} failed: {result['data']}")
                job_success = False
        else:
            print(f"  ❌ POST /jobs failed: {result['data']}")
            job_success = False
        
        # Test get company jobs (public endpoint)
        print(f"  Testing GET /jobs/company/{company_id}...")
        result = await self.make_request("GET", f"/jobs/company/{company_id}")
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
        
        # Use authenticated user with job
        test_email = list(self.jobs.keys())[0] if self.jobs else None
        if not test_email:
            print("  ❌ No jobs available for application testing")
            self.test_results["application_management"] = False
            return False
        
        headers = self.get_auth_headers(test_email)
        job_id = self.jobs[test_email]
        
        # Test get applications for job (correct endpoint)
        print(f"  Testing GET /applications/job/{job_id}...")
        result = await self.make_request("GET", f"/applications/job/{job_id}", headers=headers)
        if result["success"]:
            print(f"  ✅ GET /applications/job/{job_id} successful - found {len(result['data'])} applications")
            
            # If applications exist, test getting specific application
            if result["data"]:
                app_id = result["data"][0]["id"]
                print(f"  Testing GET /applications/{app_id}...")
                result = await self.make_request("GET", f"/applications/{app_id}", headers=headers)
                if result["success"]:
                    print("  ✅ GET /applications/{id} successful")
                else:
                    print(f"  ❌ GET /applications/{app_id} failed: {result['data']}")
                    app_success = False
                
                # Test update application status
                print(f"  Testing PATCH /applications/{app_id}/status...")
                status_data = {"status": "screening", "notes": "Initial screening"}
                result = await self.make_request("PATCH", f"/applications/{app_id}/status", status_data, headers=headers)
                if result["success"]:
                    print("  ✅ PATCH /applications/{id}/status successful")
                else:
                    print(f"  ❌ PATCH /applications/{app_id}/status failed: {result['data']}")
                    app_success = False
        else:
            print(f"  ❌ GET /applications/job/{job_id} failed: {result['data']}")
            app_success = False
        
        # Test submit application (public endpoint)
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
        
        result = await self.make_request("POST", "/applications", app_data)
        if result["success"]:
            print("  ✅ POST /applications successful")
        else:
            print(f"  ❌ POST /applications failed: {result['data']}")
            app_success = False
        
        self.test_results["application_management"] = app_success
        return app_success
    
    async def test_candidate_management(self):
        """Test candidate management endpoints"""
        print("\n👥 Testing Candidate Management...")
        candidate_success = True
        
        # Use authenticated user
        test_email = list(self.tokens.keys())[0] if self.tokens else None
        if not test_email:
            print("  ❌ No authenticated users available")
            self.test_results["candidate_management"] = False
            return False
        
        headers = self.get_auth_headers(test_email)
        
        # Test get candidates
        print("  Testing GET /candidates...")
        result = await self.make_request("GET", "/candidates", headers=headers)
        if result["success"]:
            print(f"  ✅ GET /candidates successful - found {len(result['data'])} candidates")
            
            # If candidates exist, test getting specific candidate
            if result["data"]:
                candidate_id = result["data"][0]["id"]
                print(f"  Testing GET /candidates/{candidate_id}...")
                result = await self.make_request("GET", f"/candidates/{candidate_id}", headers=headers)
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
    
    async def test_interview_management(self):
        """Test interview management endpoints"""
        print("\n🎯 Testing Interview Management...")
        interview_success = True
        
        # Use authenticated user with job
        test_email = list(self.jobs.keys())[0] if self.jobs else None
        if not test_email:
            print("  ❌ No jobs available for interview testing")
            self.test_results["interview_management"] = False
            return False
        
        headers = self.get_auth_headers(test_email)
        job_id = self.jobs[test_email]
        
        # First get applications for the job to test interview endpoints
        print(f"  Getting applications for job {job_id}...")
        result = await self.make_request("GET", f"/applications/job/{job_id}", headers=headers)
        
        if result["success"] and result["data"]:
            app_id = result["data"][0]["id"]
            
            # Test get interviews for application
            print(f"  Testing GET /interviews/application/{app_id}...")
            result = await self.make_request("GET", f"/interviews/application/{app_id}", headers=headers)
            if result["success"]:
                print(f"  ✅ GET /interviews/application/{app_id} successful - found {len(result['data'])} interviews")
                
                # If interviews exist, test updating one
                if result["data"]:
                    interview_id = result["data"][0]["id"]
                    print(f"  Testing PATCH /interviews/{interview_id}...")
                    update_data = {
                        "status": "completed",
                        "feedback": {
                            "recommendation": "hire",
                            "technical_score": 8,
                            "communication_score": 9,
                            "notes": "Strong candidate"
                        }
                    }
                    result = await self.make_request("PATCH", f"/interviews/{interview_id}", update_data, headers=headers)
                    if result["success"]:
                        print("  ✅ PATCH /interviews/{id} successful")
                    else:
                        print(f"  ❌ PATCH /interviews/{interview_id} failed: {result['data']}")
                        interview_success = False
            else:
                print(f"  ❌ GET /interviews/application/{app_id} failed: {result['data']}")
                interview_success = False
            
            # Test schedule interview
            print("  Testing POST /interviews...")
            from datetime import datetime, timedelta
            future_time = datetime.now() + timedelta(days=7)
            
            interview_data = {
                "application_id": app_id,
                "interviewer_id": "interviewer-123",
                "interview_type": "technical",
                "scheduled_at": future_time.isoformat(),
                "duration_minutes": 60,
                "meeting_link": "https://meet.google.com/abc-def-ghi",
                "notes": "Technical interview for Python developer position"
            }
            
            result = await self.make_request("POST", "/interviews", interview_data, headers=headers)
            if result["success"]:
                print("  ✅ POST /interviews successful")
            else:
                print(f"  ❌ POST /interviews failed: {result['data']}")
                interview_success = False
        else:
            print("  ⚠️ No applications found to test interview endpoints")
        
        self.test_results["interview_management"] = interview_success
        return interview_success
    
    async def test_analytics(self):
        """Test analytics endpoints"""
        print("\n📊 Testing Analytics...")
        analytics_success = True
        
        # Use authenticated user
        test_email = list(self.tokens.keys())[0] if self.tokens else None
        if not test_email:
            print("  ❌ No authenticated users available")
            self.test_results["analytics"] = False
            return False
        
        headers = self.get_auth_headers(test_email)
        
        # Test dashboard analytics
        print("  Testing GET /analytics/dashboard...")
        result = await self.make_request("GET", "/analytics/dashboard", headers=headers)
        if result["success"]:
            print("  ✅ GET /analytics/dashboard successful")
        else:
            print(f"  ❌ GET /analytics/dashboard failed: {result['data']}")
            analytics_success = False
        
        # Test job analytics if we have a job
        if self.jobs:
            job_id = list(self.jobs.values())[0]
            print(f"  Testing GET /analytics/jobs/{job_id}...")
            result = await self.make_request("GET", f"/analytics/jobs/{job_id}", headers=headers)
            if result["success"]:
                print("  ✅ GET /analytics/jobs/{id} successful")
            else:
                print(f"  ❌ GET /analytics/jobs/{job_id} failed: {result['data']}")
                analytics_success = False
        
        self.test_results["analytics"] = analytics_success
        return analytics_success
    
    async def test_oauth_endpoints(self):
        """Test OAuth endpoints (informational)"""
        print("\n🔗 Testing OAuth Endpoints...")
        oauth_success = True
        
        # Test Google OAuth URL
        print("  Testing GET /oauth/google/url...")
        result = await self.make_request("GET", "/oauth/google/url")
        if result["success"]:
            print("  ✅ GET /oauth/google/url successful")
        else:
            print(f"  ⚠️ GET /oauth/google/url failed (expected): {result['data']}")
            # OAuth endpoints may not work without proper redirect URI setup
        
        # Test Microsoft OAuth URL
        print("  Testing GET /oauth/microsoft/url...")
        result = await self.make_request("GET", "/oauth/microsoft/url")
        if result["success"]:
            print("  ✅ GET /oauth/microsoft/url successful")
        else:
            print(f"  ⚠️ GET /oauth/microsoft/url failed (expected): {result['data']}")
        
        self.test_results["oauth_endpoints"] = oauth_success
        return oauth_success
    
    async def test_email_config(self):
        """Test email configuration endpoints"""
        print("\n📧 Testing Email Configuration...")
        email_success = True
        
        # Use authenticated user
        test_email = list(self.tokens.keys())[0] if self.tokens else None
        if not test_email:
            print("  ❌ No authenticated users available")
            self.test_results["email_config"] = False
            return False
        
        headers = self.get_auth_headers(test_email)
        
        # Test get email config
        print("  Testing GET /email-config...")
        result = await self.make_request("GET", "/email-config", headers=headers)
        if result["success"]:
            print("  ✅ GET /email-config successful")
        else:
            print(f"  ❌ GET /email-config failed: {result['data']}")
            email_success = False
        
        self.test_results["email_config"] = email_success
        return email_success
    
    async def run_all_tests(self):
        """Run all backend tests"""
        print("🚀 Starting HireFlow AI Backend API Tests")
        print(f"Backend URL: {BACKEND_URL}")
        print("=" * 60)
        
        # Run tests in order
        await self.test_health_check()
        await self.test_authentication()
        await self.test_company_management()
        await self.test_job_management()
        await self.test_application_management()
        await self.test_candidate_management()
        await self.test_interview_management()
        await self.test_analytics()
        await self.test_oauth_endpoints()
        await self.test_email_config()
        
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