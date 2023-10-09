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
# logging
import logging
import os

import requests
from azure.storage.blob import ContainerClient, BlobProperties

from storage.remote_file import RemoteFile
from storage.storageaccess import StorageAccess

logger = logging.getLogger(__name__)

TYPE = 'azure'


class AzureStorageAccess(StorageAccess):

    def list_content(self, access_token: str, organization: str, container: str, root_dir_name: str) -> list[
        RemoteFile]:
        logging.debug("list_content - Start")

        read_sas = _get_sas_token(access_token, organization, container, "read")
        logger.info("Creating container client...")
        source_container_client = ContainerClient.from_container_url(
            f'{_get_storage_url(organization, container)}?{read_sas}')
        logger.info("Creating container client...Done!")
        logger.info("Listing available blobs...")
        blobs = source_container_client.list_blobs(name_starts_with=f'{root_dir_name}/')
        logger.info("Listing available blobs...Done!")

        logging.debug("list_content - Done")
        return [_convert_to_remotefile(blob) for blob in blobs]

    def upload_file(self, access_token: str, organization: str, space: str, root_dir_name: str, file_name: str,
                    content):
        logging.debug("upload_file - Start")

        write_sas = _get_sas_token(access_token, organization, space, "upload")
        container_client = ContainerClient.from_container_url(
            f'{_get_storage_url(organization, "loadingzone")}?{write_sas}')

        path = f'{root_dir_name}/{file_name}'

        container_client.upload_blob(name=path, data=content, validate_content=True)

        logging.debug("upload_file - Done")


def _convert_to_remotefile(blob: BlobProperties):
    return RemoteFile(blob.name, blob.creation_time)


def _get_sas_token(access_token: str, organization: str, space: str, reqtype: str):
    """
    Generates an upload-token via accessmanager (version > 1)

    Parameters
    ----------
    access_token : str
        The access token.
    organization : str
        Organization the token shall be created for.
    space : str
        The space the token shall be created for.
    reqtype : str
        Type of request. read|upload|delete

    Returns
    -------
    _type_
        The created SAS token.
    """
    logger.info("getting shared access signature")
    url = f'{os.environ["ACCESSMANAGER_URL"]}/accessmanager/api/v2.0/accessmanager/{reqtype}?organization={organization}&space={space}'

    payload = {}
    headers = {
        'Authorization': f'Bearer {access_token}'
    }

    response = requests.post(url, headers=headers, data=payload)

    response.raise_for_status()

    logger.info("got shared access signature")

    return response.text


def _get_storage_url(account: str, container: str):
    """
    Generates storage-url
    :param account: The account-name
    :param container: The container-name
    :return: storage-url
    """
    return f'https://{account}.blob.core.windows.net/{container}'
