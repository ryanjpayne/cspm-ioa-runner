#!/usr/bin/env python3
import boto3, sys
from boto3 import client
import botocore

"""

Policy 235 - API call made from hacking-related operating system

Pattern: Makes IAM API calls with user agents containing hacking-related OS names (kali, pentoo, parrot).

Policy 258 - Tool usage: ScoutSuite

Pattern: Makes IAM API calls with user agent containing "Scout Suite".

Policy 259 - Tool usage: Endgame

Pattern: Makes IAM API calls with user agent containing "HotDogsAreSandwiches".

Policy 264 - Tool usage: CloudBerry Explorer

Pattern: Makes IAM API calls with user agent containing "CloudBerry".

"""

# Variables
UA_1 = "kali"
UA_2 = "pentoo"
UA_3 = "parrot"
UA_4 = "Scout Suite"
UA_5 = "HotDogsAreSandwiches"
UA_6 = "CloudBerry"


def iam_list_users(ua):
    # Authenticaion and Service Setup
    SESSION_CONFIG = botocore.config.Config(user_agent=ua)
    IAM = boto3.Session(profile_name=sys.argv[1]).client("iam", config=SESSION_CONFIG)
    IAM_LIST_USERS = IAM.list_users()
    if IAM_LIST_USERS:
        print("   list-users Ran Successfully with UserAgent: " + ua)


def main():
    # Pattern Query
    print("Running Policy 235 Pattern Conditions")
    iam_list_users(UA_1)
    iam_list_users(UA_2)
    iam_list_users(UA_3)
    print("\n\nRunning Policy 258 Pattern Conditions")
    iam_list_users(UA_4)
    print("\n\nRunning Policy 259 Pattern Conditions")
    iam_list_users(UA_5)
    print("\n\nRunning Policy 264 Pattern Conditions")
    iam_list_users(UA_6)


if __name__ == "__main__":
    main()
