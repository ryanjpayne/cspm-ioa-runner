#!/usr/bin/env python3
import boto3, sys, time
from botocore.exceptions import ClientError

"""

Policy 234 - Multiple access denied API calls recorded

Pattern: Creates IAM user with access key, then makes multiple CloudTrail API calls that generate access denied errors.

"""

# Authenticaion and Service Setup
IAM = boto3.Session(profile_name=sys.argv[1]).client("iam")
# Variables
NEW_USER = "testioauser_234"


def iam_create_user():
    IAM_CREATE_USER = IAM.create_user(UserName=NEW_USER)
    if IAM_CREATE_USER:
        print("\n    create_user Successfully Ran\n     USER: " + NEW_USER)


def iam_delete_user():
    IAM_DELETE_USER = IAM.delete_user(UserName=NEW_USER)
    if IAM_DELETE_USER:
        print("\n    delete_user Successfully Ran\n     USER: " + NEW_USER)


def iam_create_access_key():
    IAM_CREATE_ACCESS_KEY = IAM.create_access_key(UserName=NEW_USER)
    if IAM_CREATE_ACCESS_KEY:
        print("    create_access_key Successfully Ran\n")
    global ACCESS_KEY_ID
    ACCESS_KEY_ID = IAM_CREATE_ACCESS_KEY["AccessKey"]["AccessKeyId"]
    SECRET_ACCESS_KEY = IAM_CREATE_ACCESS_KEY["AccessKey"]["SecretAccessKey"]
    global CLOUDTRAIL
    CLOUDTRAIL = boto3.Session(
        aws_access_key_id=ACCESS_KEY_ID,
        aws_secret_access_key=SECRET_ACCESS_KEY,
        region_name="eu-west-1",
    ).client("cloudtrail")
    time.sleep(10)


def iam_delete_access_key():
    IAM_DELETE_ACCESS_KEY = IAM.delete_access_key(
        UserName=NEW_USER, AccessKeyId=ACCESS_KEY_ID
    )
    if IAM_DELETE_ACCESS_KEY:
        print("\n    delete_access_key Successfully Ran\n     USER: " + NEW_USER)


def cloudtrail_list_trails():
    for l in range(50):
        try:
            cloudtrail_list_trails = CLOUDTRAIL.list_trails()
            print(cloudtrail_list_trails)
        except ClientError as e:
            print(e.response["Error"]["Code"])


def main():
    # Setup
    iam_create_user()
    iam_create_access_key()
    # Pattern Query
    print("\n\nRunning Pattern Conditions\n")
    cloudtrail_list_trails()
    # Clean Up
    iam_delete_access_key()
    iam_delete_user()


if __name__ == "__main__":
    main()
