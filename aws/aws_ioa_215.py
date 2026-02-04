#!/usr/bin/env python3
import boto3, sys, time, json
from zipfile import ZipFile
from io import BytesIO
from botocore.exceptions import ClientError
from utils import AWS_RESOURCE_TAGS

"""

Policy 215 - Lambda function policy modified to allow public access

Pattern: Creates IAM role and Lambda function with permission, lists functions and gets policy, then adds public permission to function.

"""

# Authenticaion and Service Setup
print(boto3.Session().region_name)
LAMBDA = boto3.Session(profile_name=sys.argv[1]).client("lambda")
IAM = boto3.Session(profile_name=sys.argv[1]).client("iam")
# Variables
FUNCTION_NAME = "TEST_IOA_215"
STATEMENT_ID = FUNCTION_NAME + "_ID1"
STATEMENT_ID2 = FUNCTION_NAME + "_ID2"
IOA_ROLE = "IOA_TEST_ROLE_215"


# print(LAMBDA.region_name)
def generate_zip():
    in_memory = BytesIO()
    zf = ZipFile(in_memory, mode="w")
    zf.writestr("test.txt", "test")
    zf.close()
    in_memory.seek(0)
    global ZIP_FILE
    ZIP_FILE = in_memory.read()


def iam_create_role():
    ASSUME_ROLE_POLICY_DOCUMENT = json.dumps(
        {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Principal": {"Service": "lambda.amazonaws.com"},
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


def lambda_list_functions():
    LAMBDA_LIST_FUNCTIONS = LAMBDA.list_functions()
    if LAMBDA_LIST_FUNCTIONS:
        print("    list-functions Successfully Ran\n")


def lambda_get_policy():
    LAMBDA_GET_POLICY = LAMBDA.get_policy(FunctionName=FUNCTION_NAME)
    if LAMBDA_GET_POLICY:
        print("    get-policy Successfully Ran\n     Function: " + FUNCTION_NAME + "\n")


def lambda_create_function():
    # Convert AWS_RESOURCE_TAGS list format to dict format for Lambda
    tags_dict = {tag["Key"]: tag["Value"] for tag in AWS_RESOURCE_TAGS}
    LAMBDA_CREATE_FUNCTION = LAMBDA.create_function(
        FunctionName=FUNCTION_NAME,
        Runtime="python3.6",
        Role=IOA_ROLE_ARN,
        Handler="my-function-handler",
        Code={"ZipFile": ZIP_FILE},
        Tags=tags_dict,
    )
    if LAMBDA_CREATE_FUNCTION:
        print(
            "    create-function Successfully Ran\n     Created Function: "
            + FUNCTION_NAME
            + "\n"
        )
    time.sleep(2)


def lambda_add_permission(statement_id):
    LAMBDA_ADD_PERMISSION = LAMBDA.add_permission(
        FunctionName=FUNCTION_NAME,
        StatementId=statement_id,
        Action="lambda:InvokeFunction",
        Principal="*",
    )
    if LAMBDA_ADD_PERMISSION:
        print(
            "    add-permission Successfully Ran\n     Function: "
            + FUNCTION_NAME
            + "\n"
        )
    time.sleep(2)


def lambda_invoke_function():
    LAMBDA_INVOKE_FUNCTION = LAMBDA.invoke(FunctionName=FUNCTION_NAME)
    if LAMBDA_INVOKE_FUNCTION:
        print(
            "    invoke-function Successfully Ran\n     Function: "
            + FUNCTION_NAME
            + "\n"
        )


def lambda_update_function_code():
    LAMBDA_UPDATE_FUNCTION_CODE = LAMBDA.update_function_code(
        FunctionName=FUNCTION_NAME, ZipFile=ZIP_FILE
    )
    if LAMBDA_UPDATE_FUNCTION_CODE:
        print(
            "    update-function-code Successfully Ran\n     Function: "
            + FUNCTION_NAME
            + "\n"
        )


def lambda_update_function_configuration():
    LAMBDA_UPDATE_FUNCTION_CONFIGURATION = LAMBDA.update_function_configuration(
        FunctionName=FUNCTION_NAME, Description="testioa215"
    )
    if LAMBDA_UPDATE_FUNCTION_CONFIGURATION:
        print(
            "    update-function-configuration Successfully Ran\n     Function: "
            + FUNCTION_NAME
            + "\n"
        )


def lambda_remove_permission(statement_id):
    LAMBDA_REMOVE_PERMISSION = LAMBDA.remove_permission(
        FunctionName=FUNCTION_NAME, StatementId=statement_id
    )
    if LAMBDA_REMOVE_PERMISSION:
        print(
            "    remove-permission Successfully Ran\n     Removed Function Permission: "
            + statement_id
            + " from "
            + FUNCTION_NAME
            + "\n"
        )


def lambda_delete_function():
    LAMBDA_DELETE_FUNCTION = LAMBDA.delete_function(FunctionName=FUNCTION_NAME)
    if LAMBDA_DELETE_FUNCTION:
        print(
            "    delete-function Successfully Ran\n     Delete Function: "
            + FUNCTION_NAME
            + "\n"
        )


def main():
    # Test Case Prep
    print("\n\nSetting Up for Test Case\n")
    iam_create_role()
    generate_zip()
    lambda_create_function()
    lambda_add_permission(STATEMENT_ID)
    # Before Query
    print("\n\nRunning Before Conditions\n")
    lambda_list_functions()
    lambda_get_policy()
    # Pattern Query
    print("\n\nRunning Pattern Conditions\n")
    lambda_add_permission(STATEMENT_ID2)
    # After Query
    print("\n\nRunning After Conditions\n")
    lambda_update_function_code()
    lambda_invoke_function()
    lambda_update_function_configuration()
    # Clean Up
    print("\n\nCleaning Up\n")
    lambda_remove_permission(STATEMENT_ID)
    lambda_remove_permission(STATEMENT_ID2)
    lambda_delete_function()
    iam_delete_role()


if __name__ == "__main__":
    main()
