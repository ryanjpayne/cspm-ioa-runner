#!/bin/bash
set -e

# Source the utils file for standardized tags
# shellcheck source=./utils.sh
source "$(dirname "$0")/utils.sh"

: '
Policy 318 - Certificate added to an application registration

Pattern: Creates an App Registration and adds a certificate to it, then cleans up.

'

APP_NAME="CSPM-IOA-318-TestApp-$(date +%s)"
CERT_FILE="/tmp/ioa318cert.pem"

echo "Running Azure IOA 318"
echo "Running Azure IOA 318 - Prep"

echo "Creating App Registration: $APP_NAME"
APP_ID=$(az ad app create --display-name "$APP_NAME" --tags $AZURE_RESOURCE_TAGS --query appId -o tsv)

echo "App Registration created with App ID: $APP_ID"

echo "Generating self-signed certificate"
openssl req -x509 -newkey rsa:2048 -keyout /tmp/ioa318key.pem -out "$CERT_FILE" -days 1 -nodes -subj "/CN=IOA318Test"

echo "Running Azure IOA 318 - Pattern"
echo "Adding certificate to App Registration"

az ad app credential reset --id "$APP_ID" --cert "@$CERT_FILE" --append

echo "Certificate added successfully"

echo "Running Azure IOA 318 - Cleanup"
echo "Removing temporary certificate files"
rm -f "$CERT_FILE" /tmp/ioa318key.pem

echo "Deleting App Registration: $APP_NAME"
az ad app delete --id "$APP_ID"

echo "Cleanup complete"
