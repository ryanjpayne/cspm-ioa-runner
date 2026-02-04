#!/bin/bash
set -e

# Source the utils file for standardized tags
# shellcheck source=./utils.sh
source "$(dirname "$0")/utils.sh"

: '
Policy 518 - Virtual Machine disk exported by user

Pattern: Creates a managed disk, grants access to generate SAS URL (export), then cleans up.

'

RESOURCE_GROUP="CSPM-TESTING-518"
DISK_NAME="cspm518disk"

echo "Running Azure IOA 518"
echo "Running Azure IOA 518 - Prep"

echo "Creating Resource Group: $RESOURCE_GROUP"
az group create -l westus -n "$RESOURCE_GROUP" --tags $AZURE_RESOURCE_TAGS

echo "Creating managed disk: $DISK_NAME"
az disk create \
  --resource-group "$RESOURCE_GROUP" \
  --name "$DISK_NAME" \
  --size-gb 4 \
  --location westus \
  --sku Standard_LRS \
  --tags $AZURE_RESOURCE_TAGS

echo "Managed disk created"

echo "Running Azure IOA 518 - Pattern"
echo "Granting access to disk (generating SAS URL for export)"

az disk grant-access \
  --resource-group "$RESOURCE_GROUP" \
  --name "$DISK_NAME" \
  --duration-in-seconds 3600 \
  --access-level Read

echo "Disk access granted (SAS URL generated)"

echo "Running Azure IOA 518 - Cleanup"
echo "Revoking disk access"

az disk revoke-access \
  --resource-group "$RESOURCE_GROUP" \
  --name "$DISK_NAME"

echo "Deleting Resource Group: $RESOURCE_GROUP"
az group delete --yes -n "$RESOURCE_GROUP"

echo "Cleanup complete"
