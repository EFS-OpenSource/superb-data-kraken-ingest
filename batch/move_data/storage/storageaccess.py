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
class StorageAccess:
    def __init__(self):
        pass

    def move_data(self, access_token: str, organization: str, src_space: str, dst_space: str, root_dir: str):
        """
        Moves a directory from one space to another
        :param access_token: The access-token.
        :param organization: The organization.
        :param src_space: The source-space (usually 'loadingzone')
        :param dst_space: The target-space
        :param root_dir: The root-directory
        """
        pass
