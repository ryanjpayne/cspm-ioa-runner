#!/bin/bash
set -e

# Source the utils file for standardized tags
# shellcheck source=./utils.sh
source "$(dirname "$0")/utils.sh"

: '
Policy 243 - Event Hub namespace deleted

Pattern: Creates an Event Hub namespace, then deletes it.

'

RESOURCE_GROUP="CSPM-TESTING-243"
NAMESPACE="cspm243ns$(date +%s)"

echo "Running Azure IOA 243"
echo "Running Azure IOA 243 - Prep"

echo "Creating Resource Group: $RESOURCE_GROUP"
az group create -l westus -n "$RESOURCE_GROUP" --tags $AZURE_RESOURCE_TAGS

echo "Creating Event Hub namespace: $NAMESPACE"
az eventhubs namespace create \
  --name "$NAMESPACE" \
  --resource-group "$RESOURCE_GROUP" \
  --location westus \
  --sku Basic \
  --tags $AZURE_RESOURCE_TAGS

echo "Event Hub namespace created"

echo "Running Azure IOA 243 - Pattern"
echo "Deleting Event Hub namespace: $NAMESPACE"

az eventhubs namespace delete \
  --name "$NAMESPACE" \
  --resource-group "$RESOURCE_GROUP"

echo "Event Hub namespace deleted"

echo "Running Azure IOA 243 - Cleanup"
echo "Deleting Resource Group: $RESOURCE_GROUP"

az group delete --yes -n "$RESOURCE_GROUP"

echo "Cleanup complete"
