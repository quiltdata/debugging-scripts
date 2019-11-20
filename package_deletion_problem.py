import json
import random
import sys
import traceback
import uuid

import quilt3

import s3
import sts
import iam


import pandas as pd






class FunctionReporter:
    def __init__(self, name, additional_detail=None):
        self.name = name
        print(f'About to run "{self.name}"')
        if additional_detail:
            print(f"Preflight Details: {additional_detail}")


    def succeeded(self, output, additional_detail=None):
        print(f'"{self.name}" was successful')
        if additional_detail:
            print(f"Success Details: {additional_detail}")
        if output is not None:
            if isinstance(output, dict):
                pretty_print_json(output)
            else:
                print(output)
        print_divider()


    def failed(self, exception, additional_detail=None):
        print(f'ERROR. "{self.name}" failed with exception: {exception}')
        if additional_detail:
            print(f"Failure Details: {additional_detail}")
        print_divider()






def print_divider():
    print("-----")


def pretty_print_json(j):
    print(json.dumps(j, indent=4, default=str))

def header(name):
    print("\n")
    print("###########################################################################################################")
    print(f"#### {name}")
    print("###########################################################################################################")
    print()




def get_info_about_bucket(bucket):
    s3_client = s3.get_s3_client(use_quilt3_botocore_session=False)

    fn_info = FunctionReporter(f"Inspecting bucket {bucket} policy")
    try:
        response = s3.get_bucket_policy(s3_client, bucket)
        fn_info.succeeded(response)
    except Exception as ex:
        fn_info.failed(ex)


    fn_info = FunctionReporter(f"Inspecting bucket {bucket} policy status")
    try:
        response = s3.get_bucket_policy_status(s3_client, bucket)
        fn_info.succeeded(response)
    except Exception as ex:
        fn_info.failed(ex)


    fn_info = FunctionReporter(f"Inspecting bucket {bucket} versioning")
    try:
        response = s3.get_bucket_versioning(s3_client, bucket)
        fn_info.succeeded(response)
    except Exception as ex:
        fn_info.failed(ex)



    fn_info = FunctionReporter(f"Inspecting bucket {bucket} object lock configuration")
    try:
        response = s3.get_object_lock_configuration(s3_client, bucket)
        fn_info.succeeded(response)
    except Exception as ex:
        fn_info.failed(ex)




def get_info_about_key(bucket, key):
    s3_client = s3.get_s3_client(use_quilt3_botocore_session=False)

    fn_info = FunctionReporter(f"Inspecting legal hold for object s3://{bucket}/{key}")
    try:
        response = s3.get_object_legal_hold(s3_client, bucket, key)
        fn_info.succeeded(response)
    except Exception as ex:
        fn_info.failed(ex)


    fn_info = FunctionReporter(f"Inspecting object retention for object s3://{bucket}/{key}")
    try:
        response = s3.get_object_retention(s3_client, bucket, key)
        fn_info.succeeded(response)
    except Exception as ex:
        fn_info.failed(ex)



def generate_new_package_version(package_name, registry_name, push_dest):
    fn_info = FunctionReporter(f"Creating package '{package_name}' in registry {registry_name}")
    try:
        pkg = quilt3.Package()
        pkg.set(f"test-{uuid.uuid4()}", pd.DataFrame(range(random.randint(0, 100_000))))
        pkg.push(package_name, registry=registry_name, dest=push_dest)
        fn_info.succeeded(output=None)
    except Exception as ex:
        traceback.print_stack()
        fn_info.failed(ex)



def cleanup():
    raise NotImplementedError


def check_normal_creds_can_create_and_delete_random_file(bucket, key):
    s3_client = s3.get_s3_client(use_quilt3_botocore_session=False)


    put_fn_info = FunctionReporter(f"Putting test file in s3://{bucket}/{key}")
    try:
        put_response = s3.put_object(s3_client, bucket, key)
        put_fn_info.succeeded(put_response)
    except Exception as ex:
        put_fn_info.failed(ex)


    del_fn_info = FunctionReporter(f"Deleting test file in s3://{bucket}/{key}")
    try:
        delete_response = s3.delete_object(s3_client, bucket, key)
        del_fn_info.succeeded(delete_response)
        return True
    except Exception as ex:
        del_fn_info.failed(ex)
        return False


