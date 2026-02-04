#!/usr/bin/env python3
import boto3, sys, json, time

"""

Policy 254 - CloudWatch logs policy modified to allow public access

Pattern: Puts CloudWatch Logs resource policy with public principal ("*").

"""
client = boto3.Session(profile_name=sys.argv[1]).client("logs", region_name="us-east-1")
POLICY = json.dumps(
    {
        "Version": "2012-10-17",
        "Statement": {
            "Effect": "Allow",
            "Principal": {"AWS": "*"},
            "Action": ["secretsmanager:GetSecretValue"],
            "Resource": "*",
        },
    }
)

POLICY_NAME = "cspmtestpolicy254"


def put_resource_policy():
    response = client.put_resource_policy(policyName=POLICY_NAME, policyDocument=POLICY)
    print(response)


def delete_resource_policy():
    response = client.delete_resource_policy(policyName=POLICY_NAME)
    print(f"\n\n{response}")


def main():
    put_resource_policy()
    time.sleep(15)
    delete_resource_policy()


if __name__ == "__main__":
    main()
