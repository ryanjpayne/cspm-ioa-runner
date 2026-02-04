#!/usr/bin/env python3
import boto3, urllib, json, requests, sys, webbrowser, time
from boto3 import client
import botocore

"""

Policy 236 - User without LoginProfile or role logged into the AWS web console

Pattern: Creates IAM user with access key and admin policy, gets caller identity, then gets federation token and initiates console login.

"""

# Authenticaion and Service Setup
IAM = boto3.Session(profile_name=sys.argv[1]).client("iam")
# Variables
BROWSER = "open -a /Applications/Safari.app %s"
NEW_USER = "testioauser_236"
POLICY_NAME = "InlineAdminPolicy"
POLICY = json.dumps(
    {
        "Version": "2012-10-17",
        "Statement": [{"Effect": "Allow", "Action": ["*"], "Resource": ["*"]}],
    }
)


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
        print("\n    create_access_key Successfully Ran")
    global ACCESS_KEY_ID
    ACCESS_KEY_ID = IAM_CREATE_ACCESS_KEY["AccessKey"]["AccessKeyId"]
    print("     AccessKey: " + ACCESS_KEY_ID)
    SECRET_ACCESS_KEY = IAM_CREATE_ACCESS_KEY["AccessKey"]["SecretAccessKey"]
    global STS
    global IAM_NEW_USER
    STS = boto3.Session(
        aws_access_key_id=ACCESS_KEY_ID,
        aws_secret_access_key=SECRET_ACCESS_KEY,
        region_name="eu-west-1",
    ).client("sts")
    IAM_NEW_USER = boto3.Session(
        aws_access_key_id=ACCESS_KEY_ID,
        aws_secret_access_key=SECRET_ACCESS_KEY,
        region_name="eu-west-1",
    ).client("iam")
    time.sleep(10)


def iam_delete_access_key():
    IAM_DELETE_ACCESS_KEY = IAM.delete_access_key(
        UserName=NEW_USER, AccessKeyId=ACCESS_KEY_ID
    )
    if IAM_DELETE_ACCESS_KEY:
        print("\n    delete_access_key Successfully Ran\n     USER: " + NEW_USER)


def iam_put_user_policy():
    IAM_PUT_USER_POLICY = IAM.put_user_policy(
        UserName=NEW_USER, PolicyName=POLICY_NAME, PolicyDocument=POLICY
    )
    if IAM_PUT_USER_POLICY:
        print("\n    put-user-policy Ran Successful")
    time.sleep(10)


def iam_delete_user_policy():
    IAM_DELETE_USER_POLICY = IAM.delete_user_policy(
        UserName=NEW_USER, PolicyName=POLICY_NAME
    )
    if IAM_DELETE_USER_POLICY:
        print("\n    delete-user-policy Ran Successfully\n     Policy: " + POLICY_NAME)


def get_caller_identity():
    STS_GET_CALLER_IDENTITY = STS.get_caller_identity()
    print("\n    get-caller-identity Ran Successfully")


def print_web_console_url():
    STS_GET_FEDERATION_TOKEN = STS.get_federation_token(
        Name="testioafed",
        Policy=json.dumps(
            {
                "Version": "2012-10-17",
                "Statement": [{"Effect": "Allow", "Action": "*", "Resource": "*"}],
            }
        ),
    )
    print("\n    get-federation-token Ran Successfully")
    PARAMS = {
        "Action": "getSigninToken",
        "Session": json.dumps(
            {
                "sessionId": STS_GET_FEDERATION_TOKEN["Credentials"]["AccessKeyId"],
                "sessionKey": STS_GET_FEDERATION_TOKEN["Credentials"][
                    "SecretAccessKey"
                ],
                "sessionToken": STS_GET_FEDERATION_TOKEN["Credentials"]["SessionToken"],
            }
        ),
    }
    FED_RESP = requests.get(
        url="https://signin.aws.amazon.com/federation", params=PARAMS
    )
    SIGNIN_TOKEN = FED_RESP.json()["SigninToken"]
    PARAMS_2 = {
        "Action": "login",
        "Issuer": "",
        "Destination": "https://console.aws.amazon.com/console/home",
        "SigninToken": SIGNIN_TOKEN,
    }
    URL = "https://signin.aws.amazon.com/federation?" + urllib.parse.urlencode(PARAMS_2)
    print("\n    ...Initiating ConsoleLogin\n")
    webbrowser.get(BROWSER).open(URL)


def main():
    # Test Case Prep
    print("\n\nRunning TestCase Prep\n")
    iam_create_user()
    iam_create_access_key()
    iam_put_user_policy()
    # Before Conditions
    print("\n\nRunning Before Conditions\n")
    get_caller_identity()
    # Pattern Conditions
    # print('\n\nRunning Pattern Conditions\n')
    # print('    ----------------------------------------------------\n    MUST CLEAR SAFARI BROWSER CACHE FOR AWS TO CONTINUE\n    ----------------------------------------------------\n')
    # input("   Press Enter to continue...")
    # print_web_console_url()
    # After Conditions
    # print('    -----------------------------------------------\n    Manually Execute After Conditions by clicking\n    through the Console to trigger APIs\n    -----------------------------------------------\n')
    # input("   Press Enter to continue...")
    # Clean Up
    print("\n\nCleaning Up\n")
    iam_delete_access_key()
    iam_delete_user_policy()
    iam_delete_user()


if __name__ == "__main__":
    main()
