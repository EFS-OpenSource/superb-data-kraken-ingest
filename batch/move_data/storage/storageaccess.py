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
import re


class StorageAccess:
    def __init__(self):
        pass

    def move_data(self, access_token: str, organization: str, src_space: str, dst_space: str, root_dir: str,
                  blacklist: str, whitelist: str):
        """
        Moves a directory from one space to another
        :param access_token: The access-token.
        :param organization: The organization.
        :param src_space: The source-space (usually 'loadingzone')
        :param dst_space: The target-space
        :param root_dir: The root-directory
        :param blacklist: files matching this wildcard will not be moved
        :param whitelist: files matching this wildcard will be moved
        """
        pass


def wildcard2regex(wildcard: str):
    """
    Convert wildcard to regular expression, so that '*.exe,*.js' will be converted to '^(.*\\.exe)|(.*\\.js)$' - so it doesn't accidentially find .json within .js-filter!

    - escape wildcard
    - replace '\\*' with '.*', '\\?' with '.'
    - split wildcard by ',', strip each part and surround with braces
    - force start- and end-of-line-assertion ('^'/'$')

    :param wildcard: the wildcard in a comma-separated manner
    :return: the regular expression
    """
    # Escape special characters in the wildcard pattern
    escaped_pattern = re.escape(wildcard)

    # Convert the escaped pattern to a regex pattern
    parts = escaped_pattern.replace("\\*", ".*").replace("\\?", ".").split(",")  # Split the string on commas
    # surround each part with "(...)"
    trimmed_parts = [f'({part.strip()})' for part in parts]  # Trim whitespace from each part and surround with "(..)"
    joined = "|".join(trimmed_parts)  # Join the trimmed parts with a pipe
    return f'^{joined}$'
