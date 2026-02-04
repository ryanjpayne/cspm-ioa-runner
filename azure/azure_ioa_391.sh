#!/bin/bash
set -e

# Source the utils file for standardized tags
# shellcheck source=./utils.sh
source "$(dirname "$0")/utils.sh"

: '
Policy 391 - Event Hub deleted

Pattern: Creates an Event Hub namespace and Event Hub, then deletes the Event Hub, then cleans up.

'

RESOURCE_GROUP="CSPM-TESTING-391"
NAMESPACE="cspm391ns$(date +%s)"
EVENTHUB="cspm391eh"

echo "Running Azure IOA 391"
echo "Running Azure IOA 391 - Prep"

echo "Creating Resource Group: $RESOURCE_GROUP"
az group create -l westus -n "$RESOURCE_GROUP" --tags $AZURE_RESOURCE_TAGS

echo "Creating Event Hub namespace: $NAMESPACE"
az eventhubs namespace create \
  --name "$NAMESPACE" \
  --resource-group "$RESOURCE_GROUP" \
  --location westus \
  --sku Basic \
  --tags $AZURE_RESOURCE_TAGS

echo "Creating Event Hub: $EVENTHUB"
az eventhubs eventhub create \
  --name "$EVENTHUB" \
  --namespace-name "$NAMESPACE" \
  --resource-group "$RESOURCE_GROUP"

echo "Event Hub created"

echo "Running Azure IOA 391 - Pattern"
echo "Deleting Event Hub: $EVENTHUB"

az eventhubs eventhub delete \
  --name "$EVENTHUB" \
  --namespace-name "$NAMESPACE" \
  --resource-group "$RESOURCE_GROUP"

echo "Event Hub deleted"

echo "Running Azure IOA 391 - Cleanup"
echo "Deleting Resource Group: $RESOURCE_GROUP"

az group delete --yes -n "$RESOURCE_GROUP"

echo "Cleanup complete"
