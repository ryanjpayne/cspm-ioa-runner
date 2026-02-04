#!/usr/bin/env python3
import boto3, sys, time, json
from zipfile import ZipFile
from io import BytesIO

"""

Policy 217 - Serverless Application Repository policy modified to allow public access

Pattern: Creates S3 bucket and serverless application with policy, lists applications and gets policy, then sets public application policy.

"""

# Authenticaion and Service Setup
SERVERLESSREPO = boto3.Session(
    region_name="us-east-1", profile_name=sys.argv[1]
).client("serverlessrepo")
S3 = boto3.Session(region_name="us-east-1", profile_name=sys.argv[1]).client("s3")
# Variables
BUCKET = "cspmtestioa217"
STATEMENT_ID_1 = "TESTIOA217"
STATEMENT_ID_2 = "TESTIOA217VERSION2"
LICENSE = "license"
APPLICATION_NAME = "TESTIOAAPPLICATION217"
APPLICATION_VERSION = "1.0.0"
ZIPFILE = "test.zip"
BUCKET_POLICY = (
    json.dumps(
        {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Principal": "*",
                    "Action": "s3:*Object",
                    "Resource": ["arn:aws:s3:::%s/*"],
                }
            ],
        }
    )
    % BUCKET
)
TEMPLATE = json.dumps(
    {
        "AWSTemplateFormatVersion": "2010-09-09",
        "Transform": "AWS::Serverless-2016-10-31",
        "Resources": {
            "MyFunction": {
                "Type": "AWS::Serverless::Function",
                "Properties": {
                    "Handler": "index.handler",
                    "Runtime": "nodejs14.10",
                    "CodeUri": "s3://cspmtestioa217/test.zip",
                },
            }
        },
    }
)


def generate_zip():
    in_memory = BytesIO()
    zf = ZipFile(in_memory, mode="w")
    zf.writestr(ZIPFILE, "test")
    zf.close()
    in_memory.seek(0)
    zip_file = in_memory.read()
    return zip_file


def s3_create_bucket():
    s3_create_bucket = S3.create_bucket(Bucket=BUCKET)
    if s3_create_bucket:
        print("\n    create-bucket Successfully Ran\n     Created Bucket: " + BUCKET)


def s3_delete_bucket():
    s3_delete_bucket = S3.delete_bucket(Bucket=BUCKET)
    if s3_delete_bucket:
        print("\n    delete-bucket Successfully Ran\n     Deleted Bucket: " + BUCKET)


def s3_put_bucket_policy():
    s3_put_bucket_policy = S3.put_bucket_policy(Bucket=BUCKET, Policy=BUCKET_POLICY)
    if s3_put_bucket_policy:
        print(
            "\n    put-bucket-policy Successfully Ran\n     Created Bucket Policy for Bucket: "
            + BUCKET
        )


def s3_put_object(zip_file):
    s3_put_object = S3.put_object(Bucket=BUCKET, Body=zip_file, Key=ZIPFILE)
    if s3_put_object:
        print(
            "\n    put-object Successfully Ran\n     Bucket: "
            + BUCKET
            + "\n     File: "
            + ZIPFILE
        )


def s3_delete_object():
    s3_delete_object = S3.delete_object(Bucket=BUCKET, Key=ZIPFILE)
    if s3_delete_object:
        print(
            "\n    s3_delete_object Successfully Ran\n     Bucket: "
            + BUCKET
            + "\n     File: "
            + ZIPFILE
        )


def serverlessrepo_create_application(zip_file):
    serverlessrepo_create_application = SERVERLESSREPO.create_application(
        Author="testioaauthor",
        Description=APPLICATION_NAME,
        LicenseBody=LICENSE,
        Name=APPLICATION_NAME,
        SemanticVersion=APPLICATION_VERSION,
        SourceCodeUrl="https://crowdstrike.com/",
        TemplateBody=TEMPLATE,
    )
    time.sleep(3)
    if serverlessrepo_create_application:
        print(
            "\n    create-application Successfully Ran\n     Application: "
            + APPLICATION_NAME
        )
    global application_arn
    global application_version
    application_arn = serverlessrepo_create_application["ApplicationId"]
    application_version = serverlessrepo_create_application["Version"][
        "SemanticVersion"
    ]


def serverlessrepo_delete_application():
    serverlessrepo_delete_application = SERVERLESSREPO.delete_application(
        ApplicationId=application_arn
    )
    if serverlessrepo_delete_application:
        print(
            "\n    delete-application Successfully Ran\n     Application: "
            + APPLICATION_NAME
        )


def serverlessrepo_put_application_policy(statement_id):
    serverlessrepo_put_application_policy = SERVERLESSREPO.put_application_policy(
        ApplicationId=application_arn,
        Statements=[
            {
                "Actions": ["ListApplicationVersions"],
                "Principals": [
                    "*",
                ],
                "StatementId": statement_id,
            },
        ],
    )
    if serverlessrepo_put_application_policy:
        print(
            "\n    put-application-policy Successfully Ran\n     Application: "
            + APPLICATION_NAME
            + "\n     StatementID: "
            + statement_id
        )


def serverlessrepo_list_applications():
    serverlessrepo_list_applications = SERVERLESSREPO.list_applications()
    if serverlessrepo_list_applications:
        print("\n    list-applications Successfully Ran")


def serverlessrepo_get_application_policy():
    serverlessrepo_get_application_policy = SERVERLESSREPO.get_application_policy(
        ApplicationId=application_arn
    )
    if serverlessrepo_get_application_policy:
        print("\n    get_application_policy Successfully Ran")


def serverlessrepo_get_application():
    serverlessrepo_get_application = SERVERLESSREPO.get_application(
        ApplicationId=application_arn
    )
    if serverlessrepo_get_application:
        print("\n    get-application Successfully Ran")


def main():
    # Test Case Prep
    print("\n\nSetting Up for Test Case\n")
    zipfile = generate_zip()
    s3_create_bucket()
    s3_put_bucket_policy()
    s3_put_object(zipfile)
    serverlessrepo_create_application(zipfile)
    serverlessrepo_put_application_policy(STATEMENT_ID_1)
    # Before Query
    print("\n\nRunning Before Conditions\n")
    serverlessrepo_list_applications()
    serverlessrepo_get_application_policy()
    serverlessrepo_get_application()
    # Pattern Query
    print("\n\nRunning Pattern Conditions\n")
    serverlessrepo_put_application_policy(STATEMENT_ID_2)
    # After Query
    print("\n\nRunning After Conditions\n")

    # Clean Up
    print("\n\nCleaning Up\n")
    serverlessrepo_delete_application()
    s3_delete_object()
    s3_delete_bucket()


if __name__ == "__main__":
    main()
