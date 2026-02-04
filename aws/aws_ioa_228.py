#!/usr/bin/env python3
import boto3, json, sys

"""

Policy 228 - GuardDuty monitoring disabled

Pattern: Creates GuardDuty detector, lists and gets detector, then updates detector to disable monitoring and stops monitoring members.

"""
# Authenticaion and Service Setup
GUARDDUTY = boto3.Session(profile_name=sys.argv[1]).client("guardduty")

# print(boto3.client('sts').get_caller_identity().get('Account'))


def create_detector():
    guardduty_create_detector = GUARDDUTY.create_detector(Enable=True)
    if guardduty_create_detector:
        print("   guardduty-create-detector Successfully Ran\n")


def list_detectors():
    guardduty_list_detectors = GUARDDUTY.list_detectors()
    if guardduty_list_detectors:
        print("   guardduty-list-detector Successfully Ran\n")
    global dtid
    for d in guardduty_list_detectors["DetectorIds"]:
        dtid = d


def get_detector():
    guardduty_get_detector = GUARDDUTY.get_detector(DetectorId=dtid)
    if guardduty_get_detector:
        print("   guardduty-get-detectors Successfully Ran\n")


def stop_monitoring_members():
    guardduty_stop_monitoring_members = GUARDDUTY.stop_monitoring_members(
        DetectorId=dtid, AccountIds=["123456789012"]
    )
    if guardduty_stop_monitoring_members:
        print("   guardduty-stop-monitoring-members Successfully Ran\n")


def update_detector():
    guardduty_update_detector = GUARDDUTY.update_detector(
        DetectorId=dtid,
        Enable=False,
    )
    if guardduty_update_detector:
        print("   guardduty-update-detectors Successfully Ran\n")


def delete_detector():
    guardduty_delete_detector = GUARDDUTY.delete_detector(DetectorId=dtid)
    if guardduty_delete_detector:
        print("   guardduty-delete-detectors Successfully Ran\n")


def main():
    # Test Case Prep
    print("\n\nSetting Up for Test Case\n")
    create_detector()
    # Before Query
    print("\n\nRunning Before Conditions\n")
    list_detectors()
    get_detector()
    # Pattern Query
    print("\n\nRunning Pattern Conditions\n")
    update_detector()
    stop_monitoring_members()
    # After / Clean Up
    print("\n\nRunning After Conditions and Cleaning Up\n")
    delete_detector()
    list_detectors()


if __name__ == "__main__":
    main()
