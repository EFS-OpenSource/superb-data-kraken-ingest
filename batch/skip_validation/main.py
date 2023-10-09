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
# -*- encoding: utf-8 -*-
import argparse
import base64
import json
import logging
import os

PROP_SKIP_VALIDATION = 'SKIP_VALIDATE_ORGANIZATIONS'


def _get_payload(payload: str):
    """
    Gets the payload - either directly or file if payload starts with '@'
    :param payload: payload-value
    :return: payload
    """
    if payload.startswith('@'):
        with open(payload.replace('@', ''), "r") as f:
            return f.read()
    return payload


def _extract_notification(origin):
    """
    extracts decoded data-body of argo-sensor-payload
    :param origin: as provided by argo-sensor
    :return: actual payload of notification
    """
    payload_json = json.loads(origin)
    data = payload_json['data']  # base64-encoded
    decoded_data = base64.b64decode(data).decode("utf-8").replace('\n', '')
    data_json = json.loads(decoded_data)
    body = data_json['body']  # base64-encoded
    decoded_body = base64.b64decode(body).decode("utf-8").replace('\n', '')
    return json.loads(decoded_body)


if __name__ == '__main__':

    FORMAT = '%(asctime)s %(levelname)s - %(message)s'
    logging.basicConfig(format=FORMAT)
    logger = logging.getLogger('skip_validation')
    logger.setLevel(level=logging.INFO)

    parser = argparse.ArgumentParser(description='Script to check if validation should be skipped', )

    parser.add_argument('--payload', '-p', dest='payload', type=str, required=True)

    args = parser.parse_args()
    if not args.payload:
        raise Exception('no payload provided')

    origin = _get_payload(args.payload)
    payload = _extract_notification(origin)

    if not PROP_SKIP_VALIDATION in os.environ:
        print(true)

    skip_organization_str = os.environ[PROP_SKIP_VALIDATION]
    skip_organizations = skip_organization_str.split(',')
    organization = payload['accountName']
    print(organization in skip_organization_str)
