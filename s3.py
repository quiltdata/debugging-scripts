import boto3
import json
import quilt3




def get_s3_client(use_quilt3_botocore_session=True):
    if use_quilt3_botocore_session:
        return boto3.Session(botocore_session=quilt3.session.create_botocore_session()).client("s3")
    else:
        return boto3.client("s3")




def get_bucket_policy(s3_client, bucket):
    response = s3_client.get_bucket_policy(Bucket=bucket)
    return response




def get_bucket_policy_status(s3_client, bucket):
    response = s3_client.get_bucket_policy_status(Bucket=bucket)
    return response



def get_bucket_versioning(s3_client, bucket):
    response = s3_client.get_bucket_versioning(Bucket=bucket)
    return response



def get_object_legal_hold(s3_client, bucket, key, version_id=None):
    if version_id:
        response = s3_client.get_object_legal_hold(Bucket=bucket, Key=key, VersionId=version_id)
    else:
        response = s3_client.get_object_legal_hold(Bucket=bucket, Key=key)
    return response



def get_object_lock_configuration(s3_client, bucket):
    response = s3_client.get_object_lock_configuration(Bucket=bucket)
    return response


def get_object_retention(s3_client, bucket, key, version_id=None):
    if version_id:
        response = s3_client.get_object_retention(Bucket=bucket, Key=key, VersionId=version_id)
    else:
        response = s3_client.get_object_retention(Bucket=bucket, Key=key)
    return response



test_json_bytes = bytes(json.dumps({"test": "json"}).encode('UTF-8'))
def put_object(s3_client, bucket, key, object_bytes=test_json_bytes):
    response = s3_client.put_object(Body=object_bytes, Bucket=bucket, Key=key)
    return response



def get_object(s3_client, bucket, key, version_id=None):
    if version_id:
        response = s3_client.get_object(Bucket=bucket, Key=key, VersionId=version_id)
    else:
        response = s3_client.get_object(Bucket=bucket, Key=key)

    return response


def get_object_as_string(s3_client, bucket, key, version_id=None):
    response = get_object(s3_client, bucket, key, version_id=version_id)
    return response["Body"].read().decode("utf-8")


def get_json(s3_client, bucket, key, version_id=None):
    response = get_object(s3_client, bucket, key, version_id=version_id)
    j = json.loads(response["Body"].read().decode("utf-8"))
    return j, response



def delete_object(s3_client, bucket, key):
    response = s3_client.delete_object(Bucket=bucket, Key=key)
    return response


# Blocks until all/limit objects have been listed
def list_keyspace(s3_client, bucket, prefix=None, limit=None):
    objects = []

    if prefix is None:
        response = s3_client.list_objects_v2(Bucket=bucket)
    else:
        response = s3_client.list_objects_v2(Bucket=bucket, Prefix=prefix)

    if response["KeyCount"] == 0:
        return []

    objects += response["Contents"]
    if limit is not None:
        if len(objects) >= limit:
            return objects[:limit]

    while response["IsTruncated"]:
        continuation_token = response["ContinuationToken"]

        if prefix is None:
            response = s3_client.list_objects_v2(
                    Bucket=bucket,
                    ContinuationToken=continuation_token
            )
        else:
            response = s3_client.list_objects_v2(
                    Bucket=bucket,
                    Prefix=prefix,
                    ContinuationToken=continuation_token,
            )
        if response["KeyCount"] > 0:
            objects += response["Contents"]
            if limit is not None:
                if len(objects) >= limit:
                    return objects[:limit]
    # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html#S3.Client.list_objects_v2
    return objects

def empty_keyspace(s3_client, bucket, s3_prefix):
    keys = [o["Key"] for o in list_keyspace(s3_client, bucket, prefix=s3_prefix)]
    for key in keys:
        delete_object(s3_client, bucket, key)

