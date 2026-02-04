#!/usr/bin/env python3
import argparse
import boto3
import sys
import time
from botocore.exceptions import ClientError

"""

Policy 211 - EC2 security group modified to allow ingress from the public internet

Pattern: Creates EC2 security group, describes security groups and instances, then authorizes ingress from public internet.

Policy 212 - EC2 security group modified to allow egress to the public internet

Pattern: Creates EC2 security group, describes security groups and instances, then authorizes egress to public internet.

Policy 214 - ECR repository policy modified to allow public access

Pattern: Creates ECR repository with policy, describes repositories and gets policy, then sets repository policy to allow public access.

"""

# Set up and parse options
parser = argparse.ArgumentParser(description="CSPM AWS IOA Test script")

parser.add_argument(
    "-p",
    "--policy",
    type=int,
    dest="policies",
    action="append",
    default=[211, 212, 214],
    help="REQUIRED: Which policy to run. Can have multiple instances to run multiple tests.",
)
parser.add_argument(
    "-i",
    "--iterations",
    type=int,
    dest="iterations",
    default=1,
    help="How many times to run each action (defaults to 1)",
)
parser.add_argument(
    "-b",
    "--before",
    action="store_true",
    dest="run_before",
    default=False,
    help="Whether to run any before_query actions",
)
parser.add_argument(
    "-a",
    "--after",
    action="store_true",
    dest="run_after",
    default=False,
    help="Whether to run any after_query actions",
)
parser.add_argument(
    "aws_cli_profile",
    action="store",
    help="The name of the AWS CLI profile you wish to use",
)
options = parser.parse_args()

if len(options.policies) == 0:
    parser.error("Need to specify at least one policy to run")
    parser.print_help()

try:
    boto3_session = boto3.Session(profile_name=options.aws_cli_profile)
except:
    print(
        "Failed to start boto3 session with given profile: " + options.aws_cli_profile
    )
    parser.print_help()
    sys.exit(1)

print("Running policy(s):")
print(*options.policies, sep=", ")
print("Include before actions: " + str(options.run_before))
print("Include after actions: " + str(options.run_after))
print("Iterations of each action to run: " + str(options.iterations))

if 211 in options.policies:
    # EC2 security group modified to allow ingress from the public internet
    print("---Running Policy 211---")
    ec2 = boto3_session.client("ec2", region_name="us-west-2")

    # Set up resources to use
    security_group_id = None
    try:
        # Check whether the SG already exists
        result = ec2.describe_security_groups()
        for sg in result["SecurityGroups"]:
            if sg["GroupName"] == "CSPM_Testing_policy_211":
                print("Test security group already exists, deleting: ", sg["GroupId"])
                result = ec2.delete_security_group(GroupId=sg["GroupId"])
                break

        # Create the test SG
        # Find the first VPC
        result = ec2.describe_vpcs()
        vpc_id = result.get("Vpcs", [{}])[0].get("VpcId", "")
        result = ec2.create_security_group(
            GroupName="CSPM_Testing_policy_211",
            Description="For testing CSPM policy 211, temporary",
        )
        security_group_id = result["GroupId"]

        # Give the new group a bit to show up everywhere
        time.sleep(5)
        print(
            "["
            + result["ResponseMetadata"]["HTTPHeaders"]["date"]
            + "] "
            + "Created test security group: ",
            security_group_id,
        )
    except ClientError as e:
        print(e)

    # before: ec2:DescribeSecurityGroups, ec2:DescribeInstances
    if options.run_before:
        for x in range(0, options.iterations):
            result = ec2.describe_security_groups(MaxResults=5)
            print(
                "["
                + result["ResponseMetadata"]["HTTPHeaders"]["date"]
                + "] ec2:DescribeSecurityGroups"
            )
        for x in range(0, options.iterations):
            result = ec2.describe_instances()
            print(
                "["
                + result["ResponseMetadata"]["HTTPHeaders"]["date"]
                + "] ec2:DescribeInstances"
            )

    # policy: ec2:AuthorizeSecurityGroupIngress where
    # .requestParameters.ipPermissions.items[].ipRanges.items[].cidrIp == "0.0.0.0/0" OR
    # .requestParameters.ipPermissions.items[].ipv6Ranges.items[].cidrIpv6 == "::/0"
    for x in range(0, options.iterations):
        result = ec2.authorize_security_group_ingress(
            GroupId=security_group_id,
            IpPermissions=[
                {
                    "IpProtocol": "tcp",
                    "FromPort": 22 + x,
                    "ToPort": 22 + x,
                    "IpRanges": [{"CidrIp": "0.0.0.0/0"}],
                }
            ],
        )
        print(
            "["
            + result["ResponseMetadata"]["HTTPHeaders"]["date"]
            + "] ec2:AuthorizeSecurityGroupIngress (ipv4)"
            + " status: "
            + str(result["ResponseMetadata"]["HTTPStatusCode"])
        )

    for x in range(0, options.iterations):
        result = ec2.authorize_security_group_ingress(
            GroupId=security_group_id,
            IpPermissions=[
                {
                    "IpProtocol": "tcp",
                    "FromPort": 22 + x,
                    "ToPort": 22 + x,
                    "Ipv6Ranges": [{"CidrIpv6": "::/0"}],
                }
            ],
        )
        print(
            "["
            + result["ResponseMetadata"]["HTTPHeaders"]["date"]
            + "] ec2:AuthorizeSecurityGroupIngress (ipv6)"
            + " status: "
            + str(result["ResponseMetadata"]["HTTPStatusCode"])
        )

    # after: ec2:DescribeInstances
    if options.run_after:
        for x in range(0, options.iterations):
            result = ec2.describe_instances()
            print(
                "["
                + result["ResponseMetadata"]["HTTPHeaders"]["date"]
                + "] ec2:DescribeInstances"
            )

    # Cleanup
    try:
        result = ec2.delete_security_group(GroupId=security_group_id)
        print(
            "Deleted the test security group. status: "
            + str(result["ResponseMetadata"]["HTTPStatusCode"])
        )
    except ClientError as e:
        print(e)

