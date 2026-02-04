#!/bin/bash
set -e

# Source the utils file for standardized tags
# shellcheck source=./utils.sh
source "$(dirname "$0")/utils.sh"

: '
Policy 395 - Conditional Access policy deleted

Pattern: Creates a test Conditional Access policy, then deletes it.

Note: This requires appropriate permissions to manage Conditional Access policies.
Requires Azure AD Premium P1 or P2 license.

'

POLICY_NAME="CSPM-IOA-395-TestPolicy-$(date +%s)"

echo "Running Azure IOA 395"
echo "Running Azure IOA 395 - Prep"

echo "Creating Conditional Access policy: $POLICY_NAME"

# Create a basic Conditional Access policy using Microsoft Graph API
POLICY_JSON=$(cat <<EOF
{
  "displayName": "$POLICY_NAME",
  "state": "disabled",
  "conditions": {
    "users": {
      "includeUsers": ["None"]
    },
    "applications": {
      "includeApplications": ["None"]
    }
  },
  "grantControls": {
    "operator": "OR",
    "builtInControls": ["block"]
  }
}
EOF
)

POLICY_ID=$(az rest --method POST \
  --uri "https://graph.microsoft.com/v1.0/identity/conditionalAccess/policies" \
  --body "$POLICY_JSON" \
  --headers "Content-Type=application/json" \
  --query id -o tsv)

# Note: Conditional Access policies don't support tags directly

echo "Conditional Access policy created with ID: $POLICY_ID"

echo "Running Azure IOA 395 - Pattern"
echo "Deleting Conditional Access policy: $POLICY_NAME"

az rest --method DELETE \
  --uri "https://graph.microsoft.com/v1.0/identity/conditionalAccess/policies/$POLICY_ID"

echo "Conditional Access policy deleted"

echo "Running Azure IOA 395 - Cleanup"
echo "Cleanup complete (policy already deleted)"
