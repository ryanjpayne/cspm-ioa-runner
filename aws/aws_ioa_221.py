#!/usr/bin/env python3
"""

Policy 221 - SNS topic policy modified to allow public access

Pattern: Creates SNS topic, gets topic attributes, then adds public permission to topic.

"""

import sys, time

import boto3

from utils import AWS_RESOURCE_TAGS


TEST_EMAIL = "esther.nam@crowdstrike.com"
IOA_TOPIC = "cspm-ioa-test"
IOA_POLICY_NAME = "sns-ioa-dangerous"
SLEEP_SECONDS = 3
DIV_LINE = "*" * 80


class SNSTest(object):
    def __init__(self, session, topic_name=IOA_TOPIC):
        self.session = session
        self.client = self.session.client("sns")
        self.topic_name = topic_name
        self._topic = None  # will be set after setup

    @property
    def topic(self):
        if self._topic is None:
            raise ValueError("Must run setup() to create resource")
        return self._topic

    @topic.setter
    def topic(self, topic):
        self._topic = topic

    def setup(self):
        """
        This needs to run if you are creating a new SNS topic.
        """
        print(DIV_LINE)
        print("Setup")
        print("Creating topic", self.topic_name)
        new_topic = self.client.create_topic(
            Name=self.topic_name,
            Tags=AWS_RESOURCE_TAGS,
        )

        print("Response:\n", new_topic)
        print("Topic created:", new_topic["TopicArn"])
        self.topic = self.session.resource("sns").Topic(new_topic["TopicArn"])

    def trigger_before(self):
        print(DIV_LINE)
        print("Triggering IOA before correlation: get attribute")
        result = self.client.get_topic_attributes(TopicArn=self.topic.arn)
        print(result)
        print(result["ResponseMetadata"]["HTTPHeaders"]["date"])

    def trigger_ioa(self):
        print(DIV_LINE)
        print("Triggering IOA: Adding public permission")
        result = self.topic.add_permission(
            Label=IOA_POLICY_NAME, AWSAccountId=["*"], ActionName=["Publish"]
        )
        print(result)

    def trigger_after(self):
        print(DIV_LINE)
        print("Triggering IOA after correlation: Subscribing to topic")
        result = self.client.subscribe(
            TopicArn=self.topic.arn,
            Protocol="email",
            Endpoint=TEST_EMAIL,
        )
        print(result)

    def cleanup(self):
        print(DIV_LINE)
        print("Cleanup (remove perms)")
        self.topic.remove_permission(
            Label=IOA_POLICY_NAME,
        )
        print("Verify public permission removed")
        result = self.client.get_topic_attributes(TopicArn=self.topic.arn)
        print(result)
        print("Deleting SNS topic")
        result = self.client.delete_topic(TopicArn=self.topic.arn)
        print("SNS topic deleted at", result["ResponseMetadata"]["HTTPHeaders"]["date"])


if __name__ == "__main__":
    aws_profile = sys.argv[1]
    print("Using AWS profile", aws_profile)
    botosession = boto3.Session(profile_name=aws_profile)

    print("Setting up for Policy 221 test")
    test = SNSTest(botosession)
    # use this if you didn't clean up sns topic
    # test.topic = botosession.resource('sns').Topic('arn:aws:sns:us-east-1:$$$ACCOUNTID$$$:cspm-ioa-test')
    test.setup()
    time.sleep(SLEEP_SECONDS)

    test.trigger_before()
    time.sleep(SLEEP_SECONDS)

    test.trigger_ioa()
    time.sleep(SLEEP_SECONDS)

    test.trigger_after()
    time.sleep(SLEEP_SECONDS)

    test.cleanup()
    print("Test 221 complete")