def get_info_about_normal_creds():
    return get_info_about_creds(use_quilt3_botocore_session=False)

def get_info_about_quilt3_creds():
    return get_info_about_creds(use_quilt3_botocore_session=True)


def get_info_about_creds(use_quilt3_botocore_session=False):
    """
    NOTE: use_quilt3_botocore_session indicates how the STS client will be created (which is then used to determine
          which user/role is being used via sts.get_caller_identity()). The IAM client used to explore the details of
          the user/role will always use the default credential provider chain because the Quilt3 given role is extremely
          unlikely to have adequate IAM permissions
    """
    cred_type = "quilt3_botocore_session" if use_quilt3_botocore_session else "default_provider_chain"
    print(f"Getting info about {cred_type} credentials")

    iam_client = iam.get_iam_client(use_quilt3_botocore_session=False)
    sts_client = sts.get_sts_client(use_quilt3_botocore_session=use_quilt3_botocore_session)

    fn_info = FunctionReporter(f"Getting caller identity using {cred_type} credentials")
    try:
        caller_identity = sts.get_caller_identity(sts_client)
        fn_info.succeeded(caller_identity)
    except Exception as ex:
        fn_info.failed(ex, additional_detail="Unable to report further IAM details")
        return

    arn = caller_identity["Arn"]  # user, assumed-role or federated-user


    if ":user/" in arn:
        fn_info = FunctionReporter(f"Extracting username from {arn}")
        user = iam.extract_user_from_arn(arn)
        fn_info.succeeded(user)

        fn_info = FunctionReporter(f"Getting user info")
        try:
            user_info = iam.get_user_info(iam_client, user)
            fn_info.succeeded(user_info)
        except Exception as ex:
            fn_info.failed(ex)

        fn_info = FunctionReporter(f"Getting policies for user")
        try:
            policies_for_user = iam.list_policies_for_user(iam_client, user)
            fn_info.succeeded(policies_for_user)
        except Exception as ex:
            fn_info.failed(ex)

    elif ":assumed-role/" in arn:
        fn_info = FunctionReporter(f"Extracting assumed role from {arn}")
        assumed_role = iam.extract_assumed_role_from_arn(arn)
        fn_info.succeeded(assumed_role)

        fn_info = FunctionReporter(f"Getting role info")
        try:
            role_info = iam.extract_assumed_role_from_arn(arn)
            fn_info.succeeded(role_info)
        except Exception as ex:
            fn_info.failed(ex)

        fn_info = FunctionReporter(f"Getting policies for role")
        try:
            policies_for_role = iam.list_policies_for_role(iam_client, assumed_role)
            fn_info.succeeded(policies_for_role)
        except Exception as ex:
            fn_info.failed(ex)

    elif ":federated-user/" in arn:
        raise NotImplementedError("Did not implement support for federated-user. Fingers crossed that won't matter")
    else:
        raise ValueError("ARN is not of a type that we are familiar with. Unable to retrieve further IAM info")




def repro(package_name, registry_name, push_dest):

    print("Attempting to reproduce 'unable to delete package' issue")

    generate_new_package_version(package_name, registry_name, push_dest)

    try:
        print("Delete package starting")
        quilt3.delete_package(package_name, registry_name)
        print("Deleted package without any exceptions - COULD NOT REPRO")
    except Exception as ex:
        print("Exception occurred during delete package:", ex)








def check_can_delete_manifest(s3_client, package_name, registry_name, push_dest):
    print("Attempting to delete package manifest file directly")

    generate_new_package_version(package_name, registry_name, push_dest)

    manifest_pointer_s3_key = f".quilt/named_packages/{package_name}/latest"
    manifest_pointer_s3_bucket = registry_name.lstrip("s3://").rstrip("/")

    fn_info = FunctionReporter(f"Deleting manifest file s3://{manifest_pointer_s3_bucket}/{manifest_pointer_s3_key}")
    try:
        delete_response = s3.delete_object(s3_client, manifest_pointer_s3_bucket, manifest_pointer_s3_key)
        fn_info.succeeded(delete_response)
        return True
    except Exception as ex:
        fn_info.failed(ex)
        return False






