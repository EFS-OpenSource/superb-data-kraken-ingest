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
import os.path
import re
import urllib
import uuid

import jwt
import requests

from ingest.ingeststatus import IngestStatus
from storage.azure import azure_storageaccess as azure
from storage.s3 import s3_storageaccess as s3
from storage.storageaccess import StorageAccess

ENV_STORAGE_TYPE = 'STORAGE_TYPE'


def get_service_account_access_token(token_uri: str, client_id: str, client_secret: str):
    """
    Generates OAuth-Token for the service account
    :param token_uri: token-uri
    :param client_id: client-id of confidential client
    :param client_secret: client-secret of confidential client
    :return: expires-in and access-token
    """

    logger.info("getting access-token")

    payload = {
        'grant_type': 'client_credentials',
        'client_id': client_id,
        'client_secret': client_secret
    }

    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }

    response = requests.post(token_uri, headers=headers, data=payload)
    response.raise_for_status()

    logger.info("got service account access-token")
    response_json = response.json()

    return response_json['expires_in'], response_json["access_token"]


def get_user_context_token(token_uri: str, requested_subject: str, original_client_id: str, original_client_secret: str,
                           original_access_token: str):
    """
    Generates OAuth-Token for the given user from the service account access token via token-exchange
    :param requested_subject:
    :param original_client_id:
    :param original_client_secret:
    :param original_access_token:
    :return: expires-in and access-token
    """

    logger.info("exchanging service-account access-token for user access-token")

    payload = {
        'grant_type': 'urn:ietf:params:oauth:grant-type:token-exchange',
        'client_id': original_client_id,
        'client_secret': original_client_secret,
        'subject_token': original_access_token,
        'requested_token_type': 'urn:ietf:params:oauth:token-type:access_token',
        'requested_subject': requested_subject
    }

    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }

    response = requests.post(token_uri, headers=headers, data=urllib.parse.urlencode(payload))
    response.raise_for_status()

    logger.info("got access-token in user context")
    response_json = response.json()

    return response_json['expires_in'], response_json["access_token"]


def extract_notification(origin):
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


def get_payload(payload: str):
    """
    Gets the payload - either directly or file if payload starts with '@'
    :param payload: payload-value
    :return: payload
    """
    if payload.startswith('@'):
        with open(payload.replace('@', ''), "r") as f:
            return f.read()
    return payload


def index(storage_access: StorageAccess, access_token: str, payload: dict) -> str:
    # Extract organization, space and root_dir from the payload
    organization = payload['accountName']
    space = payload['storageName']
    root_dir = payload['rootDir'].rstrip('/')

    dataset = storage_access.get_dataset(organization, space, root_dir, access_token)
    with open(dataset.meta_json, 'r') as f:
        data = f.read().encode('utf-8')

    # dataset might have ingest.json -> cleanup
    docid = str(uuid.uuid1())
    index_dto = {
        "docid": docid,
        "massdata": [obj.to_dict() for obj in dataset.massdata],
        "metadata": json.loads(data),
        "organization": organization,
        "space": space,
        "rootdir": root_dir
    }

    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }

    if dataset.ingest_state is not None:
        ingest_status = IngestStatus.load_from_json(dataset.ingest_state)
        if ingest_status.docid is not None:
            index_dto['docid'] = ingest_status.docid

    if index_dto['docid'] != docid:  # index is read from ingest.json -> update
        url = f'{os.environ["INDEXER_URL"]}/metadata/v1.0/index?organization={organization}&space={space}&docid={index_dto["docid"]}'
        response = requests.put(url, headers=headers, data=json.dumps(index_dto))
    else:  # create
        url = f'{os.environ["INDEXER_URL"]}/metadata/v1.0/index'
        response = requests.post(url, headers=headers, data=json.dumps(index_dto))

    response.raise_for_status()

    logger.info('dataset indexed!')
    return index_dto['docid']


def get_env(env_var_name: str):
    """
    returns value of environment-variable (either <env_var_name> or <organization>.<env_var_name>
    :param env_var_name: the name of the environment-variable
    :return: value of environment-variable
    """
    if env_var_name not in os.environ:
        raise Exception(f'no environment-variable found - either provide "{env_var_name}"')

    env_var_value = os.environ[env_var_name]
    # check if environment-variable-value is stored in quotas
    regex = r"\"(.*)\""
    if re.match(regex, env_var_value):
        for match in list(re.finditer(regex, env_var_value, re.MULTILINE)):
            return match.group(1)

    return env_var_value


def get_user(payload) -> str:
    organization = payload['accountName']
    env_var_name = 'USERNAME'
    long_env_var_name = f'{organization}.{env_var_name}'.upper()
    if env_var_name not in os.environ and long_env_var_name not in os.environ:
        return payload['userName']
    if long_env_var_name in os.environ:
        return os.environ[long_env_var_name]
    return os.environ[env_var_name]


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
    logging.basicConfig(format=FORMAT)
    logger = logging.getLogger('metadata_index')
    logger.setLevel(level=logging.INFO)

    parser = argparse.ArgumentParser(
        description='Script that analyses the Excels and stores the result in elasticsearch', )

    # Parameters are provided by the Workflow engine
    parser.add_argument('--payload', '-p', dest='payload', type=str, required=True)

    args = parser.parse_args()
    if not args.payload:
        raise Exception('no payload provided')

    origin = get_payload(args.payload)
    payload = extract_notification(origin)

    organization = payload['accountName']

    client_id = get_env('CLIENT_ID')
    client_secret = get_env('CLIENT_SECRET')
    token_uri = get_env('ACCESS_TOKEN_URI')
    if not client_id or not client_secret or not token_uri:
        raise Exception('environment-variables ACCESS_TOKEN_URI, CLIENT_ID and CLIENT_SECRET must be provided')

    logger.info(payload)

    _, auth_header_service_connection = get_service_account_access_token(token_uri, client_id, client_secret)

    user_name = get_user(payload)
    _, auth_header_user_context = get_user_context_token(token_uri, user_name, client_id, client_secret,
                                                         auth_header_service_connection)

    storage_access = _get_storage_access()
    docid = index(storage_access, auth_header_user_context, payload)
    decoded = jwt.decode(auth_header_user_context, options={
        "verify_signature": False
    })
    user_id = decoded['sub']
    space = payload['storageName']
    root_dir = payload['rootDir'].rstrip('/')

    state = IngestStatus(organization=organization, space=space, rootdir=root_dir, userid=user_id, docid=docid)
    storage_access.store_status(auth_header_user_context, organization, space, root_dir, state)
