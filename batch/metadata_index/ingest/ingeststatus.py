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


class IngestStatus:
    def __init__(self, organization=None, space=None, rootdir=None, userid=None, docid=None):
        self._organization = organization
        self._space = space
        self._rootdir = rootdir
        self._userid = userid
        self._docid = docid

    @property
    def organization(self):
        return self._organization

    @organization.setter
    def organization(self, organization):
        self._organization = organization

    @property
    def space(self):
        return self._space

    @space.setter
    def space(self, space):
        self._space = space

    @property
    def rootdir(self):
        return self._rootdir

    @rootdir.setter
    def rootdir(self, rootdir):
        self._rootdir = rootdir

    @property
    def userid(self):
        return self._userid

    @userid.setter
    def userid(self, userid):
        self._userid = userid

    @property
    def docid(self):
        return self._docid

    @docid.setter
    def docid(self, docid):
        self._docid = docid

    def to_dict(self):
        return {
            'organization': self._organization,
            'space': self._space,
            'rootdir': self._rootdir,
            'userid': self._userid,
            'docid': self._docid
        }

    @classmethod
    def load_from_json(cls, local_path: str):
        with open(local_path, 'r') as f:
            data = json.load(f)
        return cls(organization=data['organization'], space=data['space'], rootdir=data['rootdir'],
                            userid=data['userid'], docid=data['docid'])
