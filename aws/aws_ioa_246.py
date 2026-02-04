#!/usr/bin/env python3
import boto3, sys, time, json
from botocore.exceptions import ClientError
from utils import AWS_RESOURCE_TAGS

"""

Policy 246 - IAM role passed to new CloudFormation stack

Pattern: Creates IAM role with policy, lists roles and policies, then creates CloudFormation stack with role ARN and assumes the role identity.

"""
# simple cloudformation template
TEMPLATE = {
    "AWSTemplateFormatVersion": "2010-09-09",
    "Description": "Basic CFN template for testing",
    "Resources": {
        "246cspmtestbucketcfn": {
            "Type": "AWS::S3::Bucket",
            "Properties": {
                "AccessControl": "Private",
                "BucketName": "246cspmtestbucketcfn",
            },
        }
    },
}

IAM = boto3.Session(profile_name=sys.argv[1]).client("iam", region_name="us-east-1")
CFN = boto3.Session(profile_name=sys.argv[1]).client(
    "cloudformation", region_name="us-east-1"
)
STS = boto3.Session(profile_name=sys.argv[1]).client("sts", region_name="us-east-1")
waiter = CFN.get_waiter("stack_create_complete")
delete_waiter = CFN.get_waiter("stack_delete_complete")
ROLE = "cspmtestrole246"
STACK_NAME = "cspmioateststack246"
POLICY_NAME = "cspmtestpolicy246"

ASSUME_ROLE_POLICY_DOCUMENT = json.dumps(
    {
        "Version": "2012-10-17",
        "Statement": [
            {"Effect": "Allow", "Principal": {"AWS": "*"}, "Action": "sts:AssumeRole"}
        ],
    }
)
STACK_POLICY = json.dumps(
    {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Action": ["s3:CreateBucket", "s3:DeleteBucket"],
                "Resource": ["arn:aws:s3:::*"],
            }
        ],
    }
)


def create_role():
    print(type(ASSUME_ROLE_POLICY_DOCUMENT))
    try:
        response = IAM.create_role(
            RoleName=ROLE,
            AssumeRolePolicyDocument=ASSUME_ROLE_POLICY_DOCUMENT,
            Description="CSPM Test Role",
            Tags=AWS_RESOURCE_TAGS,
        )
        global IOA_ROLE_ARN
        IOA_ROLE_ARN = response["Role"]["Arn"]
        print(f"\n\nROLE CREATION {response}\n\n")
        time.sleep(20)
    except ClientError as e:
        if e.response["Error"]["Code"] == "EntityAlreadyExists":
            print("Role already exists. Deleting Role")
            delete_role()
            time.sleep(10)
            create_role()
        else:
            print(e)


def create_policy():
    response = IAM.create_policy(
        PolicyName=POLICY_NAME,
        Path="/",
        PolicyDocument=STACK_POLICY,
        Tags=AWS_RESOURCE_TAGS,
    )
    time.sleep(10)
    print(response)
    arn = response["Policy"]["Arn"]
    return arn


def attach_role_policy(policy_arn):
    policy_attach_res = IAM.attach_role_policy(RoleName=ROLE, PolicyArn=policy_arn)

    time.sleep(20)


def list_roles():
    response = IAM.list_roles()
    print(response)


def list_role_policies():
    try:
        response = IAM.list_role_policies(RoleName=ROLE)
        print(response)
    except ClientError as e:
        print(e)


def list_attached_role_policies():
    response = IAM.list_attached_role_policies(RoleName=ROLE, PathPrefix="/")


def create_stack():
    response = CFN.create_stack(
        StackName=STACK_NAME,
        TemplateBody=json.dumps(TEMPLATE),
        Parameters=[],
        DisableRollback=False,
        TimeoutInMinutes=20,
        Capabilities=[
            "CAPABILITY_IAM",
        ],
        Tags=AWS_RESOURCE_TAGS,
        RoleARN=IOA_ROLE_ARN,
    )


def sts_assume_identity():
    response = STS.assume_role(
        RoleArn=IOA_ROLE_ARN,
        RoleSessionName="123testcspm",
    )


def detatch_role_policy(arn):
    response = IAM.detach_role_policy(RoleName=ROLE, PolicyArn=arn)


def delete_role():
    delete_role = IAM.delete_role(RoleName=ROLE)

    print(delete_role)


def delete_policy(arn):
    response = IAM.delete_policy(PolicyArn=arn)


def delete_stack():
    response = CFN.delete_stack(StackName=STACK_NAME)


def main():
    print(f"\nPrep:\n")
    create_role()
    policy_arn = str(create_policy())
    attach_role_policy(policy_arn)

    print(f"\nBefore Conditions:\n")
    list_roles()
    list_role_policies()
    list_attached_role_policies()

    print(f"\nPattern Condition:\n")
    create_stack()
    print("\n\Building Stack....")
    waiter.wait(StackName=STACK_NAME)

    sts_assume_identity()

    delete_stack()
    detatch_role_policy(policy_arn)
    delete_role()
    delete_policy(policy_arn)
    print("\n\nDeleting Stack....")
    delete_waiter.wait(StackName=STACK_NAME)


if __name__ == "__main__":
    main()
