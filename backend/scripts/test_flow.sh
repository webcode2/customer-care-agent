#!/bin/bash

# Configuration
IAM_URL="http://localhost:8001/api/v1"
AGENT_URL="http://localhost:8000/api/v1"

echo "--- 1. Registering User First ---"
# Register without an organization
curl -s -X POST $IAM_URL/register \
     -H "Content-Type: application/json" \
     -d '{"email": "boss@newcorp.com", "password": "securepassword"}'

echo -e "\n--- 2. Logging In ---"
LOGIN_RESPONSE=$(curl -s -X POST $IAM_URL/login \
     -H "Content-Type: application/json" \
     -d '{"email": "boss@newcorp.com", "password": "securepassword"}')
TOKEN=$(echo $LOGIN_RESPONSE | grep -o '"access_token":"[^"]*' | cut -d\" -f4)

if [ -z "$TOKEN" ]; then
    echo "Failed to get token"
    exit 1
fi
echo "Login Successful. Token obtained."

echo -e "\n--- 3. Creating Organization as Authenticated User ---"
ORG_RESPONSE=$(curl -s -X POST $IAM_URL/organizations \
     -H "Authorization: Bearer $TOKEN" \
     -H "Content-Type: application/json" \
     -d '{"name": "New Corp", "slug": "new-corp", "config": {"voice": "elegant"}}')
ORG_ID=$(echo $ORG_RESPONSE | grep -o '"id":[0-9]*' | cut -d: -f2)
echo "Org Created ID: $ORG_ID (User is now linked to this Org)"

echo -e "\n--- 4. Syncing Documents (with Chunking) ---"
# Note: Since the user is now linked to ORG_ID, we use the same TOKEN
curl -s -X POST $AGENT_URL/sync \
     -H "Authorization: Bearer $TOKEN"
echo "Sync triggered and chunked."

echo -e "\n--- 5. Chatting with Agent ---"
curl -X POST $AGENT_URL/chat \
     -H "Authorization: Bearer $TOKEN" \
     -H "Content-Type: application/json" \
     -d '{"query": "Welcome to New Corp, what can you do?"}'

echo -e "\n\nTesting complete."
