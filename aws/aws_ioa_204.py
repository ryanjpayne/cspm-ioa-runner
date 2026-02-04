#!/usr/bin/env python3
import boto3, sys, time
from botocore.exceptions import ClientError

"""

Policy 204 - Cross-User IAM LoginProfile modification

Pattern: Creates an IAM user with login profile, lists users and password policy, then updates the login profile password.

"""
# User Variables
USER = "cspmtestck204"
PASS = "cspmTEST234@#$"
PASS2 = "cspmTEST234@#$2"

temppol = {
    "MinimumPasswordLength": 12,
    "RequireSymbols": True,
    "RequireNumbers": True,
    "RequireUppercaseCharacters": True,
    "RequireLowercaseCharacters": True,
    "AllowUsersToChangePassword": True,
}

# Instantiating IAM client
IAM = boto3.Session(profile_name=sys.argv[1]).client("iam")


def create_user():
    response = IAM.create_user(UserName=USER)
    print(f"Create User Output:\n {response}")


def create_login_profile():
    response = IAM.create_login_profile(UserName=USER, Password=PASS)
    print(f"Create Login Profile Output:\n {response}")
    # 30 second sleep time to allow the login profile to be created before being updated
    time.sleep(40)
    print("%s login profile already exists. Skipping..." % (USER))


def list_users():
    response = IAM.list_users(PathPrefix="/")
    print(f"List Users Output:\n {response}")


def get_password_policy():
    created_pw_pol = False

    try:
        response = IAM.get_account_password_policy()
    except ClientError as e:
        response = IAM.update_account_password_policy(**temppol)
        print(f"Create Password Policy Output:\n {response} \n")
        created_pw_pol = True
        response = IAM.get_account_password_policy()

    print(f"Get Password Policy Output:\n {response}")

    return created_pw_pol


def update_login_profile():
    response = IAM.update_login_profile(UserName=USER, Password=PASS2)
    print(f"Update Login Profile Output:\n {response}")


def delete_login_profile():
    response = IAM.delete_login_profile(UserName=USER)
    print(f"Delete Login Profile Output:\n {response}")


def delete_user():
    response = IAM.delete_user(UserName=USER)
    print(f"Delete User Output:\n {response}")


def delete_pw_policy():
    try:
        response = IAM.delete_account_password_policy()
        print(f"Delete temporary password policy:\n {response}")
    except ClientError as e:
        pass


def main():
    # Pre-Test Prep
    print("\n\nRunning Policy 204 Prep\n")
    create_user()
    create_login_profile()

    # Enumerate Users
    print("\n\nRunning Policy 204 Before Conditions\n")
    list_users()

    # Enumerate Account Password Policy
    time.sleep(5)
    print("\n\nRunning Policy 204 Before Conditions\n")
    created_policy = get_password_policy()

    # Create User
    time.sleep(5)
    print("\n\nRunning Policy 204 Pattern Conditions\n")
    update_login_profile()

    # console_login_confirmation = input(
    #    f"\n\n\nPlease Perform Console Login:\nUser Name: {USER}\nPassword={PASS2}\n\nPress any key to continue after performing console login"
    # )

    # Perform Clean Up
    time.sleep(5)
    print("\n\nRunning Policy 204 Clean Up\n")

    # User profile must be deleted before the user can be deleted
    delete_login_profile()
    delete_user()

    if created_policy:
        delete_pw_policy()


if __name__ == "__main__":
    main()
