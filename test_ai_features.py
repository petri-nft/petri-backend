#!/usr/bin/env python3
"""
Test script for AI Personality System

Run after starting the backend server:
    python test_ai_features.py

Prerequisites:
- Backend running on http://localhost:8000
- User 'alice' exists with password 'password123'
- Tree with ID 1 exists
"""

import requests
import json
import time
from typing import Dict, Any, Optional

# Configuration
API_BASE_URL = "http://localhost:8000/api"
TEST_USERNAME = "alice"
TEST_PASSWORD = "password123"
TEST_TREE_ID = 1

# Colors for terminal output
class Colors:
    GREEN = '\033[92m'
    BLUE = '\033[94m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    END = '\033[0m'

def print_section(title: str) -> None:
    """Print a section header."""
    print(f"\n{Colors.BLUE}{'='*60}")
    print(f"{title}")
    print(f"{'='*60}{Colors.END}\n")

def print_success(msg: str) -> None:
    """Print success message."""
    print(f"{Colors.GREEN}✓ {msg}{Colors.END}")

def print_error(msg: str) -> None:
    """Print error message."""
    print(f"{Colors.RED}✗ {msg}{Colors.END}")

def print_info(msg: str) -> None:
    """Print info message."""
    print(f"{Colors.YELLOW}ℹ {msg}{Colors.END}")

class AIFeaturesTester:
    def __init__(self, base_url: str, username: str, password: str, tree_id: int):
        self.base_url = base_url
        self.username = username
        self.password = password
        self.tree_id = tree_id
        self.token: Optional[str] = None
        self.headers: Dict[str, str] = {}

    def login(self) -> bool:
        """Login and get JWT token."""
        print_section("STEP 1: Login")
        
        try:
            response = requests.post(
                f"{self.base_url}/auth/login",
                json={"username": self.username, "password": self.password},
                timeout=5
            )
            
            if response.status_code == 200:
                data = response.json()
                self.token = data.get("access_token")
                self.headers = {"Authorization": f"Bearer {self.token}"}
                print_success(f"Logged in as {self.username}")
                print_info(f"Token: {self.token[:20]}...")
                return True
            else:
                print_error(f"Login failed: {response.status_code}")
                print_info(f"Response: {response.text}")
                return False
                
        except Exception as e:
            print_error(f"Login error: {str(e)}")
            return False

    def set_personality(self) -> bool:
        """Set tree personality."""
        print_section("STEP 2: Set Tree Personality")
        
        personality_data = {
            "name": "Wise Oak",
            "tone": "humorous",
            "background": "An ancient oak tree who loves making tree puns and jokes. I've been around for centuries and have a witty observation about everything!",
            "traits": {
                "loves_puns": True,
                "favorite_joke_type": "tree_jokes",
                "age_years": 342,
                "speaks_in_metaphors": True
            }
        }
        
        try:
            print_info(f"Setting personality for tree {self.tree_id}...")
            response = requests.post(
                f"{self.base_url}/trees/{self.tree_id}/personality",
                json=personality_data,
                headers=self.headers,
                timeout=10
            )
            
            if response.status_code in [200, 201]:
                data = response.json()
                print_success(f"Personality set successfully!")
                print_info(f"Personality ID: {data.get('personality_id')}")
                print_info(f"Voice ID: {data.get('voice_id')}")
                print_info(f"Available voices: {data.get('available_voices')}")
                return True
            else:
                print_error(f"Failed to set personality: {response.status_code}")
                print_info(f"Response: {response.text}")
                return False
                
        except Exception as e:
            print_error(f"Personality setup error: {str(e)}")
            return False

    def get_personality(self) -> bool:
        """Get tree personality."""
        print_section("STEP 3: Get Tree Personality")
        
        try:
            print_info(f"Fetching personality for tree {self.tree_id}...")
            response = requests.get(
                f"{self.base_url}/trees/{self.tree_id}/personality",
                headers=self.headers,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                print_success("Personality retrieved!")
                print(f"  Name: {data.get('name')}")
                print(f"  Tone: {data.get('tone')}")
                print(f"  Background: {data.get('background')[:100]}...")
                print(f"  Traits: {json.dumps(data.get('traits'), indent=4)}")
                return True
            else:
                print_error(f"Failed to get personality: {response.status_code}")
                return False
                
        except Exception as e:
            print_error(f"Error fetching personality: {str(e)}")
            return False

    def chat_with_tree(self, message: str, include_audio: bool = False) -> bool:
        """Chat with tree."""
        print_section(f"STEP 4: Chat with Tree")
        print_info(f"User message: '{message}'")
        
        try:
            response = requests.post(
                f"{self.base_url}/trees/{self.tree_id}/chat",
                json={"content": message, "include_audio": include_audio},
                headers=self.headers,
                timeout=30  # Generous timeout for AI response
            )
            
            if response.status_code == 200:
                data = response.json()
                print_success("Chat interaction successful!")
                print(f"\n  Tree name: {data.get('tree_name')}")
                print(f"  Your message: {data.get('user_message')}")
                print(f"\n  Tree response:")
                print(f"  '{data.get('tree_response')}'")
                
                if data.get('audio_url'):
                    print_info(f"Audio available: {data.get('audio_url')[:50]}...")
                
                return True
            else:
                print_error(f"Chat failed: {response.status_code}")
                print_info(f"Response: {response.text}")
                return False
                
        except requests.exceptions.Timeout:
            print_error("Chat request timed out (AI might be slow)")
            return False
        except Exception as e:
            print_error(f"Chat error: {str(e)}")
            return False

    def get_chat_history(self) -> bool:
        """Get chat history."""
        print_section("STEP 5: Get Chat History")
        
        try:
            response = requests.get(
                f"{self.base_url}/trees/{self.tree_id}/chat-history?limit=10",
                headers=self.headers,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                messages = data.get('messages', [])
                print_success(f"Retrieved {len(messages)} messages!")
                
                for i, msg in enumerate(messages, 1):
                    role = "🧑 You" if msg.get('role') == 'user' else "🌳 Tree"
                    print(f"\n  [{i}] {role}:")
                    print(f"      {msg.get('content')[:80]}...")
                    if msg.get('audio_url'):
                        print(f"      🎤 Audio: Yes")
                
                return True
            else:
                print_error(f"Failed to get history: {response.status_code}")
                return False
                
        except Exception as e:
            print_error(f"Error fetching history: {str(e)}")
            return False

    def list_public_trees(self) -> bool:
        """List public trees."""
        print_section("STEP 6: List Public Trees")
        
        try:
            response = requests.get(
                f"{self.base_url}/trees/marketplace/trees?limit=5",
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                trees = data.get('trees', [])
                print_success(f"Found {data.get('count')} public trees!")
                
                for tree in trees[:5]:
                    print(f"\n  - {tree.get('species')} (ID: {tree.get('id')})")
                    if tree.get('personality'):
                        print(f"    Name: {tree.get('personality', {}).get('name')}")
                        print(f"    Tone: {tree.get('personality', {}).get('tone')}")
                    print(f"    Owner: {tree.get('owner')}")
                    print(f"    Health: {tree.get('health_score')}%")
                
                return True
            else:
                print_error(f"Failed to list trees: {response.status_code}")
                return False
                
        except Exception as e:
            print_error(f"Error listing trees: {str(e)}")
            return False

    def get_available_voices(self) -> bool:
        """Get available ElevenLabs voices."""
        print_section("STEP 7: Get Available Voices")
        
        try:
            response = requests.get(
                f"{self.base_url}/trees/voices",
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                voices = data.get('voices', [])
                print_success(f"Found {len(voices)} available voices!")
                
                for voice in voices:
                    print(f"\n  🎤 {voice.get('name')}")
                    print(f"     ID: {voice.get('voice_id')}")
                    print(f"     Description: {voice.get('description')}")
                
                return True
            else:
                print_error(f"Failed to get voices: {response.status_code}")
                return False
                
        except Exception as e:
            print_error(f"Error fetching voices: {str(e)}")
            return False

    def run_all_tests(self) -> None:
        """Run all tests."""
        print(f"\n{Colors.BLUE}{'='*60}")
        print("🌳 AI PERSONALITY SYSTEM - TEST SUITE")
        print(f"{'='*60}{Colors.END}")
        print(f"Server: {self.base_url}")
        print(f"User: {self.username}")
        print(f"Tree ID: {self.tree_id}\n")
        
        tests = [
            ("Login", self.login),
            ("Set Personality", self.set_personality),
            ("Get Personality", self.get_personality),
            ("Chat with Tree", lambda: self.chat_with_tree("Hello! How are you today?")),
            ("Chat with Audio", lambda: self.chat_with_tree("Tell me a tree joke!", include_audio=False)),  # Set to False to avoid audio generation in test
            ("Get Chat History", self.get_chat_history),
            ("Get Available Voices", self.get_available_voices),
            ("List Public Trees", self.list_public_trees),
        ]
        
        results = []
        for test_name, test_func in tests:
            try:
                result = test_func()
                results.append((test_name, result))
                time.sleep(1)  # Rate limiting
            except Exception as e:
                print_error(f"Test '{test_name}' crashed: {str(e)}")
                results.append((test_name, False))
        
        # Summary
        print_section("TEST SUMMARY")
        passed = sum(1 for _, result in results if result)
        total = len(results)
        
        for test_name, result in results:
            status = f"{Colors.GREEN}PASS{Colors.END}" if result else f"{Colors.RED}FAIL{Colors.END}"
            print(f"  {status} - {test_name}")
        
        print(f"\nTotal: {passed}/{total} passed")
        
        if passed == total:
            print(f"{Colors.GREEN}✓ All tests passed!{Colors.END}\n")
        else:
            print(f"{Colors.YELLOW}⚠ Some tests failed. Check errors above.{Colors.END}\n")


def main():
    """Main entry point."""
    tester = AIFeaturesTester(
        base_url=API_BASE_URL,
        username=TEST_USERNAME,
        password=TEST_PASSWORD,
        tree_id=TEST_TREE_ID
    )
    
    try:
        tester.run_all_tests()
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}Tests interrupted by user{Colors.END}")
    except Exception as e:
        print_error(f"Test suite error: {str(e)}")


if __name__ == "__main__":
    main()
