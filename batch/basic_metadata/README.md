# Basic metadata generator

[![python39](https://img.shields.io/badge/python-3.9-green?logo=python)](https://www.python.org/)

## Table of Contents

- [Basic metadata generator](#basic-metadata-generator)
    - [Table of Contents](#table-of-contents)
    - [About](#about)
    - [Getting Started](#getting-started)
        - [Prerequisites](#prerequisites)
        - [Installing](#installing)
    - [Usage](#usage)
    - [Built With](#built-with)
    - [Deployment](#deployment)
        - [Environment Variables](#environment-variables)
    - [Contributing](#contributing)
    - [Changelog](#changelog)
    - [Documentation](#documentation)

---

## About

This module is used to create a basic set of metadata for spaces that are not delivering metadata. This is required to
store the required technical metadata for every dataset.

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing
purposes.

### Prerequisites

Install Python > 3.

### Installing

Execute the following steps to setup your local environment for development and testing:

- Clone the repository
- Install the required packages via ```pip install -r requirements.txt```

## Usage

Commands that are required in order to use the service.

Use the module in another python script with ```pip install -r requirements.txt```

## Built With

Links to tools used for building.

* Python v3.9.5 (see this [Link](https://www.python.org/))

## Deployment

### Environment Variables

The following environment variables are required:

| name              | description                                                           |
|-------------------|-----------------------------------------------------------------------|
| CLIENT_ID         | client-id of confidential OAuth-Client                                |
| CLIENT_SECRET     | client-secret of confidential OAuth-Client                            |
| ACCESS_TOKEN_URI  | URI of the token-endpoint                                             |
| ORGAMANAGER_URL   | URL of orgamanager                                                    |
| STORAGE_TYPE      | storage-type - one of `azure` and `s3` (default: `azure`)             |
| ACCESSMANAGER_URL | URL of accessmanager (only required, if `azure`-storage)              |
| STORAGE_DOMAIN    | domain of the storage-implementation (only required, if `s3`-storage) |
| BUCKET            | storage-bucket (only required, if `s3`-storage)                       |

## Contributing

See the [Contribution Guide](../basic_metadata/CONTRIBUTING.md).

## Changelog

See the [Changelog](../basic_metadata/CHANGELOG.md).

## Documentation

TODO provide additional documentation
