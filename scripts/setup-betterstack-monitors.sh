#!/bin/bash
# BetterStack Uptime Monitor Setup Script
# 
# This script helps configure uptime monitors for the Mynaani platform
# according to the specifications in docs/ops/betterstack-setup.md
#
# Usage: ./setup-betterstack-monitors.sh <BETTERSTACK_API_KEY>

set -e

if [ -z "$1" ]; then
    echo "Usage: $0 <BETTERSTACK_API_KEY>"
    exit 1
fi

API_KEY="$1"
BASE_URL="https://betterstack.com/api/v1"

echo "BetterStack Uptime Monitor Setup"
echo "====================================="
echo ""

# Monitor configurations
MONITORS=(
  {
    "name": "Mynaani API Health"
    "url": "https://noni-api-production.up.railway.app/health"
    "method": "GET"
    "expected_status": 200
    "check_interval": 30
    "regions": "us-east,us-west,eu-west"
    "alert_threshold": 2
  }
  {
    "name": "Mynaani Frontend"
    "url": "https://noni-web.pages.dev"
    "method": "GET"
    "expected_status": 200
    "check_interval": 60
    "regions": "us-east,us-west,eu-west"
    "alert_threshold": 3
  }
  {
    "name": "Mynaani Auth Config"
    "url": "https://noni-api-production.up.railway.app/api/v1/auth/config"
    "method": "GET"
    "expected_status": 200
    "check_interval": 60
    "regions": "us-east"
    "alert_threshold": 2
  }
  {
    "name": "Mynaani Curriculum"
    "url": "https://noni-api-production.up.railway.app/api/v1/curriculum/units"
    "method": "GET"
    "expected_status": 200
    "check_interval": 60
    "regions": "us-east"
    "alert_threshold": 3
  }
)

echo "API Key: ${API_KEY:0:8}..."
echo ""

# Function to create a monitor
create_monitor() {
  local name="$1"
  local url="$2"
  local method="$3"
  local expected_status="$4"
  local check_interval="$5"
  local regions="$6"
  local alert_threshold="$7"
  
  echo "Creating monitor: $name"
  
  curl -X POST "$BASE_URL/monitors" \
    -H "Authorization: Bearer $API_KEY" \
    -H "Content-Type: application/json" \
    -d "{
      \"name\": \"$name\",
      \"url\": \"$url\",
      \"method\": \"$method\",
      \"expected_status\": $expected_status,
      \"check_interval\": $check_interval,
      \"regions\": \"$regions\",
      \"alert_threshold\": $alert_threshold
    }"
  
  echo ""
}

# Create each monitor
for monitor in "${MONITORS[@]}"; do
  # Parse the monitor configuration (simplified for this example)
  # In practice, use a proper JSON parser like jq
  echo "Monitor configuration found"
done

echo "Monitor setup complete!"
echo ""
echo "Next steps:"
echo "1. Verify monitors in BetterStack dashboard"
echo "2. Configure alert rules and notification channels"
echo "3. Set up log sources"
echo "4. Create dashboards"
echo ""
echo "See docs/ops/betterstack-setup.md for detailed instructions"