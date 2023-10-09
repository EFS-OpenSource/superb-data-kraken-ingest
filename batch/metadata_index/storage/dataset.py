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
from storage.massdata_object import MassdataObject


class DataSet:
    def __init__(self, meta_json=None, ingest_state=None, massdata=None):
        self._meta_json = meta_json
        self._ingest_state = ingest_state
        self._massdata = massdata

    @property
    def meta_json(self) -> str:
        return self._meta_json

    @property
    def ingest_state(self) -> str:
        return self._ingest_state

    @property
    def massdata(self) -> list[MassdataObject]:
        return self._massdata