def main(package_name="quilt-debug/test", bucket="armand-staging-t4"):
    """
    Debugging process:

        1. Using normal boto3 credentials, see if there are any restrictions on the bucket/keys in the bucket (legal
           hold, object lock, etc)

        2. Using normal boto3 credentials, confirm that we can delete some object from the bucket

        3. Record information about the normal boto3 credentials

        4. Reproduce the bug using quilt3 library directly

        5. Using normal boto3 credentials, confirm that we can delete the manifest objects (is problem key-specific?).
           Currently this only checks if the pointer can be deleted. For completeness this should also check if the
           underlying manifests files can be deleted

        6. Using s3_client from data_transfer.get_s3_client(), see if we can delete the manifest objects (is problem a
           bug in delete logic or pure permissions)

        7. Using session.get_botocore_session, see if we can delete the manifest objects (is the problem a bug in the
           data_transfer.get_s3_client logic?)

        8. We expect that the above problem will fail indicating that the problem originates in the permissions
           retrieved from session.get_botocore_session. Record information about the permissions.
    """
    registry_name = f"s3://{bucket}"
    push_dest = f"{registry_name}/quilt-tmp"
    manifest_pointer_s3_key = f"{registry_name}./quilt/named_packages/{package_name}/latest"
    test_file_s3_key = "quilt-debug-tmp/tmpfile"

    header("Get bucket info (policy, object lock, etc)")
    get_info_about_bucket(bucket)



    header("Get bucket + key info (legal hold, object retention). (key = 'latest' manifest pointer) ")
    generate_new_package_version(package_name, registry_name, push_dest)
    get_info_about_key(bucket, manifest_pointer_s3_key)


    header("Checking if boto3 with default cred provider chain can create and delete a file on s3")
    normal_creds_can_delete = check_normal_creds_can_create_and_delete_random_file(bucket=bucket, key=test_file_s3_key)
    print("Normal creds can delete test file?", normal_creds_can_delete)

    header("Getting info about role/user given by default cred provider chain")
    get_info_about_normal_creds()

    header("Trying to reproduce failure during delete package")
    repro(package_name, registry_name, push_dest)


    header("Checking if boto3 with default cred provider chain can delete a manifest")
    normal_creds_can_delete = check_can_delete_manifest(s3.get_s3_client(use_quilt3_botocore_session=False),
                                                        package_name, registry_name, push_dest)
    print("Normal creds can delete 'latest' manifest pointer file?", normal_creds_can_delete)


    header("Checking if s3_client from quilt3.data_transfer.create_s3_client() can delete a manifest")
    quilt3_create_s3_client_can_delete = check_can_delete_manifest(quilt3.data_transfer.create_s3_client(),
                                                                   package_name, registry_name, push_dest)
    print("S3 client from quilt3.data_transfer.create_s3_client() can delete 'latest' manifest pointer file?",
          quilt3_create_s3_client_can_delete)


    header("Checking if s3_client from quilt3.session.create_botocore_session() can delete a manifest")
    quilt3_botocore_session_can_delete = check_can_delete_manifest(s3.get_s3_client(use_quilt3_botocore_session=True),
                                                                   package_name, registry_name, push_dest)
    print("S3 client from quilt3.session.create_botocore_session() can delete 'latest' manifest pointer file?",
          quilt3_botocore_session_can_delete)



    header("Getting IAM info about credentials provided via quilt3.session.create_botocore_session()")
    get_info_about_quilt3_creds()


    header("Trying to clean up any leftover files")
    cleanup()






def safe_main(package_name="quilt-debug/test", bucket="armand-staging-t4"):
    try:
        main(package_name, bucket)
    except Exception as ex:
        traceback.print_stack(file=sys.stdout)
        print("Uncaught exception caused exit from main():", ex)









if __name__ == '__main__':
    safe_main()
