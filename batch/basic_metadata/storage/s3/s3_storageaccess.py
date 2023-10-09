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

from storage.remote_file import RemoteFile
from storage.storageaccess import StorageAccess

ENV_STORAGE_DOMAIN = 'STORAGE_DOMAIN'
ENV_BUCKET = 'BUCKET'

PROP_ACCESS_KEY = 'AccessKeyId'
PROP_SECRET_KEY = 'SecretAccessKey'
PROP_SESSION_TOKEN = 'SessionToken'
NS_KEY = 'sts'

TYPE = 's3'

logger = logging.getLogger(__name__)


class S3StorageAccess(StorageAccess):

    def __init__(self):
        super().__init__()
        _validate()
        self.storage_domain = os.getenv(ENV_STORAGE_DOMAIN)
        self.bucket = os.getenv(ENV_BUCKET)

    def list_content(self, access_token: str, organization: str, container: str, root_dir_name: str) -> list[
        RemoteFile]:
        logging.warning('list_content is not implemented yet!')
        pass

    def upload_file(self, access_token: str, organization: str, space: str, root_dir_name: str, file_name: str,
                    content: str):
        logging.warning('upload_file is not implemented yet!')
        pass


def _validate():
    env_vars = os.environ
    _check_env(ENV_STORAGE_DOMAIN, env_vars)
    _check_env(ENV_BUCKET, env_vars)


def _check_env(env_var_name, env_vars):
    if env_var_name not in env_vars:
        raise ValueError(f'environment variable \'{env_var_name}\' is not found!')
