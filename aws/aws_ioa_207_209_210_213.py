#!/usr/bin/env python3
import boto3, json, sys

"""

Policy 207 - S3 bucket access logging disabled

Pattern: Creates S3 bucket with policy and versioning, gets bucket configurations, then disables logging.

Policy 209 - S3 bucket made public through ACL

Pattern: Creates S3 bucket with policy and versioning, gets bucket configurations, then sets public ACL.

Policy 210 - S3 bucket made public through policy

Pattern: Creates S3 bucket with policy and versioning, gets bucket configurations, then applies public bucket policy.

Policy 213 - S3 bucket versioning disabled

Pattern: Creates S3 bucket with policy and versioning, gets bucket configurations, then disables versioning.

"""
# Authenticaion and Service Setup
S3 = boto3.Session(region_name="us-east-1", profile_name=sys.argv[1]).client("s3")
# Variables
BUCKET = "testioap207p209p210p213"
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
STATUS_ENABLED = "Enabled"
STATUS_DISABLED = "Suspended"


def s3_create_bucket():
    s3_create_bucket = S3.create_bucket(Bucket=BUCKET)
    if s3_create_bucket:
        print("\n    create-bucket Successfully Ran\n     Created Bucket: " + BUCKET)


def s3_list_bucket():
    s3_list_bucket = S3.list_buckets()
    if s3_list_bucket:
        print(
            "\n    list_bucket_policy Successfully Ran\n     List S3 Buckets: " + BUCKET
        )


def s3_get_bucket_policy():
    s3_get_bucket_policy = S3.get_bucket_policy(Bucket=BUCKET)
    if s3_get_bucket_policy:
        print(
            "\n    get_bucket_policy Successfully Ran\n     Gathered Bucket Policy: "
            + BUCKET
        )


def s3_get_bucket_acl():
    s3_get_bucket_acl = S3.get_bucket_acl(Bucket=BUCKET)
    if s3_get_bucket_acl:
        print(
            "\n    get_bucket_acl Successfully Ran\n     Gathered Bucket ACL Policy: "
            + BUCKET
        )


def s3_get_bucket_versioning():
    s3_get_bucket_versioning = S3.get_bucket_versioning(Bucket=BUCKET)
    if s3_get_bucket_versioning:
        print(
            "\n    get_bucket_versioning Successfully Ran\n     Gathered Bucket versioning Policy: "
            + BUCKET
        )


def s3_get_bucket_logging():
    s3_get_bucket_logging = S3.get_bucket_logging(Bucket=BUCKET)
    if s3_get_bucket_logging:
        print(
            "\n    get_bucket_logging Successfully Ran\n     Gathered Bucket Logging: "
            + BUCKET
        )


def s3_put_bucket_policy():
    s3_put_bucket_policy = S3.put_bucket_policy(Bucket=BUCKET, Policy=BUCKET_POLICY)
    if s3_put_bucket_policy:
        print(
            "\n    put-bucket-policy Successfully Ran\n     Created Bucket Policy for Bucket: "
            + BUCKET
        )


def s3_put_bucket_acl():
    s3_put_bucket_acl = S3.put_bucket_acl(ACL="public-read-write", Bucket=BUCKET)
    if s3_put_bucket_acl:
        print(
            "\n    put-bucket-acl Successfully Ran\n     Created Bucket ACL Policy for Bucket: "
            + BUCKET
        )


def s3_put_bucket_logging():
    s3_put_bucket_logging = S3.put_bucket_logging(Bucket=BUCKET, BucketLoggingStatus={})
    if s3_put_bucket_acl:
        print(
            "\n    put-bucket-logging Successfully Ran\n     Created Bucket Logging for Bucket: "
            + BUCKET
        )


def s3_put_bucket_versioning(status):
    s3_put_bucket_versioning = S3.put_bucket_versioning(
        Bucket=BUCKET,
        VersioningConfiguration={"Status": status},
    )


def s3_delete_bucket():
    s3_delete_bucket = S3.delete_bucket(Bucket=BUCKET)
    if s3_delete_bucket:
        print("\n    delete-bucket Successfully Ran\n     Deleted Bucket: " + BUCKET)


def main():
    # Test Case Prep
    print("\n\nSetting Up for Test Case\n")
    s3_create_bucket()
    s3_put_bucket_policy()
    s3_put_bucket_versioning(STATUS_ENABLED)
    # Before Query
    print("\n\nRunning Policy 207, 209, 210, 213 Before Conditions\n")
    s3_list_bucket()
    print("\n\nRunning Policy 210 Before Conditions\n")
    s3_get_bucket_policy()
    print("\n\nRunning Policy 209 Before Conditions\n")
    s3_get_bucket_acl()
    print("\n\nRunning Policy 207 Before Conditions\n")
    s3_get_bucket_logging()
    print("\n\nRunning Policy 213 Before Conditions\n")
    s3_get_bucket_versioning()
    # Pattern Query
    print("\n\nRunning Policy 210 Pattern Conditions\n")
    s3_put_bucket_policy()
    print("\n\nRunning Policy 209 Pattern Conditions\n")
    s3_put_bucket_acl()
    print("\n\nRunning Policy 207 Pattern Conditions\n")
    s3_put_bucket_logging()
    print("\n\nRunning Policy 213 Pattern Conditions\n")
    s3_put_bucket_versioning(STATUS_DISABLED)
    # After Query
    print("\n\nRunning Policy 207, 209, 210, 213 After Conditions\n")
    s3_list_bucket()
    s3_get_bucket_policy()
    s3_get_bucket_acl()
    s3_get_bucket_logging()
    s3_get_bucket_versioning()
    # Clean Up
    print("\n\nCleaning Up\n")
    s3_delete_bucket()


if __name__ == "__main__":
    main()
