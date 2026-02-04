#!/usr/bin/env python3
import boto3, sys, json, time, uuid
from utils import AWS_RESOURCE_TAGS

"""

Policy 255 - Elastic File System policy modified to allow public access

Pattern: Creates EFS file system, then puts file system policy with public principal ("*"), and describes the policy.

"""
client = boto3.Session(profile_name=sys.argv[1]).client("efs", region_name="us-east-1")
EFS_NAME = "cspmtestefs255"


def create_efs():
    token_uuid = str(uuid.uuid1())
    efs_values = {}
    response = client.create_file_system(
        CreationToken=token_uuid,
        PerformanceMode="generalPurpose",
        Tags=AWS_RESOURCE_TAGS,
    )

    id = response["FileSystemId"]
    arn = response["FileSystemArn"]
    efs_values["id"] = str(id)
    efs_values["arn"] = str(arn)

    return efs_values


def put_file_system_policy(values):
    efs_id = values["id"]
    efs_arn = values["arn"]
    policy_string = '{"Version":"2012-10-17","Statement":{"Effect":"Allow","Principal":{"AWS": "*"},"Action":["elasticfilesystem:AccessPointArn"],"Resource":"ARN"}}'.replace(
        "ARN", efs_arn
    )
    POLICY = json.loads(policy_string)
    response = client.put_file_system_policy(FileSystemId=efs_id, Policy=policy_string)

    print(response)


def perform_after_condition(id):
    response = client.describe_file_system_policy(FileSystemId=id)
    print(response)


def delete_file_system(efs_id):
    response = client.delete_file_system(
        FileSystemId=efs_id,
    )
    # returns 204
    print(response)


def main():
    print("\n\nPerforming Prep Conditions\n")
    efs_values = create_efs()
    efs_id = efs_values["id"]
    time.sleep(5)

    print("\n\nPerforming Pattern Conditions\n")
    put_file_system_policy(efs_values)

    print("\n\nPerforming After\n")
    perform_after_condition(efs_id)

    print("\n\nPerforming Clean Up\n")

    delete_file_system(efs_id)


if __name__ == "__main__":
    main()
