#!/usr/bin/env python3
import boto3, sys, time, json
from botocore.exceptions import ClientError
from utils import AWS_RESOURCE_TAGS

"""

Policy 253 - Default VPC deleted

Pattern: Creates key pair and default VPC, describes instances, then creates and runs EC2 instance.

Policy 249 - EC2 instance manually deleted by IAM user

Pattern: Describes instances, then terminates EC2 instance.

"""

KEYPAIR = "ioa253keypair"
IMAGE_NAME = "AWSIOA253"
REGION = "us-east-1"

TAGS = AWS_RESOURCE_TAGS


class EC2Test(object):
    def __init__(self, client):
        self.client = client

    def setup(self):
        print("\nSetting up for Policy 253 test")
        print("\nCreaing KeyPair")

        try:
            self.keypair = self.client.create_key_pair(
                KeyName=KEYPAIR,
                TagSpecifications=[{"ResourceType": "key-pair", "Tags": TAGS}],
            )
            print(f"Key Pair Created")
        except ClientError as e:
            if e.response["Error"]["Code"] == "EntityAlreadyExists":
                print("KeyPair Already Exists. Deleting...")
                self.clean_up()
                time.sleep(20)
                self.setup()

    def trigger_before(self):
        print("\nRunning Before Conditions for Policy 253 test")

        self.describe_instances = self.client.describe_instances()

        try:
            # if not creating a vpc comment out the next 2 lines and uncomment the third line
            self.create_default_vpc = self.client.create_default_vpc()
            self.vpc_id = self.create_default_vpc["Vpc"]["VpcId"]
            # self.vpc_id = "null"
        except ClientError as e:
            if e.response["Error"]["Code"] == "DefaultVpcAlreadyExists":
                print(
                    "**************************************************************************"
                )
                print(f"{REGION}.console.aws.amazon.com/vpc/home")
                key = input("*** Policy 253 - Please Delete Default VPC ***")
                print(
                    "**************************************************************************"
                )
                self.trigger_before()
        print(self.vpc_id)
        return self.vpc_id

    def trigger_pattern(self):
        print("\nRunning Pattern Conditions for Policy 253 test")
        images = self.client.describe_images(
            Owners=["amazon"], Filters=[{"Name": "name", "Values": ["amzn2-ami-hvm*"]}]
        )
        ami = images["Images"][0]["ImageId"]
        self.create_image = self.client.run_instances(
            ImageId=ami,
            InstanceType="t3.micro",
            KeyName=KEYPAIR,
            MinCount=1,
            MaxCount=1,
            TagSpecifications=[{"ResourceType": "instance", "Tags": TAGS}],
        )
        print(f"CREATE OUTPUT: {self.create_image}")
        self.instance_id = self.create_image["Instances"][0]["InstanceId"]
        return self.instance_id

    def trigger_waiter(self, id, ec2_waiters):
        ec2_waiter.wait(InstanceIds=[id])

    def trigger_249_before(self):
        print("\nRunning Before Conditions for Policy 249 test")

        self.describe_image = self.client.describe_instances()

    def trigger_249_pattern(self, id):
        self.terminate_instance = self.client.terminate_instances(InstanceIds=[id])

    def clean_up(self, instances):
        print("CLEANING UP")
        self.delete_key_pair = self.client.delete_key_pair(KeyName=KEYPAIR)
        self.delete_image = self.client.terminate_instances(InstanceIds=instances)
        print(self.delete_image)
        print(self.delete_key_pair)

    def delete_vpc(self, vpc):
        print("REMOVING VPC")
        time.sleep(40)
        try:
            self.delete_vpc = self.client.delete_vpc(VpcId=vpc)
            print(self.delete_vpc)
        except ClientError as e:
            print(e)
            if e.response["Error"]["Code"] == "DependencyViolation":
                print("WAITING TO DELETE VPC")
                self.delete_vpc(vpc)


if __name__ == "__main__":
    instances = []
    aws_profile = sys.argv[1]
    print("Using AWS profile", aws_profile)
    ec2 = boto3.Session(profile_name=aws_profile).client("ec2", region_name=REGION)
    ec2_waiter = ec2.get_waiter("instance_running")
    account = (
        boto3.Session(profile_name=aws_profile)
        .client("sts")
        .get_caller_identity()
        .get("Account")
    )
    print(f"\nACCOUNT{account}\n")

    test = EC2Test(ec2)
    test.setup()

    # Avoiding creating a default vpc in non-cscbte enviornments
    if account == "698278383212":
        vpc_id = test.trigger_before()

    instance_id = test.trigger_pattern()
    test.trigger_waiter(instance_id, ec2_waiter)
    test.trigger_249_before()
    test.trigger_249_pattern(instance_id)

    # Vpc needs to be manually deleted
    instances.append(instance_id)

    test.clean_up(instances)

    # if vpc_id:
    #     vpc_id = test.delete_vpc(vpc_id)