if 212 in options.policies:
    # EC2 security group modified to allow egress to the public internet
    print("---Running Policy 212---")
    ec2 = boto3_session.client("ec2", region_name="us-west-2")

    # Set up resources to use
    security_group_id = None
    try:
        # Check whether the SG already exists
        result = ec2.describe_security_groups()
        for sg in result["SecurityGroups"]:
            if sg["GroupName"] == "CSPM_Testing_policy_212":
                print("Test security group already exists, deleting: ", sg["GroupId"])
                ec2.delete_security_group(GroupId=sg["GroupId"])
                break

        # Create the test SG
        # Find the first VPC
        result = ec2.describe_vpcs()
        vpc_id = result.get("Vpcs", [{}])[0].get("VpcId", "")
        result = ec2.create_security_group(
            GroupName="CSPM_Testing_policy_212",
            Description="For testing CSPM policy 212, temporary",
        )
        security_group_id = result["GroupId"]

        # Give the new group a bit to show up everywhere
        time.sleep(5)
        print(
            "["
            + result["ResponseMetadata"]["HTTPHeaders"]["date"]
            + "] "
            + "Created test security group: ",
            security_group_id,
        )
    except ClientError as e:
        print(e)

    # before: ec2:DescribeSecurityGroups, ec2:DescribeInstances
    if options.run_before:
        for x in range(0, options.iterations):
            result = ec2.describe_security_groups(MaxResults=5)
            print(
                "["
                + result["ResponseMetadata"]["HTTPHeaders"]["date"]
                + "] ec2:DescribeSecurityGroups"
            )
        for x in range(0, options.iterations):
            result = ec2.describe_instances()
            print(
                "["
                + result["ResponseMetadata"]["HTTPHeaders"]["date"]
                + "] ec2:DescribeInstances"
            )

    # policy: ec2:AuthorizeSecurityGroupEgress where
    # .requestParameters.ipPermissions.items[].ipRanges.items[].cidrIp == "0.0.0.0/0" OR
    # .requestParameters.ipPermissions.items[].ipv6Ranges.items[].cidrIpv6 == "::/0"
    for x in range(0, options.iterations):
        result = ec2.authorize_security_group_egress(
            GroupId=security_group_id,
            IpPermissions=[
                {
                    "IpProtocol": "tcp",
                    "FromPort": 22 + x,
                    "ToPort": 22 + x,
                    "IpRanges": [{"CidrIp": "0.0.0.0/0"}],
                }
            ],
        )
        print(
            "["
            + result["ResponseMetadata"]["HTTPHeaders"]["date"]
            + "] ec2:AuthorizeSecurityGroupEgress (ipv4)"
            + " status: "
            + str(result["ResponseMetadata"]["HTTPStatusCode"])
        )

    for x in range(0, options.iterations):
        result = ec2.authorize_security_group_egress(
            GroupId=security_group_id,
            IpPermissions=[
                {
                    "IpProtocol": "tcp",
                    "FromPort": 22 + x,
                    "ToPort": 22 + x,
                    "Ipv6Ranges": [{"CidrIpv6": "::/0"}],
                }
            ],
        )
        print(
            "["
            + result["ResponseMetadata"]["HTTPHeaders"]["date"]
            + "] ec2:AuthorizeSecurityGroupEgress (ipv6)"
            + " status: "
            + str(result["ResponseMetadata"]["HTTPStatusCode"])
        )

    # after: ec2:DescribeInstances
    if options.run_after:
        for x in range(0, options.iterations):
            result = ec2.describe_instances()
            print(
                "["
                + result["ResponseMetadata"]["HTTPHeaders"]["date"]
                + "] ec2:DescribeInstances"
            )

    # Cleanup
    try:
        result = ec2.delete_security_group(GroupId=security_group_id)
        print(
            "Deleted the test security group. status: "
            + str(result["ResponseMetadata"]["HTTPStatusCode"])
        )
    except ClientError as e:
        print(e)

