#!/bin/bash
set -e

# Source the utils file for standardized tags
# shellcheck source=./utils.sh
source "$(dirname "$0")/utils.sh"

: '
Policy 317 - Secret added to an application registration

Pattern: Creates an App Registration and adds a client secret to it, then cleans up.

'

APP_NAME="CSPM-IOA-317-TestApp-$(date +%s)"

echo "Running Azure IOA 317"
echo "Running Azure IOA 317 - Prep"

echo "Creating App Registration: $APP_NAME"
APP_ID=$(az ad app create --display-name "$APP_NAME" --tags $AZURE_RESOURCE_TAGS --query appId -o tsv)

echo "App Registration created with App ID: $APP_ID"

echo "Running Azure IOA 317 - Pattern"
echo "Adding client secret to App Registration"

az ad app credential reset --id "$APP_ID" --append --query password -o tsv > /dev/null

echo "Client secret added successfully"

echo "Running Azure IOA 317 - Cleanup"
echo "Deleting App Registration: $APP_NAME"

az ad app delete --id "$APP_ID"

echo "Cleanup complete"
