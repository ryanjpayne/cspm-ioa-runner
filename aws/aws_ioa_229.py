#!/usr/bin/env python3
import boto3, sys, time, json, os
from utils import AWS_RESOURCE_TAGS

"""

Policy 229 - CloudTrail logging disabled

Pattern: Creates S3 bucket and CloudTrail trail with logging, describes trails and gets status, then stops logging and deletes trail.

"""

# Authenticaion and Service Setup
CLOUDTRAIL = boto3.Session(profile_name=sys.argv[1]).client("cloudtrail")
S3 = boto3.Session(region_name="us-east-1", profile_name=sys.argv[1]).client("s3")
# Variables
TRAIL_NAME = "test_ioa_229"
BUCKET = "awscloudtraillogsioa229"
BUCKET_POLICY = json.dumps(
    {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Sid": "AWSCloudTrailAclCheck20150319",
                "Effect": "Allow",
                "Principal": {"Service": "cloudtrail.amazonaws.com"},
                "Action": "s3:GetBucketAcl",
                "Resource": "arn:aws:s3:::%s",
            },
            {
                "Sid": "AWSCloudTrailWrite20150319",
                "Effect": "Allow",
                "Principal": {"Service": "cloudtrail.amazonaws.com"},
                "Action": "s3:PutObject",
                "Resource": "arn:aws:s3:::%s/*",
                "Condition": {
                    "StringEquals": {"s3:x-amz-acl": "bucket-owner-full-control"}
                },
            },
        ],
    }
) % (BUCKET, BUCKET)


def s3_create_bucket():
    s3_create_bucket = S3.create_bucket(Bucket=BUCKET)
    if s3_create_bucket:
        print("\n    create-bucket Successfully Ran\n     Created Bucket: " + BUCKET)


def s3_delete_bucket():
    s3_delete_bucket = S3.delete_bucket(Bucket=BUCKET)
    if s3_delete_bucket:
        print("   delete-bucket Successfully Ran\n    Deleted Bucket: " + BUCKET)


def s3_put_bucket_policy():
    s3_put_bucket_policy = S3.put_bucket_policy(Bucket=BUCKET, Policy=BUCKET_POLICY)
    if s3_put_bucket_policy:
        print(
            "\n    put-bucket-policy Successfully Ran\n     Created Bucket Policy for Bucket: "
            + BUCKET
        )


def s3_delete_object():
    cmd = (
        "aws s3 rm --recursive s3://awscloudtraillogsioa229/AWSLogs/ --profile %s  > /dev/null"
        % sys.argv[1]
    )
    s3_delete_object = os.system(cmd)


def create_trail():
    cloudtrail_create_trail = CLOUDTRAIL.create_trail(
        Name=TRAIL_NAME,
        S3BucketName=BUCKET,
        IncludeGlobalServiceEvents=False,
        IsMultiRegionTrail=False,
        EnableLogFileValidation=False,
        IsOrganizationTrail=False,
        TagsList=AWS_RESOURCE_TAGS,
    )
    if cloudtrail_create_trail:
        print(
            "\n    create-trail Successfully Ran\n    Created Trail: "
            + TRAIL_NAME
            + "\n"
        )


def start_logging():
    cloudtrail_start_logging = CLOUDTRAIL.start_logging(Name=TRAIL_NAME)
    if cloudtrail_start_logging:
        print(
            "   start-logging Successfully Ran\n    Started Logging for Trail: "
            + TRAIL_NAME
            + "\n"
        )


def stop_logging():
    cloudtrail_stop_logging = CLOUDTRAIL.start_logging(Name=TRAIL_NAME)
    if cloudtrail_stop_logging:
        print(
            "   stop-logging Successfully Ran\n    Stopped Logging for Trail: "
            + TRAIL_NAME
            + "\n"
        )


def delete_trail():
    cloudtrail_delete_trail = CLOUDTRAIL.delete_trail(Name=TRAIL_NAME)
    if cloudtrail_delete_trail:
        print(
            "   delete-trail Successfully Ran\n    Deleted Trail: " + TRAIL_NAME + "\n"
        )


def udpate_trail():
    cloudtrail_update_trail = CLOUDTRAIL.update_trail(
        Name=TRAIL_NAME, IncludeGlobalServiceEvents=False
    )
    if cloudtrail_update_trail:
        print(
            "   update-trail Successfully Ran\n    Updated Trail: " + TRAIL_NAME + "\n"
        )


def describe_trails():
    cloudtrail_describe_trails = CLOUDTRAIL.describe_trails()
    if cloudtrail_describe_trails:
        print("   describe-trails Successfully Ran\n")


def list_trails():
    cloudtrail_list_trails = CLOUDTRAIL.list_trails()
    if cloudtrail_list_trails:
        print("   list-trails Successfully Ran\n")


def get_event_selectors():
    cloudtrail_get_event_selectors = CLOUDTRAIL.get_event_selectors(
        TrailName=TRAIL_NAME
    )
    if cloudtrail_get_event_selectors:
        print("   get-event-selectors Successfully Ran\n")


def get_trail_status():
    cloudtrail_get_trail_status = CLOUDTRAIL.get_trail_status(Name=TRAIL_NAME)
    if cloudtrail_get_trail_status:
        print("   get-trail-status Successfully Ran\n    Trail: " + TRAIL_NAME + "\n")


def main():
    # Test Case Prep
    print("\n\nSetting Up for Test Case\n")
    s3_create_bucket()
    s3_put_bucket_policy()
    create_trail()
    start_logging()
    # Before Query
    print("\n\nRunning Before Conditions\n")
    describe_trails()
    list_trails()
    get_event_selectors()
    get_trail_status()
    # Pattern Query
    print("\n\nRunning Pattern Conditions\n")
    stop_logging()
    udpate_trail()
    delete_trail()
    # After Query
    print("\n\nRunning After Conditions\n")
    describe_trails()
    # Clean Up
    print("\nCleaning Up\n")
    s3_delete_object()
    s3_delete_bucket()


if __name__ == "__main__":
    main()
