#!/usr/bin/env python3
import boto3, sys, time
from utils import AWS_RESOURCE_TAGS

"""

Policy 225 - RDS database snapshot modified to share publicly

Pattern: Creates RDS instance and snapshot, describes instances and snapshots, then modifies snapshot attribute to share publicly.

Policy 251 - RDS database manually deleted by IAM user

Pattern: Deletes RDS database instance.

"""

# Authenticaion and Service Setup
RDS = boto3.Session(profile_name=sys.argv[1]).client("rds")
# Database Variables
DB_NAME = "test-mysql-instance-ioa-225-251"
DB_SNAPSHOT_NAME = DB_NAME + "-snapshot1"
DB_NAME_2 = "test-mysql-instance-ioa-225-251-2"
DB_SNAPSHOT_NAME_2 = DB_NAME_2 + "-snapshot1"


def describe_instances(db_name):
    while True:
        rds_describe_instances = RDS.describe_db_instances(DBInstanceIdentifier=db_name)
        if rds_describe_instances:
            print("   describe-db-instances Successfully Ran")
            for r in rds_describe_instances["DBInstances"]:
                if str(r["DBInstanceStatus"]) == "available":
                    print("    ***Instance Available***\n")
                    return
                else:
                    print(
                        "    ***Timeout 30s for Instance to Become Available***  Status: "
                        + str(r["DBInstanceStatus"])
                        + "\n"
                    )
                    time.sleep(30)


def describe_snapshots(db_name, db_snapshot_name):
    while True:
        rds_describe_snapshots = RDS.describe_db_snapshots(
            DBInstanceIdentifier=db_name, DBSnapshotIdentifier=db_snapshot_name
        )
        if rds_describe_snapshots:
            print("   describe-db-snapshots Successfully Ran")
            for r in rds_describe_snapshots["DBSnapshots"]:
                if str(r["Status"]) == "available":
                    print("    ***Snapshot Completed***\n")
                    return
                else:
                    print(
                        "    ***Timeout 30s for Snapshot to Complete***  Status: "
                        + str(r["Status"])
                        + "\n"
                    )
                    time.sleep(30)


def describe_snapshot_attributes(db_snapshot_name):
    rds_describe_snapshot_attributes = RDS.describe_db_snapshot_attributes(
        DBSnapshotIdentifier=db_snapshot_name
    )
    if rds_describe_snapshot_attributes:
        print("   describe-db-snapshot-attributes Successfully Ran\n")


def create_instance(db_name):
    rds_create = RDS.create_db_instance(
        DBInstanceIdentifier=db_name,
        DBInstanceClass="db.t3.micro",
        Engine="mysql",
        MasterUsername="admin",
        MasterUserPassword="secret99",
        AllocatedStorage=20,
        BackupRetentionPeriod=0,
        Tags=AWS_RESOURCE_TAGS,
    )
    if rds_create:
        print(
            "   create-db-instances Successfully Ran\n    Created Instance: "
            + db_name
            + "\n"
        )

    print("    ***Time out 120s for Instance Creation to Complete***\n")
    time.sleep(120)


def create_snapshot(db_name, db_snapshot_name):
    rds_snapshot_create = RDS.create_db_snapshot(
        DBSnapshotIdentifier=db_snapshot_name,
        DBInstanceIdentifier=db_name,
        Tags=AWS_RESOURCE_TAGS,
    )
    if rds_snapshot_create:
        print(
            "   create-db-snapshot Successfully Ran\n    Created Snapshot: "
            + db_snapshot_name
            + "\n"
        )

    print("     ***Time out 120s for Snapshot Creation to Complete***\n")
    time.sleep(120)


def modify_snapshot_attributes(db_snapshot_name):
    modify_snapshot_attributes = RDS.modify_db_snapshot_attribute(
        DBSnapshotIdentifier=db_snapshot_name,
        AttributeName="restore",
        ValuesToAdd=[
            "all",
        ],
    )
    if modify_snapshot_attributes:
        print("   modify-snapshot-attributes Successfully Ran\n")


def delete_instance(db_name):
    rds_delete = RDS.delete_db_instance(
        DBInstanceIdentifier=db_name,
        SkipFinalSnapshot=True,
        DeleteAutomatedBackups=True,
    )
    if rds_delete:
        print(
            "   delete-db-instance Successfully Ran\n    Deleted DB Instance: "
            + db_name
            + "\n"
        )


def delete_snapshot(db_snapshot_name):
    rds_snapshot_delete = RDS.delete_db_snapshot(DBSnapshotIdentifier=db_snapshot_name)
    if rds_snapshot_delete:
        print(
            "   delete-db-snapshot Successfully Ran\n    Deleted Snapshot: "
            + db_snapshot_name
            + "\n"
        )


def main():
    # Test Case Prep
    print("\n\nSetting Up for Test Case\n")
    create_instance(DB_NAME)
    describe_instances(DB_NAME)
    create_snapshot(DB_NAME, DB_SNAPSHOT_NAME)
    # Before Query
    print("\n\nRunning Policy 225 Before Conditions\n")
    describe_instances(DB_NAME)
    describe_snapshots(DB_NAME, DB_SNAPSHOT_NAME)
    describe_snapshot_attributes(DB_SNAPSHOT_NAME)
    # Pattern Query
    print("\n\nRunning Policy 225 Pattern Conditions\n")
    modify_snapshot_attributes(DB_SNAPSHOT_NAME)
    # After Query
    print("\n\nRunning Policy 225 After Conditions\n")
    create_instance(DB_NAME_2)
    describe_instances(DB_NAME_2)
    create_snapshot(DB_NAME_2, DB_SNAPSHOT_NAME_2)
    # Clean Up
    print("\n\nCleaning Up\n")
    describe_snapshots(DB_NAME_2, DB_SNAPSHOT_NAME_2)
    delete_snapshot(DB_SNAPSHOT_NAME)
    delete_snapshot(DB_SNAPSHOT_NAME_2)
    print("\n\nRunning Policy 251 Pattern Conditions\n")
    delete_instance(DB_NAME)
    delete_instance(DB_NAME_2)


if __name__ == "__main__":
    main()
