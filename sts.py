import boto3
import quilt3

def get_sts_client(use_quilt3_botocore_session=True):
    if use_quilt3_botocore_session:
        return boto3.Session(botocore_session=quilt3.session.create_botocore_session()).client("sts")
    else:
        return boto3.client('sts')



def get_caller_identity(sts_client):
    return sts_client.get_caller_identity()

