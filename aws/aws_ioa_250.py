#!/usr/bin/env python3
import boto3, sys, time
from utils import AWS_RESOURCE_TAGS

"""

Policy 250 - EC2 instance limit enumerated through GameLift followed by instance creation

Pattern: Creates key pair, describes EC2 instance limits via GameLift, then runs EC2 instance.

"""

# Authenticaion and Service Setup
EC2 = boto3.Session(region_name="eu-west-3", profile_name=sys.argv[1]).client("ec2")
GAMELIFT = boto3.Session(profile_name=sys.argv[1]).client("gamelift")
# Variables
AMI = "ami-0d6aecf0f0425f42a"
INSTANCE_NAME = "TestIOA-250"
KEY_PAIR = "testioakey_250"


def ec2_create_key_pair():
    EC2_CREATE_KEY_PAIR = EC2.create_key_pair(
        KeyName=KEY_PAIR,
        TagSpecifications=[{"ResourceType": "key-pair", "Tags": AWS_RESOURCE_TAGS}],
    )
    if EC2_CREATE_KEY_PAIR:
        print(
            "\n   create-key-pair Successfully Ran\n     Created KeyPair: " + KEY_PAIR
        )


def ec2_delete_key_pair():
    EC2_DELETE_KEY_PAIR = EC2.delete_key_pair(KeyName=KEY_PAIR)
    if EC2_DELETE_KEY_PAIR:
        print("   delete-key-pair Successfully Ran\n     Deleted KeyPair: " + KEY_PAIR)


def describe_ec2_instance_limits():
    gamelift_describe_ec2_instance_limits = GAMELIFT.describe_ec2_instance_limits()
    if gamelift_describe_ec2_instance_limits:
        print("   describe_ec2_instance_limits Successfully Ran\n")


def run_instances(instance_name):
    # Add Name tag to AWS_RESOURCE_TAGS
    tags_with_name = AWS_RESOURCE_TAGS + [{"Key": "Name", "Value": instance_name}]
    ec2_run_instances = EC2.run_instances(
        ImageId=AMI,
        InstanceType="t2.micro",
        KeyName=KEY_PAIR,
        MinCount=1,
        MaxCount=1,
        TagSpecifications=[{"ResourceType": "instance", "Tags": tags_with_name}],
    )
    for i in ec2_run_instances["Instances"]:
        global INSTANCE_ID
        INSTANCE_ID = i["InstanceId"]

    if ec2_run_instances:
        print(
            "   run-instances Successfully Ran\n    Created Instance: "
            + INSTANCE_ID
            + "\n"
        )


def terminate_instances():
    ec2_terminate_instances = EC2.terminate_instances(
        InstanceIds=[
            INSTANCE_ID,
        ],
        DryRun=False,
    )
    if ec2_terminate_instances:
        print(
            "   terminate-instances Successfully Ran\n    Terminated Instance: "
            + INSTANCE_ID
            + "\n"
        )


def main():
    # Setup
    ec2_create_key_pair()
    # Pattern Query
    print("\n\nRunning Pattern Conditions\n")
    describe_ec2_instance_limits()
    run_instances(INSTANCE_NAME)
    # Clean Up
    print("\n\nCleaning Up\n")
    terminate_instances()
    ec2_delete_key_pair()


if __name__ == "__main__":
    main()