if 214 in options.policies:
    # ECR repository policy modified to allow public access
    print("---Running Policy 214---")
    ecr = boto3_session.client("ecr", region_name="us-west-2")

    # Set up resources for test
    target_repository = None
    try:
        # Check whether the repository already exists
        result = ecr.describe_repositories()
        for repo in result["repositories"]:
            if repo["repositoryName"] == "cspm_testing_policy_214":
                print(
                    "Test repository already exists, deleting: ", repo["repositoryName"]
                )
                ecr.delete_repository(repositoryName=repo["repositoryName"])
                break

        # Create the test Repo
        result = ecr.create_repository(repositoryName="cspm_testing_policy_214")
        target_repository = result["repository"]["repositoryName"]
        result = ecr.set_repository_policy(
            repositoryName=target_repository,
            force=False,
            policyText='{"Version": "2008-10-17","Statement": [{"Sid": "testing only","Effect": "Deny","Principal": {"Service": "codebuild.amazonaws.com"},"Action": ["ecr:GetLifecyclePolicy"]}]}',
        )

        # Give the new object a bit to show up everywhere
        time.sleep(5)
        print(
            "["
            + result["ResponseMetadata"]["HTTPHeaders"]["date"]
            + "] "
            + "Created test repository: ",
            target_repository,
        )
    except ClientError as e:
        print(e)

    # before: ecr:DescribeRepositories, ecr:GetRepositoryPolicy
    if options.run_before:
        for x in range(0, options.iterations):
            result = ecr.describe_repositories(maxResults=10)
            print(
                "["
                + result["ResponseMetadata"]["HTTPHeaders"]["date"]
                + "] ecr:DescribeRepositories"
            )
        for x in range(0, options.iterations):
            result = ecr.get_repository_policy(repositoryName=target_repository)
            print(
                "["
                + result["ResponseMetadata"]["HTTPHeaders"]["date"]
                + "] ecr:GetRepositoryPolicy"
            )

    # policy: ecr:SetRepositoryPolicy with principal=*
    for x in range(0, options.iterations):
        result = ecr.set_repository_policy(
            repositoryName=target_repository,
            force=False,
            policyText='{"Version": "2008-10-17","Statement": [{"Sid": "testing only","Effect": "Allow","Principal": "*","Action": ["ecr:GetLifecyclePolicy"]}]}',
        )
        print(
            "["
            + result["ResponseMetadata"]["HTTPHeaders"]["date"]
            + "] ecr:SetRepositoryPolicy"
            + " status: "
            + str(result["ResponseMetadata"]["HTTPStatusCode"])
        )

    # after: any action on same ECR
    if options.run_after:
        for x in range(0, options.iterations):
            result = ecr.get_repository_policy(repositoryName=target_repository)
            print(
                "["
                + result["ResponseMetadata"]["HTTPHeaders"]["date"]
                + "] ecr:GetRepositoryPolicy"
            )

    # Cleanup
    try:
        result = ecr.delete_repository(repositoryName=target_repository)
        print(
            "Deleted the test repository. status: "
            + str(result["ResponseMetadata"]["HTTPStatusCode"])
        )
    except ClientError as e:
        print(e)
