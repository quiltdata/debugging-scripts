import boto3
import json
import os



"""
1. Check current credentials and policies
2. Check if we can write, get, delete a test object in this bucet
3. Check for Bucket/object restrictions
4. Check for IAM restrictions
"""

def get_s3_client():
    return boto3.client("s3")



def get_bucket_policy(bucket):
    response = get_s3_client().get_bucket_policy(Bucket=bucket)
    return response

def get_bucket_policy_status(bucket):
    response = get_s3_client().get_bucket_policy_status(Bucket=bucket)
    return response

def get_bucket_versioning(bucket):
    response = get_s3_client().get_bucket_versioning(Bucket=bucket)
    return response


def get_object_legal_hold(bucket, key, version_id=None):
    if version_id:
        response = get_s3_client().get_object_legal_hold(Bucket=bucket, Key=key, VersionId=version_id)
    else:
        response = get_s3_client().get_object_legal_hold(Bucket=bucket, Key=key)
    return response

def get_object_lock_configuration(bucket):
    response = get_s3_client().get_object_lock_configuration(Bucket=bucket)
    return response


def get_object_retention(bucket, key, version_id=None):
    if version_id:
        response = get_s3_client().get_object_retention(Bucket=bucket, Key=key, VersionId=version_id)
    else:
        response = get_s3_client().get_object_retention(Bucket=bucket, Key=key)
    return response


def put_object():
    pass

def get_object():
    pass

def list_object():
    pass

def delete_object():
    pass


def get_sts_client():
    return boto3.client('sts')

def get_caller_identity():
    return get_sts_client().get_caller_identity()


def get_iam_client():
    return boto3.client('iam')

def get_user(user_name):
    return get_iam_client().get_user(UserName=user_name)

def get_role(role_name):
    return get_iam_client().get_role(RoleName=role_name)

def list_policies_for_user(user_name):
    return get_iam_client().list_attached_user_policies(UserName=user_name)


def list_policies_for_role(role_name):
    return get_iam_client().list_attached_role_policies(RoleName=role_name)



def pretty_json(j):
    return json.dumps(j, indent=4)

def spacer():
    return "------\n\n"

def wait():
    return input("Waiting")

def get_bucket():
    return os.environ.get("S3_BUCKET")

def get_key():
    return os.environ.get("S3_KEY", "tmp/quilt_debug.json")


if __name__ == '__main__':
    bucket = get_bucket()
    key = get_key()
    print(f"BUCKET={bucket}")
    print(f"KEY={key}")
    print(spacer())

    print("Checking current credentials")
    try:
        caller_identity = get_caller_identity()
        caller_arn = caller_identity["Arn"]
        print(caller_arn)
    except Exception as ex:
        print("Exception occurred:", ex)
    print(spacer())
    wait()


    print(f"Getting information about caller")
    user = False
    name = None
    if "user" in caller_arn:
        user = True
        name = caller_arn.split(":user/")[1]
        print("Type=USER")
    elif "role" in caller_arn:
        user = False
        name = caller_arn.split(":role/")[1]
        print("Type=ROLE")
    else:
        print("Looks like the caller is neither a user or a role")
        quit()

    try:
        if user:
            caller_info = get_user(name)
        else:
            caller_info = get_role(name)
        print(caller_info)
    except Exception as ex:
        print("Exception occurred:", ex)
    print(spacer())
    wait()




    print(f"Finding policies attached to {name}")
    if user:
        policies = list_policies_for_user(name)
    else:
        policies = list_policies_for_role(name)
    policies = policies["AttachedPolicies"]
    print(pretty_json(policies))
    print(spacer())
    wait()



    print(f"Inspecting bucket {bucket} policy")
    try:
        response = get_bucket_policy(bucket)
        print(pretty_json(response))
    except Exception as ex:
        print("Exception occurred:", ex)
    print(spacer())
    wait()

    print(f"Inspecting bucket {bucket} policy status")
    try:
        response = get_bucket_policy_status(bucket)
        print(pretty_json(response))
    except Exception as ex:
        print("Exception occurred:", ex)
    print(spacer())
    wait()

    print(f"Inspecting bucket {bucket} versioning")
    try:
        response = get_bucket_versioning(bucket)
        print(pretty_json(response))
    except Exception as ex:
        print("Exception occurred:", ex)
    print(spacer())
    wait()


    print(f"Inspecting bucket {bucket} object lock configuration")
    try:
        response = get_object_lock_configuration(bucket)
        print(pretty_json(response))
    except Exception as ex:
        print("Exception occurred:", ex)
    print(spacer())
    wait()




    print(f"Testing object put, list and delete of object in bucket {bucket}")
    json_bytes = bytes(json.dumps({"test": "json"}).encode('UTF-8'))
    put_key = "tmp/quilt_debug.json"


    print(f"Putting s3://{bucket}/{put_key}")
    try:
        response = get_s3_client().put_object(Body=json_bytes, Bucket=bucket, Key=put_key)
        print(pretty_json(response))
    except Exception as ex:
        print("Exception occurred", ex)
    print(spacer())



    print(f"Getting s3://{bucket}/{key}")
    try:
        response = get_s3_client().get_object(Bucket=bucket, Key=key)
        out = json.loads(response["Body"].read().decode("utf-8"))
        print(response)
        print(out)
    except Exception as ex:
        print("Exception occurred", ex)
    print(spacer())



    print(f"Deleting s3://{bucket}/{key}")
    try:
        response = get_s3_client().delete_object(Bucket=bucket, Key=key)
        print(pretty_json(response))
    except Exception as ex:
        print("Exception occurred", ex)
    print(spacer())
    wait()



    print(f"Inspecting legal hold for object s3://{bucket}/{key}")
    try:
        response = get_object_legal_hold(bucket, key)
        print(pretty_json(response))
    except Exception as ex:
        print("Exception occurred:", ex)
    print(spacer())
    wait()



    print(f"Inspecting object retention for object s3://{bucket}/{key}")
    try:
        response = get_object_retention(bucket, key)
        print(pretty_json(response))
    except Exception as ex:
        print("Exception occurred:", ex)
    print(spacer())
