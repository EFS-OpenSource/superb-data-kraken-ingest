#  ****************************************************************************
#  @copyright 2023 e:fs TechHub GmbH (sdk@efs-techhub.com)
#
#  @license Apache v2.0
#  
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#  
#      http://www.apache.org/licenses/LICENSE-2.0
#  
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
#  ****************************************************************************
# -*- encoding: utf-8 -*-
import argparse
import base64
import json
import logging
import os
import re

from authentication import authentication
from metadata import metadata
from storage.azure import azure_storageaccess as azure
from storage.s3 import s3_storageaccess as s3
from storage.storageaccess import StorageAccess

ENV_STORAGE_TYPE = 'STORAGE_TYPE'


def _get_argument(arg_value: str, arg_name: str, env_var_name: str):
    """
    returns arg_value or value of fallback-environment-variable if arg_value is None, raises exception if fallback fails
    :param arg_value: the argument-value as passed by cli
    :param arg_name: the argument-name expected
    :param env_var_name: the name of the fallback-environment-variable
    :return: argument-value or value of fallback-environment-variable
    """
    if not arg_value:
        if env_var_name not in os.environ:
            raise Exception(
                f'no keyname for azure event hub found - either provide via "--{arg_name}" or provide environment-variable "{env_var_name}"')
        else:
            env_var_value = os.environ[env_var_name]
            # check if environment-variable-value is stored in quotas
            regex = r"\"(.*)\""
            if re.match(regex, env_var_value):
                for match in list(re.finditer(regex, env_var_value, re.MULTILINE)):
                    return match.group(1)

            return env_var_value
    return arg_value


def _extract_notification(origin):
    """
    extracts decoded data-body of argo-sensor-payload
    :param origin: as provided by argo-sensor
    :return: actual payload of notification
    """
    payload_json = json.loads(origin)
    data = payload_json['data']  # base64-encoded
    decoded_data = base64.b64decode(data).decode("utf-8").replace('\n', '')
    data_json = json.loads(decoded_data)
    body = data_json['body']  # base64-encoded
    decoded_body = base64.b64decode(body).decode("utf-8").replace('\n', '')
    return json.loads(decoded_body)


def _get_storage_access() -> StorageAccess:
    storage_type = azure.TYPE
    if ENV_STORAGE_TYPE in os.environ:
        storage_type = os.getenv(ENV_STORAGE_TYPE)
    if storage_type == s3.TYPE:
        return s3.S3StorageAccess()
    if storage_type == azure.TYPE:
        return azure.AzureStorageAccess()
    raise ValueError(f'unknown storage-type {storage_type}')


if __name__ == '__main__':
    FORMAT = '%(asctime)s %(levelname)s - %(message)s'
    logging.basicConfig(format=FORMAT, level=logging.INFO)

    parser = argparse.ArgumentParser(description='Script that create a basic set of metadata if required for a Space', )

    parser.add_argument('--payload', '-p', dest='payload', type=str, required=True)
    parser.add_argument('--client-id', '-ci', dest='client', type=str, required=False)
    parser.add_argument('--client-secret', '-c', dest='secret', type=str, required=False)

    args = parser.parse_args()
    if not args.payload:
        raise Exception('no payload provided')

    payload = _extract_notification(args.payload)
    logging.info(payload)

    client_id = _get_argument(args.client, 'client-id', 'CLIENT_ID')
    client_secret = _get_argument(args.secret, 'client-secret', 'CLIENT_SECRET')
    if not client_id or not client_secret:
        raise Exception('client-id and client-secret must be provided')

    # Extract organization, space and root_dir from the payload
    organization = payload['accountName']
    space = payload['storageName']
    container = payload['containerName']
    root_dir = payload['rootDir']
    username = payload['userName']

    # Request an access_token
    logging.info("Fetching access_token...")
    access_token = authentication.get_access_token(username, client_id, client_secret)
    logging.info("Fetching access_token...Done!")

    # CUSTOM CODE
    logging.info("Creating metadata...")
    storage_access = _get_storage_access()
    metadata.create_basic_metadata(storage_access, access_token, organization, space, container, root_dir)
    logging.info("Creating metadata...Done")
