#!/usr/bin/env python3
"""
Test script for authentication system
Run this to test user registration and login
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def test_health():
    """Test health endpoint"""
    try:
        response = requests.get(f"{BASE_URL}/health")
        print(f"✅ Health check: {response.status_code}")
        print(f"   Response: {response.json()}")
        return True
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return False

def test_register():
    """Test user registration"""
    try:
        user_data = {
            "email": "test@example.com",
            "username": "testuser",
            "password": "testpassword123"
        }
        
        response = requests.post(
            f"{BASE_URL}/auth/register",
            json=user_data
        )
        
        print(f"✅ Registration: {response.status_code}")
        if response.status_code == 201:
            user = response.json()
            print(f"   User created: {user['username']} ({user['email']})")
            return user
        else:
            print(f"   Error: {response.json()}")
            return None
            
    except Exception as e:
        print(f"❌ Registration failed: {e}")
        return None

def test_login():
    """Test user login"""
    try:
        login_data = {
            "email": "test@example.com",
            "password": "testpassword123"
        }
        
        response = requests.post(
            f"{BASE_URL}/auth/login",
            json=login_data
        )
        
        print(f"✅ Login: {response.status_code}")
        if response.status_code == 200:
            token_data = response.json()
            print(f"   Token received: {token_data['token_type']} {token_data['access_token'][:20]}...")
            return token_data['access_token']
        else:
            print(f"   Error: {response.json()}")
            return None
            
    except Exception as e:
        print(f"❌ Login failed: {e}")
        return None

def test_me_endpoint(token):
    """Test /me endpoint with token"""
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f"{BASE_URL}/auth/me", headers=headers)
        
        print(f"✅ /me endpoint: {response.status_code}")
        if response.status_code == 200:
            user = response.json()
            print(f"   User info: {user['username']} ({user['email']})")
            return True
        else:
            print(f"   Error: {response.json()}")
            return False
            
    except Exception as e:
        print(f"❌ /me endpoint failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 Testing Authentication System")
    print("=" * 40)
    
    # Test health
    if not test_health():
        print("❌ Health check failed, stopping tests")
        return
    
    print()
    
    # Test registration
    user = test_register()
    if not user:
        print("❌ Registration failed, stopping tests")
        return
    
    print()
    
    # Test login
    token = test_login()
    if not token:
        print("❌ Login failed, stopping tests")
        return
    
    print()
    
    # Test protected endpoint
    success = test_me_endpoint(token)
    if success:
        print("✅ All tests passed!")
    else:
        print("❌ Some tests failed")

if __name__ == "__main__":
    main()