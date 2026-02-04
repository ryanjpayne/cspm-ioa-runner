#!/bin/bash
set -e

# Source the utils file for standardized tags
# shellcheck source=./utils.sh
source "$(dirname "$0")/utils.sh"

: '
Policy 321 - Virtual Machine modified to allow ingress from the public Internet

Policy 322 - Virtual Machine modified to allow egress to the public Internet

Pattern: Creates a Network Security Group, adds inbound and outbound rules allowing all traffic from/to the Internet, then deletes the rules.

'
RESOURCE_GROUP=CSPM_TESTING_321_322
echo "Creating Resource Group $RESOURCE_GROUP"
az group create -l westus -n $RESOURCE_GROUP --tags $AZURE_RESOURCE_TAGS

NSG_NAME=NSGIOA
NSG_RULE_321=NSG_321
NSG_RULE_322=NSG_322

echo "Running Prep"
az network nsg create --name $NSG_NAME --resource-group $RESOURCE_GROUP --tags $AZURE_RESOURCE_TAGS

echo "Running 321 Pattern"
az network nsg rule create --name $NSG_RULE_321 --nsg-name $NSG_NAME -g $RESOURCE_GROUP --access Allow --direction Inbound --protocol "*" --destination-port-ranges "*" --destination-address-prefixes "*" --priority 100

echo "Running 322 Pattern"
az network nsg rule create --name $NSG_RULE_322 --nsg-name $NSG_NAME -g $RESOURCE_GROUP --access Allow --direction Outbound --protocol "*" --destination-port-ranges "*" --destination-address-prefixes "*" --priority 100

echo "Cleaning Up"
az network nsg rule delete -g $RESOURCE_GROUP --name $NSG_RULE_321 --nsg-name $NSG_NAME
az network nsg rule delete -g $RESOURCE_GROUP --name $NSG_RULE_322 --nsg-name $NSG_NAME

echo "Deleting Resource Group $RESOURCE_GROUP"
az group delete --yes -n $RESOURCE_GROUP
