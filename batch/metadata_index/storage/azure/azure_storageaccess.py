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
# -*- coding: utf-8 -*-
import logging
import os
import tempfile

import requests
from azure.storage.blob import BlobClient, ContainerClient, BlobProperties

from storage.dataset import DataSet
from storage.massdata_object import MassdataObject
from storage.storageaccess import StorageAccess

logger = logging.getLogger(__name__)

TYPE = 'azure'


class AzureStorageAccess(StorageAccess):

    def __init__(self):
        super().__init__()

    def get_dataset(self, organization: str, space: str, root_dir_name: str, access_token: str) -> DataSet:
        read_sas = _get_sas_token(access_token, organization, space, "read")
        logger.debug("Creating container client...")
        source_container_client = ContainerClient.from_container_url(
            f'{_get_storage_url(organization, space)}?{read_sas}')
        logger.debug("Creating container client...Done!")
        logger.debug("Listing available blobs...")

        my_blobs = source_container_client.list_blobs(name_starts_with=f'{root_dir_name}/')
        dataset = list(my_blobs)

        logger.debug("Listing available blobs...Done!")
        # create temporal directory
        logger.debug("Creating temp directory...")
        temp_dir = tempfile.mkdtemp()
        logger.debug("Creating temp directory...Done!")

        massdata = [file for file in dataset if
                    not file.name.endswith('/meta.json') and not file.name.endswith(f'/{self.INGEST_STATUS_FILE}')]

        # handle meta.json
        meta_jsons = [file for file in dataset if file.name.endswith('/meta.json')]
        if len(meta_jsons) < 1:
            raise FileNotFoundError('no meta.json found!')

        meta_json = meta_jsons[0]
        logger.info(f"Checking file {meta_json.name}...")

        # download meta.json
        src_blob_client = BlobClient.from_blob_url(
            f'{_get_storage_url(organization, space)}/{meta_json.name}?{read_sas}')
        local_meta_json = self._download_file(meta_json, src_blob_client, temp_dir)

        # handle ingest.json
        ingest_jsons = [file for file in dataset if file.name.endswith(f'/{self.INGEST_STATUS_FILE}')]
        local_ingest_json = None
        if len(ingest_jsons) > 1:  # multiple ingest.jsom found -> error
            raise ValueError(f'Unexpected directory structure: multiple {self.INGEST_STATUS_FILE} files found')
        if len(ingest_jsons) > 0:
            ingest_json = ingest_jsons[0]

            # download ingest.json
            src_blob_client = BlobClient.from_blob_url(
                f'{_get_storage_url(organization, space)}/{ingest_json.name}?{read_sas}')
            local_ingest_json = self._download_file(ingest_json, src_blob_client, temp_dir)

        return DataSet(meta_json=local_meta_json, ingest_state=local_ingest_json,
                       massdata=[_massdata_object(blob) for blob in massdata])

    def _download_file(self, file, src_blob_client, temp_dir):
        logger.info(f'Download {file.name}...')
        filename = file.name.replace("/", "_")
        local_file = os.path.join(temp_dir, filename)
        with open(local_file, "wb") as f:
            data = src_blob_client.download_blob()
            data.readinto(f)
            f.close()

        logger.info(f'Download {file.name}...Done!')
        return local_file

    def upload_status(self, access_token: str, organization: str, space: str, root_dir: str, local_file: str):
        """
        Updates
        """
        write_sas = _get_sas_token(access_token, organization, space, "upload/main")
        prefix = '' if root_dir == '' else root_dir + '/'
        blob_path = prefix + os.path.basename(local_file)
        container_client = ContainerClient.from_container_url(f'{_get_storage_url(organization, space)}?{write_sas}')
        # delete ingest.json if already exists
        ingest_blobs = container_client.list_blobs(name_starts_with=blob_path)
        ingest_blobs_list = list(ingest_blobs)
        if len(ingest_blobs_list) > 0: # -> only 1
            delete_sas = _get_sas_token(access_token, organization, space, "delete")
            blob_client = BlobClient.from_blob_url(f'{_get_storage_url(organization, space)}/{blob_path}?{delete_sas}')
            blob_client.delete_blob()
        with open(local_file, 'rb') as data:
            container_client.upload_blob(name=blob_path, data=data, validate_content=True)


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


# azure storage functionality


def _get_storage_url(account: str, container: str):
    """
    Generates storage-url
    :param account: The account-name
    :param container: The container-name
    :return: storage-url
    """
    return f'https://{account}.blob.core.windows.net/{container}'


def _massdata_object(blob: BlobProperties) -> MassdataObject:
    return MassdataObject(name=blob.name.split('/')[-1], location=blob.name, date_created=blob.creation_time,
                          size=blob.size)
