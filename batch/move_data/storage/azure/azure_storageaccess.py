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
import logging
import os
import re
import time
import urllib.parse
from typing import Union

import requests
from azure.storage.blob import BlobClient, ContainerClient

from storage.storageaccess import StorageAccess, wildcard2regex

logger = logging.getLogger('move_data')

TYPE = 'azure'


class AzureStorageAccess(StorageAccess):
    def __init__(self):
        super().__init__()

    def move_data(self, access_token: str, organization: str, src_space: str, dst_space: str, root_dir: str,
                  blacklist: str, whitelist: str):

        delete_sas = _get_sas_token(os.environ['DELETE_ENDPOINT'], access_token, organization, src_space)
        upload_sas = _get_sas_token(os.environ['UPLOAD_ENDPOINT'], access_token, organization, dst_space)
        read_sas = _get_sas_token(os.environ['READ_ENDPOINT'], access_token, organization, src_space)

        source_container_client = ContainerClient.from_container_url(
            f'{_get_storage_url(organization, src_space)}?{read_sas}')
        my_blobs = source_container_client.list_blobs(name_starts_with=root_dir + "/")
        blob_names = [blob.name for blob in my_blobs]
        filtered = filter_blobs(blob_names, blacklist, whitelist)

        # iterate over all blobs, move only filtered and delete other blobs
        for blob_name in blob_names:
            file_name = urllib.parse.quote(blob_name)

            src_blob_client = BlobClient.from_blob_url(
                f'{_get_storage_url(organization, src_space)}/{file_name}?{delete_sas}')

            if blob_name in filtered:
                dst_blob_client = BlobClient.from_blob_url(
                    f'{_get_storage_url(organization, dst_space)}/{file_name}?{upload_sas}')

                # Copy started
                logger.info(f'moving file from {blob_name} to {blob_name}')
                logger.debug(f'copying file from {src_blob_client.url} to {dst_blob_client.url}')
                dst_blob_client.start_copy_from_url(src_blob_client.url)
                props = dst_blob_client.get_blob_properties()
                while props.copy.status == 'pending':
                    time.sleep(10)
                    logger.debug('copy-job still pending')
                    props = dst_blob_client.get_blob_properties()
            else:
                logger.warning(
                    f'file {file_name} did not pass filter-criteria (blacklist: \'{blacklist}\', whitelist: \'{whitelist}\') - will be deleted!')
            logger.debug(f'deleting file from {src_blob_client.url}')
            src_blob_client.delete_blob()


def _get_storage_url(organization: str, container: str):
    """
    Generates storage-url
    :param organization: The organization-name
    :param container: The container-name
    :return: storage-url
    """
    return f'https://{organization}.blob.core.windows.net/{container}'


def _get_sas_token(endpoint: str, access_token: str, organization: str, container: str):
    if 'api/v1.0' in endpoint:
        return _get_sas_token_v1(endpoint, access_token, organization, container)
    return _get_sas_token_v2(endpoint, access_token, organization, container)


def _get_sas_token_v2(endpoint: str, access_token: str, organization: str, container: str):
    """
    Generates an upload-token via accessmanager (version > 1)
    :param endpoint: which endpoint to use
    :param access_token: The OAuth access-token
    :param organization: The organization-name
    :param container: The container-name
    :return: Shared Access Token
    """
    logger.info("getting shared access signature")
    url = f'{endpoint}?organization={organization}&space={container}'

    payload = {}
    headers = {
        'Authorization': f'Bearer {access_token}'
    }

    response = requests.post(url, headers=headers, data=payload)

    response.raise_for_status()

    logger.info("got shared access signature")

    return response.text


def _get_sas_token_v1(endpoint: str, access_token: str, organization: str, container: str):
    """
    Generates an upload-token via accessmanager (version 1)
    :param endpoint: which endpoint to use
    :param access_token: The OAuth access-token
    :param organization: The organization-name
    :param container: The container-name
    :return: Shared Access Token
    """
    logger.info("getting shared access signature")
    url = f'{endpoint}?connectionId={organization}&containerName={container}'

    payload = {}
    headers = {
        'Authorization': f'Bearer {access_token}'
    }

    response = requests.post(url, headers=headers, data=payload)

    response.raise_for_status()

    logger.info("got shared access signature")

    return response.text


def filter_blobs(blobs: list[str], blacklist: str, whitelist: str) -> Union[set[str], list[str]]:
    """
    Filter blobs as follows:

    - if whitelist is provided - remove blacklisted blobs from whitelisted blobs
    - if no whitelist, but blacklist is provided - remove blacklisted blobs from original blob-list
    - if neither whitelist nor blacklist is provided - use the original blob-list

    :param blobs: the original blob-list
    :param blacklist: the blacklist-wildcard
    :param whitelist: the whitelist-wildcard
    :return: the filtered blob-list
    """

    whitelisted = blobs
    if whitelist:
        whitelisted = file_filter(whitelist, blobs)
    blacklisted = []
    if blacklist:
        blacklisted = file_filter(blacklist, blobs)

    # if whitelist -> remove blacklist from whitelist
    if whitelist:
        return set(set(whitelisted) - set(blacklisted))
    # if no whitelist, but blacklist -> remove blacklist from original blob-list
    elif blacklist:
        return set(set(blobs) - set(blacklisted))

    return blobs


def file_filter(wildcard: str, blobnames: list[str]) -> list[str]:
    """
    Filter blobnames by wildcard

    :param wildcard: the wildcard
    :param blobnames: the blob-names
    :return: the filtered blobnames
    """
    pattern = wildcard2regex(wildcard)
    return [blob for blob in blobnames if re.search(pattern, blob, re.IGNORECASE)]
