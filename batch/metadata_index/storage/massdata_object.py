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


class MassdataObject:
    def __init__(self, name: str, location: str, date_created: datetime, size: int):
        self._name = name
        self._date_created = date_created
        self._location = location
        self._size = size

    @property
    def name(self) -> str:
        return self._name

    @property
    def date_created(self) -> datetime:
        return self._date_created

    @property
    def location(self) -> str:
        return self._location

    @property
    def size(self) -> int:
        return self._size

    def to_dict(self):
        return {'name': self._name, 'dateCreated': self._date_created.strftime("%Y-%m-%dT%H:%M:%S%z"), 'location': self._location,
                'size': self._size}
