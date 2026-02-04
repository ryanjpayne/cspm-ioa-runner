#!/bin/bash
set -e

# Source the utils file for standardized tags
# shellcheck source=./utils.sh
source "$(dirname "$0")/utils.sh"

: '
Policy 303 - User MFA disabled

Pattern: Creates a test user, enables MFA, then disables it, then cleans up.

Note: This requires appropriate permissions to manage users and MFA settings.
The script uses Microsoft Graph API to manage MFA settings.

'

USER_PRINCIPAL_NAME="cspm303testuser$(date +%s)@$(az account show --query 'tenantDisplayName' -o tsv | tr -d ' ').onmicrosoft.com"
DISPLAY_NAME="CSPM IOA 303 Test User"
PASSWORD="CSPMTest@$(date +%s)!"

echo "Running Azure IOA 303"
echo "Running Azure IOA 303 - Prep"

echo "Creating test user: $USER_PRINCIPAL_NAME"
USER_ID=$(az ad user create \
  --display-name "$DISPLAY_NAME" \
  --user-principal-name "$USER_PRINCIPAL_NAME" \
  --password "$PASSWORD" \
  --force-change-password-next-sign-in false \
  --query id -o tsv)

# Note: Azure AD users don't support tags directly

echo "Test user created with ID: $USER_ID"

echo "Enabling MFA for user"
# Enable MFA using Microsoft Graph API
az rest --method POST \
  --uri "https://graph.microsoft.com/v1.0/users/$USER_ID/authentication/methods" \
  --body '{"@odata.type":"#microsoft.graph.phoneAuthenticationMethod","phoneNumber":"+1 5551234567","phoneType":"mobile"}' \
  --headers "Content-Type=application/json" || echo "MFA setup attempted (may require additional permissions)"

echo "Running Azure IOA 303 - Pattern"
echo "Disabling MFA for user"

# Disable MFA by removing authentication methods
az rest --method GET \
  --uri "https://graph.microsoft.com/v1.0/users/$USER_ID/authentication/methods" \
  --query 'value[].id' -o tsv | while read METHOD_ID; do
    az rest --method DELETE \
      --uri "https://graph.microsoft.com/v1.0/users/$USER_ID/authentication/methods/$METHOD_ID" || echo "Method removal attempted"
done

echo "MFA disabled for user"

echo "Running Azure IOA 303 - Cleanup"
echo "Deleting test user: $USER_PRINCIPAL_NAME"

az ad user delete --id "$USER_ID"

echo "Cleanup complete"
