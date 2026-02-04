#!/bin/bash
set -e

# Source the utils file for standardized tags
# shellcheck source=./utils.sh
source "$(dirname "$0")/utils.sh"

: '
Policy 323 - Virtual Machine manually deleted

Pattern: event.dataset:azure.activitylogs and event.action:"MICROSOFT.COMPUTE/VIRTUALMACHINES/DELETE" and event.outcome:success

'
set -e

RESOURCE_GROUP=CSPM_TESTING_323
VM=323IOAVM

echo "Running Azure IOA 323"
echo "Running Azure IOA 323 - Prep"

echo "Creating Resource Group $RESOURCE_GROUP"
az group create -l westus -n $RESOURCE_GROUP --tags $AZURE_RESOURCE_TAGS

az vm create \
  --resource-group $RESOURCE_GROUP \
  --name $VM \
  --image UbuntuLTS \
  --authentication-type password \
  --admin-password CSPM@test6CSPM@test6 \
  --tags $AZURE_RESOURCE_TAGS

echo "Waiting for $VM to be created"

az vm wait -g $RESOURCE_GROUP -n $VM --created 

echo "Running Azure IOA 323 - Pattern"

az vm delete -g $RESOURCE_GROUP -n $VM --yes

echo "Running Azure IOA 323 - Cleanup"

az vm wait -g $RESOURCE_GROUP -n $VM --deleted 

echo "Deleting Resource Group $RESOURCE_GROUP"
az group delete --yes -n $RESOURCE_GROUP
