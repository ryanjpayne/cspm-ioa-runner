#!/usr/bin/env python3
"""

Policy 206 - VPC Flow logs disabled

Pattern: Creates VPC flow logs, describes them, then deletes the flow logs.

"""

import sys, time

import boto3

from utils import AWS_RESOURCE_TAGS

SLEEP_SECONDS = 3
DIV_LINE = "*" * 80
BUCKET = "cspmioa206bucket"


class VPCFlowLogsTest(object):
    def __init__(self, session, vpc_id=None, s3_bucket_arn=None):
        self.session = session
        self.client = self.session.client("ec2")
        if vpc_id is None:
            self.vpc = self.client.create_vpc(CidrBlock="192.168.0.0/22")
            self.vpc_id = self.vpc["Vpc"]["VpcId"]
        else:
            self.vpc_id = vpc_id
        if s3_bucket_arn is None:
            self.s3 = self.session.client("s3")
            new_bucket = self.s3.create_bucket(Bucket=BUCKET)
            self.s3_bucket_arn = "arn:aws:s3:::%s" % (BUCKET)
        else:
            self.s3_bucket_arn = s3_bucket_arn

    def setup(
        self,
    ):
        """
        This needs to run if you are creating a new SNS topic.
        """
        print(DIV_LINE)
        print("Setup: create flow logs for VPC ID ", self.vpc_id)
        result = self.client.create_flow_logs(
            ResourceIds=[self.vpc_id],
            ResourceType="VPC",
            TrafficType="ACCEPT",
            LogDestinationType="s3",
            LogDestination=self.s3_bucket_arn,
            TagSpecifications=[
                {"ResourceType": "vpc-flow-log", "Tags": AWS_RESOURCE_TAGS}
            ],
        )
        self._vpc_flow_log_ids = result["FlowLogIds"]

    def trigger_before(self):
        print(DIV_LINE)
        print("Triggering IOA before correlation: describe-flow-logs")
        result = self.client.describe_flow_logs()
        print(result)
        print(result["ResponseMetadata"]["HTTPHeaders"]["date"])

    def trigger_ioa(self):
        print(DIV_LINE)
        time.sleep(10)
        print("Triggering IOA: Deleting flow logs")
        result = self.client.delete_flow_logs(FlowLogIds=self._vpc_flow_log_ids)
        print(result)
        print(result["ResponseMetadata"]["HTTPHeaders"]["date"])

    def trigger_after(self):
        print("No after pattern to trigger")

    def cleanup(self):
        print("Cleaning up")
        print("Verifying flow logs deleted")
        result = self.client.describe_flow_logs()
        print(result)
        self.client.delete_vpc(VpcId=self.vpc_id)
        s3 = boto3.resource("s3")
        bucket = s3.Bucket(BUCKET)
        bucket.objects.delete()
        response = bucket.delete()


if __name__ == "__main__":
    aws_profile = sys.argv[1]
    try:
        vpc_id = sys.argv[2]
    except IndexError as e:
        print("No VPC ID set. Creating a test VPC.")
        vpc_id = None

    try:
        s3_bucket_arn = sys.argv[3]
    except IndexError as e:
        print("No S3 bucket ARN configured. Creating a test S3 Bucket.")
        s3_bucket_arn = None

    print("Using AWS profile", aws_profile)
    botosession = boto3.Session(profile_name=aws_profile)

    print("Setting up for Policy 206 test")
    test = VPCFlowLogsTest(botosession, vpc_id=vpc_id, s3_bucket_arn=s3_bucket_arn)

    test.setup()
    time.sleep(SLEEP_SECONDS)

    test.trigger_before()
    time.sleep(SLEEP_SECONDS)

    test.trigger_ioa()
    time.sleep(SLEEP_SECONDS)

    test.trigger_after()
    time.sleep(SLEEP_SECONDS)

    test.cleanup()
    print("Test 206 complete")
