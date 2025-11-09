#!/bin/bash

# Login
echo "🔑 Logging in..."
LOGIN_RESPONSE=$(curl -s -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "alice", "password": "password123"}')

TOKEN=$(echo $LOGIN_RESPONSE | python3 -c "import sys, json; print(json.load(sys.stdin)['access_token'])")
echo "✅ Token: ${TOKEN:0:20}..."

# Plant a tree
echo "🌱 Planting tree..."
PLANT_RESPONSE=$(curl -s -X POST http://localhost:8000/api/trees \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "species": "oak",
    "latitude": 40.7128,
    "longitude": -74.0060,
    "location_name": "New York",
    "description": "A test oak tree"
  }')

echo "Response:"
echo $PLANT_RESPONSE | python3 -m json.tool

