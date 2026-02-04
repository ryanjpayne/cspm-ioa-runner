#!/usr/bin/env python3
import boto3, sys, time, json
from utils import AWS_RESOURCE_TAGS

"""

Policy 257 - IAM role assumed itself

Pattern: Creates IAM role, assumes the role, then assumes the same role again from within the assumed role session.

"""

# Authenticaion and Service Setup
STS = boto3.Session(profile_name=sys.argv[1]).client("sts")
IAM = boto3.Session(profile_name=sys.argv[1]).client("iam")
# Variables
IOA_ROLE = "IOA_TEST_ROLE_257"


def iam_create_role():
    ASSUME_ROLE_POLICY_DOCUMENT = json.dumps(
        {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Principal": {"AWS": "*"},
                    "Action": "sts:AssumeRole",
                }
            ],
        }
    )
    IAM_CREATE_ROLE = IAM.create_role(
        RoleName=IOA_ROLE,
        AssumeRolePolicyDocument=ASSUME_ROLE_POLICY_DOCUMENT,
        Tags=AWS_RESOURCE_TAGS,
    )
    global IOA_ROLE_ARN
    IOA_ROLE_ARN = IAM_CREATE_ROLE["Role"]["Arn"]
    if IAM_CREATE_ROLE:
        print(
            "    create-role Successfully Ran\n\n    ***Creating " + IOA_ROLE + "***\n"
        )
    time.sleep(10)


def iam_delete_role():
    IAM_DELETE_ROLE = IAM.delete_role(RoleName=IOA_ROLE)
    if IAM_DELETE_ROLE:
        print("    delete-role Successfully Ran\n     Deleted Role: " + IOA_ROLE)


def iam_list_users(session):
    IAM_LIST_USERS = session.list_users()
    if IAM_LIST_USERS:
        print("    list-users Successfully Ran\n")


def sts_assume_role(session):
    STS_ASSUME_ROLE = session.assume_role(
        RoleArn=IOA_ROLE_ARN, RoleSessionName="IOA_257"
    )
    # global ACCESS_KEY_ID
    # global SECRET_ACCESS_KEY
    # global SESSION_TOKEN
    global STS2
    ACCESS_KEY_ID = STS_ASSUME_ROLE["Credentials"]["AccessKeyId"]
    SECRET_ACCESS_KEY = STS_ASSUME_ROLE["Credentials"]["SecretAccessKey"]
    SESSION_TOKEN = STS_ASSUME_ROLE["Credentials"]["SessionToken"]
    STS2 = boto3.Session(
        aws_access_key_id=ACCESS_KEY_ID,
        aws_secret_access_key=SECRET_ACCESS_KEY,
        aws_session_token=SESSION_TOKEN,
    ).client("sts")
    if STS_ASSUME_ROLE:
        print(
            "    assume-role Successfully Ran\n     Role Id: "
            + STS_ASSUME_ROLE["AssumedRoleUser"]["AssumedRoleId"]
            + "\n     Access Key: "
            + STS_ASSUME_ROLE["Credentials"]["AccessKeyId"]
        )


def main():
    # iam_delete_role()
    # Test Case Prep
    print("\n\nSetting Up for Test Case\n")
    iam_create_role()
    sts_assume_role(STS)
    # Pattern Query
    print("\n\nRunning Pattern Conditions\n")
    sts_assume_role(STS2)
    # After Query
    print("\n\nRunning After Conditions\n")
    # iam_list_users(IAM2)
    sts_assume_role(STS2)
    # Clean Up
    print("\n\nCleaning Up\n")
    iam_delete_role()


if __name__ == "__main__":
    main()
