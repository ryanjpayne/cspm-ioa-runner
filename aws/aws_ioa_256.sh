#!/bin/bash

: '
Policy 256 - Simple Email Service sender authorization policy modified to allow public access

Pattern: Creates SES email identity, puts identity policy with public principal ("*"), gets identity DKIM attributes, and lists identity policies.

'

EMAIL=aws-ioa-256-test@crowdstrike.com
REGION=us-east-1
PROFILE=${1:-cscbte}
ACCOUNT=$(aws sts get-caller-identity --query Account --output text --profile ${PROFILE})
ARN=arn:aws:ses:$REGION:$ACCOUNT:identity/$EMAIL

echo "Performing Prep"
aws sesv2 create-email-identity --email-identity $EMAIL --profile $PROFILE --region $REGION

#Pattern
echo "Performing Pattern"
aws ses put-identity-policy --identity $ARN --policy-name ioa256 --policy '{"Version":"2012-10-17","Statement":{"Effect":"Allow","Principal":{"AWS": "*"},"Action":["SES:SendEmail"],"Resource":"'$ARN'"}}' --profile $PROFILE --region $REGION

echo "Performing After"
aws ses get-identity-dkim-attributes --identities $EMAIL --profile $PROFILE --region $REGION
aws ses list-identity-policies --identity $EMAIL --profile $PROFILE --region $REGION

echo "Cleaning Up"
# Cleaning Up
aws ses delete-identity --identity $EMAIL --profile $PROFILE --region $REGION
