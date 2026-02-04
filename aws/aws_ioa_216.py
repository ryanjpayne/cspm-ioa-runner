#!/usr/bin/env python3
import boto3, sys, time, json
from zipfile import ZipFile
from io import BytesIO
from utils import AWS_RESOURCE_TAGS

"""

Policy 216 - Lambda layer version policy modified to allow public access

Pattern: Creates IAM role and publishes Lambda layer with permission, lists layers and versions, then adds public permission to layer version.

"""

# Authenticaion and Service Setup
LAMBDA = boto3.Session(profile_name=sys.argv[1]).client("lambda")
IAM = boto3.Session(profile_name=sys.argv[1]).client("iam")
# Variables
FUNCTION_NAME = "TEST_IOA_216"
IOA_ROLE = "IOA_TEST_ROLE_216"
LAYER_NAME = "TEST_IOA_216_LAYER"
POLICY_ID_1 = "TEST_IOA_216_STATEMENT_ID_1"
POLICY_ID_2 = "TEST_IOA_216_STATEMENT_ID_2"


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
        Layers=[LAYER_VERSION_ARN],
    )
    if LAMBDA_CREATE_FUNCTION:
        print(
            "    create-function Successfully Ran\n     Created Function: "
            + FUNCTION_NAME
            + "\n"
        )
    time.sleep(2)


def lambda_delete_function():
    LAMBDA_DELETE_FUNCTION = LAMBDA.delete_function(FunctionName=FUNCTION_NAME)
    if LAMBDA_DELETE_FUNCTION:
        print(
            "    delete-function Successfully Ran\n     Deleted Function: "
            + FUNCTION_NAME
            + "\n"
        )


def lambda_list_layers():
    LAMBDA_LIST_LAYERS = LAMBDA.list_layers()
    if LAMBDA_LIST_LAYERS:
        print("    list-layers Successfully Ran\n")


def lambda_list_layer_versions():
    LAMBDA_LIST_LAYER_VERSIONS = LAMBDA.list_layer_versions(LayerName=LAYER_NAME)
    #    for x in LAMBDA_LIST_LAYER_VERSIONS['LayerVersions']:
    #        print(x['Version'])
    global LAYER_VERSION_ARN
    global LAYER_VERSION
    LAYER_VERSION_ARN = LAMBDA_LIST_LAYER_VERSIONS["LayerVersions"][0][
        "LayerVersionArn"
    ]
    LAYER_VERSION = LAMBDA_LIST_LAYER_VERSIONS["LayerVersions"][0]["Version"]
    if LAMBDA_LIST_LAYER_VERSIONS:
        print("    list-layer-versions Successfully Ran\n")


def lambda_get_layer_version():
    LAMBDA_GET_LAYER_VERSION = LAMBDA.get_layer_version(
        LayerName="TEST_IOA_216_LAYER", VersionNumber=LAYER_VERSION
    )
    if LAMBDA_GET_LAYER_VERSION:
        print("    get-layer-version Successfully Ran\n")


def lambda_get_layer_version_by_arn():
    LAMBDA_GET_LAYER_VERSION_BY_ARN = LAMBDA.get_layer_version_by_arn(
        Arn=LAYER_VERSION_ARN
    )


def lambda_get_layer_version_policy():
    LAMBDA_GET_LAYER_VERSION_POLICY = LAMBDA.get_layer_version_policy(
        LayerName="TEST_IOA_216_LAYER", VersionNumber=LAYER_VERSION
    )
    if LAMBDA_GET_LAYER_VERSION_POLICY:
        print("    get-layer-version-policy Successfully Ran\n")


def lambda_publish_layer_version():
    LAMBDA_PUBLISH_LAYER_VERSION = LAMBDA.publish_layer_version(
        LayerName=LAYER_NAME,
        Content={"ZipFile": ZIP_FILE},
        CompatibleRuntimes=["python3.6"],
    )
    if LAMBDA_PUBLISH_LAYER_VERSION:
        print("    publish-layer-version Successfully Ran\n")
    global LAYER_VERSION_ARN
    global LAYER_VERSION
    LAYER_VERSION_ARN = LAMBDA_PUBLISH_LAYER_VERSION["LayerVersionArn"]
    LAYER_VERSION = LAMBDA_PUBLISH_LAYER_VERSION["Version"]


def lambda_add_layer_version_permission(policyid):
    LAMBDA_ADD_LAYER_VERSION_PERMISSION = LAMBDA.add_layer_version_permission(
        LayerName=LAYER_NAME,
        VersionNumber=LAYER_VERSION,
        StatementId=policyid,
        Action="lambda:GetLayerVersion",
        Principal="*",
    )
    if LAMBDA_ADD_LAYER_VERSION_PERMISSION:
        print("    add-layer-version-permission Successfully Ran\n")


def lambda_remove_layer_version():
    LAMBDA_REMOVE_LAYER_VERSION = LAMBDA.remove_layer_version()
    if LAMBDA_REMOVE_LAYER_VERSION:
        print("    remove-layer-version Successfully Ran\n")


def lambda_delete_layer_version():
    versions = LAMBDA.list_layer_versions(LayerName=LAYER_NAME)
    for x in versions["LayerVersions"]:
        LAMBDA_DELETE_LAYER_VERSION = LAMBDA.delete_layer_version(
            LayerName=LAYER_NAME, VersionNumber=x["Version"]
        )
        if LAMBDA_DELETE_LAYER_VERSION:
            print(
                "\n    delete-layer-version Successfully Ran\n     Deleted Version: "
                + str(x["Version"])
            )


def main():
    # Test Case Prep
    print("\n\nSetting Up for Test Case\n")
    iam_create_role()
    generate_zip()
    lambda_publish_layer_version()
    lambda_list_layer_versions()
    lambda_add_layer_version_permission(POLICY_ID_1)
    # Before Query
    print("\n\nRunning Before Conditions\n")
    lambda_list_layers()
    lambda_list_layer_versions()
    lambda_get_layer_version_policy()
    # Pattern Query
    print("\n\nRunning Pattern Conditions\n")
    lambda_add_layer_version_permission(POLICY_ID_2)
    # After Query
    print("\n\nRunning After Conditions\n")
    lambda_publish_layer_version()
    lambda_get_layer_version()
    lambda_get_layer_version_by_arn()
    lambda_create_function()
    # Clean Up
    print("\n\nCleaning Up\n")
    lambda_delete_layer_version()
    lambda_delete_function()
    iam_delete_role()


if __name__ == "__main__":
    main()
