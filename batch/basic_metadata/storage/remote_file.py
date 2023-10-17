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
from datetime import datetime


class RemoteFile:
    def __init__(self, name: str, date_created: datetime):
        self._name = name
        self._date_created = date_created

    @property
    def name(self) -> str:
        return self._name

    @property
    def date_created(self) -> datetime:
        return self._date_created