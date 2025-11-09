#!/usr/bin/env python3
"""
Chat/Orchestrator API Testing - Focused Test
"""

import asyncio
import aiohttp
import json
import sys

# Backend URL from frontend/.env
BACKEND_URL = "https://component-review-3.preview.emergentagent.com/api"

# Test credentials
TEST_EMAIL = "admin@techcorp.com"
TEST_PASSWORD = "password123"

class ChatAPITester:
    def __init__(self):
        self.session = None
        self.token = None
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def login(self):
        """Login and get token"""
        print("🔐 Logging in...")
        
        form_data = aiohttp.FormData()
        form_data.add_field('username', TEST_EMAIL)
        form_data.add_field('password', TEST_PASSWORD)
        
        url = f"{BACKEND_URL}/auth/login"
        async with self.session.post(url, data=form_data) as response:
            if response.status == 200:
                token_data = await response.json()
                self.token = token_data['access_token']
                print("✅ Login successful")
                return True
            else:
                error_data = await response.text()
                print(f"❌ Login failed: {error_data}")
                return False
    
    def get_auth_headers(self):
        """Get authorization headers"""
        return {"Authorization": f"Bearer {self.token}"}
    
    async def test_chat_endpoints(self):
        """Test all chat endpoints"""
        print("\n🤖 Testing Chat/Orchestrator API...")
        
        headers = self.get_auth_headers()
        session_id = None
        
        # Test 1: Send initial chat message
        print("  1. Testing POST /chat/ - Initial message...")
        chat_data = {"message": "Hello, what can you help me with?"}
        
        url = f"{BACKEND_URL}/chat/"
        async with self.session.post(url, json=chat_data, headers=headers) as response:
            if response.status == 200:
                data = await response.json()
                session_id = data.get("session_id")
                print(f"  ✅ POST /chat/ successful")
                print(f"    📝 Response: {data.get('response', '')[:100]}...")
                print(f"    🆔 Session ID: {session_id}")
                print(f"    ⚡ Action taken: {data.get('action_taken')}")
            else:
                error_data = await response.text()
                print(f"  ❌ POST /chat/ failed: {error_data}")
                return False
        
        # Test 2: Send follow-up message
        if session_id:
            print("  2. Testing POST /chat/ - Follow-up message...")
            followup_data = {
                "message": "Can you help me create a new job posting?",
                "session_id": session_id
            }
            
            async with self.session.post(url, json=followup_data, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"  ✅ POST /chat/ with session_id successful")
                    print(f"    📝 Response: {data.get('response', '')[:100]}...")
                else:
                    error_data = await response.text()
                    print(f"  ❌ POST /chat/ with session_id failed: {error_data}")
                    return False
        
        # Test 3: Get chat sessions
        print("  3. Testing GET /chat/sessions...")
        url = f"{BACKEND_URL}/chat/sessions"
        async with self.session.get(url, headers=headers) as response:
            if response.status == 200:
                sessions = await response.json()
                print(f"  ✅ GET /chat/sessions successful - found {len(sessions)} sessions")
                if sessions:
                    session = sessions[0]
                    print(f"    📋 Session structure: {list(session.keys())}")
            else:
                error_data = await response.text()
                print(f"  ❌ GET /chat/sessions failed: {error_data}")
                return False
        
        # Test 4: Get chat history
        if session_id:
            print(f"  4. Testing GET /chat/history/{session_id}...")
            url = f"{BACKEND_URL}/chat/history/{session_id}"
            async with self.session.get(url, headers=headers) as response:
                if response.status == 200:
                    history = await response.json()
                    print(f"  ✅ GET /chat/history/{session_id} successful - found {len(history)} messages")
                    if history:
                        message = history[0]
                        print(f"    📋 Message structure: {list(message.keys())}")
                        roles = [msg.get("role") for msg in history]
                        print(f"    💬 Roles in conversation: {roles}")
                else:
                    error_data = await response.text()
                    print(f"  ❌ GET /chat/history/{session_id} failed: {error_data}")
                    return False
        
        # Test 5: Delete chat session
        if session_id:
            print(f"  5. Testing DELETE /chat/sessions/{session_id}...")
            url = f"{BACKEND_URL}/chat/sessions/{session_id}"
            async with self.session.delete(url, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"  ✅ DELETE /chat/sessions/{session_id} successful")
                    print(f"    📝 Response: {data.get('message')}")
                    
                    # Verify session is deleted
                    print("  6. Verifying session deletion...")
                    url = f"{BACKEND_URL}/chat/sessions"
                    async with self.session.get(url, headers=headers) as response:
                        if response.status == 200:
                            sessions = await response.json()
                            session_ids = [s.get("session_id") for s in sessions]
                            if session_id not in session_ids:
                                print("  ✅ Session successfully deleted")
                            else:
                                print("  ⚠️ Session still exists after deletion")
                                return False
                else:
                    error_data = await response.text()
                    print(f"  ❌ DELETE /chat/sessions/{session_id} failed: {error_data}")
                    return False
        
        return True
    
    async def run_test(self):
        """Run the complete chat API test"""
        print("🚀 Starting Chat/Orchestrator API Test")
        print(f"Backend URL: {BACKEND_URL}")
        print("=" * 60)
        
        # Login first
        if not await self.login():
            return False
        
        # Test chat endpoints
        success = await self.test_chat_endpoints()
        
        print("\n" + "=" * 60)
        if success:
            print("🎉 All Chat/Orchestrator API tests passed!")
        else:
            print("❌ Some Chat/Orchestrator API tests failed")
        
        return success

async def main():
    """Main test runner"""
    async with ChatAPITester() as tester:
        success = await tester.run_test()
        return 0 if success else 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)