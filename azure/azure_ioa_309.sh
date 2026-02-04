#!/bin/bash
set -e

# Source the utils file for standardized tags
# shellcheck source=./utils.sh
source "$(dirname "$0")/utils.sh"

: '
Policy 309 - Storage Account Networking changed to All Networks

Pattern: Creates a Storage Account and modifies network rules to allow all networks, then cleans up.

'

RESOURCE_GROUP="CSPM-TESTING-309"
STORAGE_ACCOUNT="cspm309sa$(date +%s)"

echo "Running Azure IOA 309"
echo "Running Azure IOA 309 - Prep"

echo "Creating Resource Group: $RESOURCE_GROUP"
az group create -l westus -n "$RESOURCE_GROUP" --tags $AZURE_RESOURCE_TAGS

echo "Creating Storage Account: $STORAGE_ACCOUNT"
az storage account create \
  --name "$STORAGE_ACCOUNT" \
  --resource-group "$RESOURCE_GROUP" \
  --location westus \
  --sku Standard_LRS \
  --default-action Deny \
  --tags $AZURE_RESOURCE_TAGS

echo "Storage Account created"

echo "Running Azure IOA 309 - Pattern"
echo "Changing network rules to allow all networks"

az storage account update \
  --name "$STORAGE_ACCOUNT" \
  --resource-group "$RESOURCE_GROUP" \
  --default-action Allow

echo "Network rules updated to allow all networks"

echo "Running Azure IOA 309 - Cleanup"
echo "Deleting Resource Group: $RESOURCE_GROUP"

az group delete --yes -n "$RESOURCE_GROUP"

echo "Cleanup complete"
