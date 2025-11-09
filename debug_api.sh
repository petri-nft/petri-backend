#!/usr/bin/env bash
# Quick debug script to see what frontend is getting

echo "=== BACKEND API RESPONSE ==="
TOKEN=$(curl -s -X POST http://localhost:8000/api/auth/login \
  -H 'Content-Type: application/json' \
  -d '{"username":"alice","password":"password123"}' | jq -r '.access_token')

echo "Token: $TOKEN"
echo ""

echo "=== TREES RESPONSE ==="
TREES=$(curl -s -H "Authorization: Bearer $TOKEN" http://localhost:8000/api/trees)
echo "$TREES" | jq '.'
echo ""

echo "=== TREE COUNT ==="
echo "$TREES" | jq 'length'
echo ""

echo "=== FIRST TREE DETAILS ==="
echo "$TREES" | jq '.[0] | {id, user_id, species}'
echo ""

echo "=== ALICE'S USER ID ==="
curl -s -X POST http://localhost:8000/api/auth/login \
  -H 'Content-Type: application/json' \
  -d '{"username":"alice","password":"password123"}' | jq '.user_id'
