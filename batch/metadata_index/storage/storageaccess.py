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
import json
import logging
import os
import tempfile

from ingest.ingeststatus import IngestStatus
from storage.dataset import DataSet

logger = logging.getLogger(__name__)


class StorageAccess:
    INGEST_STATUS_FILE = 'ingest.json'

    def __init__(self):
        pass

    def get_dataset(self, organization: str, space: str, root_dir_name: str, access_token: str) -> DataSet:
        """
        Downloads the files within the root-directory from the given organization, space and root directory

        Parameters
        ----------
        organization : str
            The organization
        space : str
            The space the dataset is assigned to
        root_dir_name : str
            The root directory of the dataset.
        access_token : str
            The access token that shall be used.

        Returns
        -------
        [DataSet]
            DataSet of path of the local directory that contains the meta.json and ingest.json and list of massdata-objects.
        """
        pass

    def store_status(self, access_token: str, organization: str, space: str, root_dir: str, state: IngestStatus):
        """
        Stores the status-file in rootdir in cloud-storage.

        May delete existing ingest.json -> PERMISSIONS!!

        Parameters
        ----------
        access_token : str
            The access token that shall be used.
        organization : str
            The organization
        space : str
            The space the dataset is assigned to
        root_dir : str
            The root directory of the dataset.
        state : IngestStatus
            The state of ingest.

        """
        temp_dir = tempfile.mkdtemp()
        local_file = os.path.join(temp_dir, self.INGEST_STATUS_FILE)
        with open(local_file, "w") as f:
            json.dump(state.to_dict(), f)
        self.upload_status(access_token, organization, space, root_dir, local_file)

    def upload_status(self, access_token: str, organization: str, space: str, root_dir: str, local_file: str):
        pass
