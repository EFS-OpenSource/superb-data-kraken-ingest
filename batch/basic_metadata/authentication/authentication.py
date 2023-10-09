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
import urllib

import requests


def get_access_token(user_name: str, client: str, secret: str) -> str:
    """
    Returns an access_token using the given client and secret.
    If a user_name is passed, an access_token for this user is returned, else a
    system user access_token is returned.

    Parameters
    ----------
    user_name : str
        Optional user_name the token shall be created for.
    client : str
        The client ID
    secret : str
        The client secret

    Returns
    -------
    str
        The generated access_token
    """
    _, auth_header_service_connection = _get_service_account_access_token(client, secret)
    if user_name:
        _, auth_header_user_context = _get_user_context_token(user_name, client, secret, auth_header_service_connection)
        return auth_header_user_context

    return auth_header_service_connection


def _get_service_account_access_token(client_id: str, client_secret: str):
    """
    Generates OAuth-Token for the service account
    :param client_id:
    :param client_secret:
    :return: expires-in and access-token
    """

    logging.info("getting access-token")
    access_token_uri = os.environ['ACCESS_TOKEN_URI']

    payload = {
        'grant_type': 'client_credentials',
        'client_id': client_id,
        'client_secret': client_secret
    }

    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }

    response = requests.post(access_token_uri, headers=headers, data=payload)
    response.raise_for_status()

    logging.info("got service account access-token")
    response_json = response.json()

    return response_json['expires_in'], response_json["access_token"]


def _get_user_context_token(requested_subject: str, original_client_id: str, original_client_secret: str,
                            original_access_token: str):
    """
    Generates OAuth-Token for the given user from the service account access token via token-exchange
    :param requested_subject:
    :param original_client_id:
    :param original_client_secret:
    :param original_access_token:
    :return: expires-in and access-token
    """

    logging.info("exchanging service-account access-token for user access-token")
    access_token_uri = os.environ['ACCESS_TOKEN_URI']

    payload = {
        'grant_type': 'urn:ietf:params:oauth:grant-type:token-exchange',
        'client_id': original_client_id,
        'client_secret': original_client_secret,
        'subject_token': original_access_token,
        'requested_token_type': 'urn:ietf:params:oauth:token-type:access_token',
        'requested_subject': requested_subject
    }

    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }

    response = requests.post(access_token_uri, headers=headers, data=urllib.parse.urlencode(payload))
    response.raise_for_status()

    logging.info("got access-token in user context")
    response_json = response.json()

    return response_json['expires_in'], response_json["access_token"]
