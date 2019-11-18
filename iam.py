import boto3
import quilt3


def get_iam_client(use_quilt3_botocore_session=False):
    if use_quilt3_botocore_session:
        return boto3.Session(botocore_session=quilt3.session.create_botocore_session()).client("iam")
    else:
        return boto3.client('iam')



def get_user_info(iam_client, user_name):
    return iam_client.get_user(UserName=user_name)

def get_role_info(iam_client, role_name):
    return iam_client.get_role(RoleName=role_name)

def list_policies_for_user(iam_client, user_name):
    return iam_client.list_attached_user_policies(UserName=user_name)


def list_policies_for_role(iam_client, role_name):
    return iam_client.list_attached_role_policies(RoleName=role_name)


def extract_user_from_arn(arn):
    return arn.split(":user/")[1]


def extract_assumed_role_from_arn(arn):
    role_and_session = arn.split(":assumer-role/")[1]
    role, session = role_and_session.split("/")
    return role





