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
import json
import logging
import os

import requests

from storage.remote_file import RemoteFile
from storage.storageaccess import StorageAccess


def create_basic_metadata(storage_access: StorageAccess, access_token: str, organization: str, space: str,
                          container: str, root_dir_name: str):
    """
    Creates a basic set of metadata for the gien dataset. Generation is only triggered if the space
    is configured to require metadata generation.

    Parameters
    ----------
    storage_access : StorageAccess
        The storage-access-implementation
    access_token : str
        The access token that shall be used.
    organization : str
        The organization the space belongs to.
    space : str
        The space the dataset belongs to.
    container : str
        The container the dataset is currently stored in.
    root_dir_name : str
        Path of the dataset.
    """
    logging.debug("create_basic_metadata - Start")

    space_info = _get_space_info(access_token, organization, space)

    if not space_info['metadataGenerate']:
        logging.info("Skipping metadata generation for space %s", space)
        return

    # List content of the dataset
    remotefiles = storage_access.list_content(access_token, organization, container, root_dir_name)

    # Check if meta.json is contained
    logging.info("Checking files for existing metadata...")
    for remotefile in remotefiles:
        logging.debug(remotefile.name)
        if remotefile.name == f'{root_dir_name}/meta.json':
            # metadata file exists -> exit
            logging.info("Metadata already exists -> Skipping")
            return
    logging.info("Checking files for existing metadata...Done")

    # If reached the metadata file does not exist -> create it
    logging.info("Creating metadata...")
    meta_data = _create_metadata(root_dir_name, space, remotefiles)
    logging.info("Creating metadata...Done")
    # upload the file
    logging.info("Uploading file...")
    # upload file to loadingzone
    storage_access.upload_file(access_token, organization, space, root_dir_name, "meta.json",
                               json.dumps(meta_data, indent=4))
    logging.info("Uploading file...Done")

    logging.debug("create_basic_metadata - Done")


def _get_space_info(access_token: str, organization: str, space: str):
    """
    Returns the space information from the organization-manager.

    Parameters
    ----------
    access_token : str
        The access token.
    organization : str
        The organization.
    space : str
        The space.

    Returns
    -------
    _type_
        Space information.
    """
    logging.debug("_get_space_info - Start")

    org_id = _resolve_organization_id(access_token, organization)

    url = f'{os.environ["ORGAMANAGER_URL"]}/organizationmanager/api/v2.0/organization/{org_id}/space/name/{space}'
    headers = {'Authorization': f'Bearer {access_token}'}

    response = requests.get(url, headers=headers)

    response.raise_for_status()
    logging.debug("_get_space_info - Done")
    return response.json()


def _resolve_organization_id(access_token: str, organization: str) -> str:
    """
    Returns the id for the given organization.

    Parameters
    ----------
    access_token : str
        The access token.
    organization : str
        The organization.

    Returns
    -------
    str
        ID of the organization.
    """
    logging.debug("_resolve_organization_id - Start")

    url = f'{os.environ["ORGAMANAGER_URL"]}/organizationmanager/api/v1.0/organization/name/{organization}'

    headers = {'Authorization': f'Bearer {access_token}'}

    response = requests.get(url, headers=headers)

    response.raise_for_status()

    orga = response.json()

    logging.info("ID of organization %s found: %s", organization, orga['id'])
    return str(orga['id'])


def _create_metadata(root_dir_name: str, space: str, remotefiles: list[RemoteFile]):
    """
    Creates the metadata content and returns it.

    Parameters
    ----------
    root_dir_name : str
        Name of the root directory.
    space : str
        The space.
    remotefiles : _type_
        List of RemoteFile.

    Returns
    -------
    _type_
        Content fo the metadata file.
    """
    logging.debug("_create_metadata - Start")

    # Read the metadata template
    with open("./data/tpl_meta.json", "r") as fp:
        meta_data = json.load(fp)

    # Fill the required fields
    # Names
    meta_data["name"] = root_dir_name
    meta_data["project"]["name"] = space
    meta_data["scope"]["name"] = space

    # Date
    for remotefile in remotefiles:
        if remotefile.date_created:
            meta_data["dateTime"]["createdAt"] = remotefile.date_created.strftime("%Y-%m-%dT%H:%M:%S%z")
            break

    logging.debug("_create_metadata - Done")
    return meta_data
