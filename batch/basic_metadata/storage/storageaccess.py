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
from .remote_file import RemoteFile


class StorageAccess:
    def __init__(self):
        pass

    def list_content(self, access_token: str, organization: str, container: str, root_dir_name: str) -> list[
        RemoteFile]:
        """
        Lists the content of the given dataset.

        Parameters
        ----------
        access_token : str
            The access_token.
        organization : str
            The organization.
        container : str
            The container.
        root_dir_name : str
            The root dataset.

        Returns
        -------
        _type_
            List of remote_files.
        """
        pass

    def upload_file(self, access_token: str, organization: str, space: str, root_dir_name: str, file_name: str,
                    content):
        """
        Uploads the given file content.

        Parameters
        ----------
        access_token : str
            The access token.
        organization : str
            The organization.
        space : str
            The space.
        root_dir_name : str
            The root directory of the dataset.
        file_name : str
            Name of the file that shall be created.
        content : _type_
            Content of the file.
        """
        pass
