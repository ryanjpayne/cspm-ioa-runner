#!/usr/bin/env python3
import boto3, sys, time, json
from botocore.exceptions import ClientError
from utils import AWS_RESOURCE_TAGS

"""

Policy 223 - EC2 AMI shared publicly

Pattern: Creates EC2 instance, describes instances and images, copies image, then modifies image attribute to allow public launch permission.

"""


REGION = "us-east-1"

aws_profile = sys.argv[1]
client = boto3.Session(profile_name=aws_profile).client("ec2", region_name=REGION)
images = client.describe_images(
    Owners=["amazon"], Filters=[{"Name": "name", "Values": ["amzn2-ami-hvm*"]}]
)
IMAGEAMI = images["Images"][0]["ImageId"]

TAGS = AWS_RESOURCE_TAGS


def set_up():
    create_image = client.run_instances(
        ImageId=IMAGEAMI,
        InstanceType="t3.micro",
        MinCount=1,
        MaxCount=1,
        TagSpecifications=[{"ResourceType": "instance", "Tags": TAGS}],
    )
    print(f"CREATE OUTPUT: {create_image}")
    instance_id = create_image["Instances"][0]["InstanceId"]
    time.sleep(30)
    return instance_id


def trigger_223_before(instance):
    print("Running 223 before")
    describe_instances = client.describe_instances()
    describe_instance_attribute = client.describe_instance_attribute(
        Attribute="instanceType", InstanceId=instance
    )
    describe_images = client.describe_images(ImageIds=[IMAGEAMI])

    copy_image = client.copy_image(
        Name="223IOA",
        SourceImageId=IMAGEAMI,
        SourceRegion=REGION,
    )

    copied_image_id = copy_image["ImageId"]
    print("Waiting for image to become available...")
    status = client.describe_images(
        Filters=[
            {"Name": "image-id", "Values": [copied_image_id]},
            {"Name": "state", "Values": ["available"]},
        ]
    )
    while len(status["Images"]) < 1:
        time.sleep(30)
        status = client.describe_images(
            Filters=[
                {"Name": "image-id", "Values": [copied_image_id]},
                {"Name": "state", "Values": ["available"]},
            ]
        )
        print(status)

    return copied_image_id


def trigger_223_pattern(instance, copied_image_id):
    try:
        modify_image_attribute = client.modify_image_attribute(
            ImageId=copied_image_id,
            LaunchPermission={
                "Add": [
                    {"Group": "all"},
                ],
            },
        )
    except Exception as e:
        print(e)
        clean_up(instance, copied_image_id)


def trigger_223_after(copied_image):
    print("RUNNING AFTER")
    run_instances = client.run_instances(
        ImageId=copied_image,
        InstanceType="t3.micro",
        MaxCount=1,
        MinCount=1,
        TagSpecifications=[{"ResourceType": "instance", "Tags": TAGS}],
    )
    image_id = run_instances["Instances"][0]["InstanceId"]
    return image_id


def clean_up(instances, copied_image_id):
    print("CLEANING UP")
    if type(instances) is str:
        instances = list(instances.split(","))
    delete_instances = client.terminate_instances(InstanceIds=instances)
    delete_image = client.deregister_image(ImageId=copied_image_id)
    print(delete_image, delete_instances)


def main():
    # Creating Instance List For Clean Up
    instances = list()

    # Prep
    instance_id = set_up()

    # Before Condition
    copied_image_id = trigger_223_before(instance_id)

    # Pattern Condition
    trigger_223_pattern(copied_image_id, copied_image_id)

    # After Condition
    instance_id2 = trigger_223_after(copied_image_id)

    # Clean Up
    instances.append(instance_id)
    instances.append(instance_id2)
    clean_up(instances, copied_image_id)


if __name__ == "__main__":
    main()
