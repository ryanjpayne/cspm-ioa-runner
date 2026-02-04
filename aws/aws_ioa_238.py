#!/usr/bin/env python3
import boto3, sys, time, json
from botocore.exceptions import ClientError
from utils import AWS_RESOURCE_TAGS

"""

Policy 238 - Inline administrator policy (*:*) applied to IAM principal (user, role, group)

Pattern: Creates IAM user, group, and role, lists and gets IAM entities, then applies inline administrator policies to user, role, and group.

"""
# User Variables
USER = "cspmtestjj238"
GROUP = "cspmtestgroupjj238"
ROLE = "cspmtestrolejj238"
POLICY_NAME = "cspmtestpolicyjj238"
POLICY = json.dumps(
    {
        "Version": "2012-10-17",
        "Statement": [{"Effect": "Allow", "Action": ["*"], "Resource": ["*"]}],
    }
)
IAM = boto3.Session(profile_name=sys.argv[1]).client("iam")


def create_user():
    try:
        response = IAM.create_user(UserName=USER)
        print(f"Create User Output:\n {response}")
    except ClientError as e:
        if e.response["Error"]["Code"] == "EntityAlreadyExists":
            print("User already exists")


def iam_create_access_key():
    IAM_CREATE_ACCESS_KEY = IAM.create_access_key(UserName=USER)
    if IAM_CREATE_ACCESS_KEY:
        print("    create_access_key Successfully Ran\n")
    global ACCESS_KEY_ID
    ACCESS_KEY_ID = IAM_CREATE_ACCESS_KEY["AccessKey"]["AccessKeyId"]
    SECRET_ACCESS_KEY = IAM_CREATE_ACCESS_KEY["AccessKey"]["SecretAccessKey"]
    global iam
    iam = boto3.Session(
        aws_access_key_id=ACCESS_KEY_ID,
        aws_secret_access_key=SECRET_ACCESS_KEY,
        region_name="eu-west-1",
    ).client("iam")
    time.sleep(10)


def iam_delete_access_key(accesskeyid):
    IAM_DELETE_ACCESS_KEY = IAM.delete_access_key(
        UserName=USER, AccessKeyId=accesskeyid
    )
    if IAM_DELETE_ACCESS_KEY:
        print("\n    delete_access_key Successfully Ran\n     USER: " + USER)


def create_group():
    try:
        response = IAM.create_group(GroupName=GROUP)
        print(f"Create Group Output:\n {response}")
    except ClientError as e:
        if e.response["Error"]["Code"] == "EntityAlreadyExists":
            print("group already exists")


def create_role():
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
    try:
        response = IAM.create_role(
            RoleName=ROLE,
            AssumeRolePolicyDocument=ASSUME_ROLE_POLICY_DOCUMENT,
            Description="CSPM Test Role",
            Tags=AWS_RESOURCE_TAGS,
        )
        # print(response)
    except ClientError as e:
        if e.response["Error"]["Code"] == "EntityAlreadyExists":
            print("group already exists")


def list_users(iam_creds):
    print(iam_creds)
    response = iam_creds.list_users()
    # print(response)


def list_user_policies():
    response = IAM.list_user_policies(
        UserName=USER,
    )
    # print(response)


def list_attached_user_policies(iam_creds):
    response = iam_creds.list_attached_user_policies(UserName=USER, PathPrefix="/")
    # print(response)


def get_user():
    response = IAM.get_user(
        UserName=USER,
    )
    # print(response)


def list_groups():
    response = IAM.list_groups()
    # print(response)


def list_group_policies():
    response = IAM.list_group_policies(GroupName=GROUP)


def list_attached_group_policies():
    response = IAM.list_attached_group_policies(GroupName=GROUP)


def get_group():
    response = IAM.get_group(GroupName=GROUP)


def list_roles(iam_creds):
    response = iam_creds.list_roles()
    # print(response)


def list_role_policies(iam_creds):
    response = iam_creds.list_role_policies(RoleName=ROLE)
    # print(response)


def list_attached_role_policies(iam_creds):
    response = iam_creds.list_attached_role_policies(RoleName=ROLE, PathPrefix="/")


def get_role(iam_creds):
    response = iam_creds.get_role(RoleName=ROLE)


# pattern Conditions
def iam_put_user_policy():
    response = IAM.put_user_policy(
        UserName=USER, PolicyName=POLICY_NAME, PolicyDocument=POLICY
    )
    # print(f"\nPattern Condition:\n{response}")


def perform_clean_up():
    delete_user_policy = IAM.delete_user_policy(
        PolicyName=POLICY_NAME,
        UserName=USER,
    )
    delete_role_policy = IAM.delete_role_policy(RoleName=ROLE, PolicyName=POLICY_NAME)
    delete_group_policy = IAM.delete_group_policy(
        GroupName=GROUP, PolicyName=POLICY_NAME
    )
    delete_role = IAM.delete_role(RoleName=ROLE)
    delete_user = IAM.delete_user(UserName=USER)
    delete_group = IAM.delete_group(GroupName=GROUP)
    print(
        f"\n\n\nCLEAN UP:\nDeleted user: {delete_user}\nDeleted Group: {delete_group}\n Detach Policy:{delete_user_policy} \nDelete_Role: {delete_role}"
    )


def put_role_policy():
    put_role_policy = IAM.put_role_policy(
        RoleName=ROLE, PolicyName=POLICY_NAME, PolicyDocument=POLICY
    )


def put_group_policy():
    put_group_policy = IAM.put_group_policy(
        GroupName=GROUP, PolicyName=POLICY_NAME, PolicyDocument=POLICY
    )


def main():
    # Setup
    print("\n\nPerforming Setup")
    create_user()
    iam_create_access_key()
    #    ACCESS_KEY_ID = iam_create_access_key()
    #    iam_create_access_key()
    create_group()
    create_role()
    # Before Conditions
    print("\n\nPerforming Before Pattern")
    list_users(IAM)
    list_user_policies()
    list_attached_user_policies(IAM)
    get_user()
    list_groups()
    list_group_policies()
    list_attached_group_policies()
    get_group()
    list_roles(IAM)
    list_role_policies(IAM)
    list_attached_role_policies(IAM)
    get_role(IAM)
    # Pattern Condition
    print("\n\nPerforming Pattern")
    iam_put_user_policy()
    put_role_policy()
    put_group_policy()
    time.sleep(10)
    # After condition
    print("\n\nPerforming After Pattern")
    list_users(iam)
    list_attached_user_policies(iam)
    list_roles(iam)
    list_role_policies(iam)
    list_attached_role_policies(iam)
    get_role(iam)
    # Cleanup
    iam_delete_access_key(ACCESS_KEY_ID)
    perform_clean_up()


if __name__ == "__main__":
    main()
