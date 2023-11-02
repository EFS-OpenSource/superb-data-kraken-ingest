# Ingest


[![python39](https://img.shields.io/badge/python-3.9-green?logo=python)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)

<p align="center">
  <img src="docs/images/logo-sdk-white-transparent.png" alt="SDK LOGO" width="50%">
  <br>
  <em>A data platform for everyone</em>
</p>

- [Ingest](#ingest)
  - [About](#about)
    - [skip\_validation](#skip_validation)
    - [basic\_metadata](#basic_metadata)
    - [anonymize](#anonymize)
    - [enrichment](#enrichment)
    - [validate](#validate)
    - [metadata\_index](#metadata_index)
    - [move\_data](#move_data)
  - [Getting Started](#getting-started)
    - [Prerequisites](#prerequisites)
    - [Setup](#setup)
    - [Configuration](#configuration)
    - [Usage](#usage)
  - [Contributing](#contributing)
  - [Changelog](#changelog)

## About


The ingest is a service of the **Superb Data Kraken Platform (SDK)**. It is designed for managing data-ingestion to the SDK.

For a more detailed understanding of the broader context of the platform this project is used in, refer to
the [architecture documentation](https://github.com/EFS-OpenSource/superb-data-kraken-architecture).

For instructions on how to deploy the `ingest` on an instance of the **SDK**, refer to
the [installation instructions](https://github.com/EFS-OpenSource/superb-data-kraken-install-instructions).

The workers that are part of the ingest are explained in more detail below.

![Ingest](docs/images/ingest.png)


### skip_validation


Certain organizations may not need to validate data (should be ingested as is). This worker provides a functionality, so one can configure, for which
organizations no validation is required. Configuration via [SKIP_VALIDATE_ORGANIZATIONS](./argo/config-map.yml).


### basic_metadata


In case no "qualified" metadata is provided, this worker generates a basic metadata-set and stores it in the cloud storage (loadingzone).


### anonymize


This worker will provide functionality to anonymize metadata. However it is not implemented yet.


### enrichment


This worker will provide functionality to enrich metadata. However it is not implemented yet.


### validate


This worker will provide functionality to validate the dataset. However it is not implemented yet.


### metadata_index

Indexes meta.json to the dedicated `<orga>_<space>_measurements`-index via [metadata-service](https://github.com/EFS-OpenSource/superb-data-kraken-metadata).
For this, the worker accesses the cloud storage to read the meta.json and pass the content to the service. The document-id is stored in a dedicated file
ingest.json - this prevents multiple indexing. **CAUTION:** Only users with the role `<orga>_<space>_trustee` may update documents - executing the ingest
multiple times from a user without trustee-permission will lead to errors!

The following environment variables are required:

| name              | description                                                                                     |
| ----------------- | ----------------------------------------------------------------------------------------------- |
| CLIENT_ID         | client-id of confidential OAuth-Client                                                          |
| CLIENT_SECRET     | client-secret of confidential OAuth-Client                                                      |
| ACCESS_TOKEN_URI  | URI of the token-endpoint                                                                       |
| INDEXER_URL       | URL of the metadata-backend                                                                     |
| STORAGE_TYPE      | storage-type - one of `azure` and `s3` (default: `azure` - s3 currently not supported)          |
| ACCESSMANAGER_URL | URL of the accessmanager (only required if `azure`-storage)                                     |
| STORAGE_DOMAIN    | domain of the storage-implementation (only required, if `s3`-storage - currently not supported) |
| BUCKET            | storage-bucket (only required, if `s3`-storage - currently not supported)                       |

### move_data

Finally, the data is being moved from `loadingzone` to the main-storage.

The following pipeline variables are required:

| name                   | description                                                                                                 |
| ---------------------- | ----------------------------------------------------------------------------------------------------------- |
| CLIENT_ID              | client-id of confidential OAuth-Client                                                                      |
| CLIENT_SECRET          | client-secret of confidential OAuth-Client                                                                  |
| ACCESS_TOKEN_URI       | URI of the token-endpoint                                                                                   |
| STORAGE_TYPE           | storage-type - one of `azure` and `s3` (default: `azure` - s3 currently not supported)                      |
| READ_ENDPOINT          | endpoint for generating SAS-Token in read-scope (only required, if `azure`-storage)                         |
| UPLOAD_ENDPOINT        | endpoint for generating SAS-Token in upload-scope (only required, if `azure`-storage)                       |
| DELETE_ENDPOINT        | endpoint for generating SAS-Token in delete-scope (only required, if `azure`-storage)                       |
| BLACKLIST              | comma-separated list of wildcarded blob names that should not be moved to main-storage but deleted directly |
| &lt;ORGA&gt;.WHITELIST | comma-separated list of wildcarded blob names that should be moved to main-storage                          |
| STORAGE_DOMAIN         | domain of the storage-implementation (only required, if `s3`-storage - currently not supported)             |
| BUCKET                 | storage-bucket (only required, if `s3`-storage - currently not supported)                                   |

**NOTE on black- and whitelist:** The blacklist applies globally. It can be used to define files that can potentially cause damage to the system (*.exe, *.bat). If your organization only has certain file-extensions, you can use the organization-scoped whitelist to prevent uploading other extensions. The blacklist restricts each whitelist.

If you have the following configuration a bat- or a png-file would not be moved to main-storage:

```
blacklist = "*.exe,*.bat"
whitelist = "*.csv,*.json,*.bat"
```

## Getting Started

Follow the instructions below to set up a local copy of the project for development and testing.

### Prerequisites

- python >= 3.9
- A running OIDC/OAuth2 provider instance
- A running kafka-instance
- A running [argo workflows instance](https://argoproj.github.io/argo-workflows/)
- A running [argo events instance](https://argoproj.github.io/argo-events/) with an [EventSource](https://argoproj.github.io/argo-events/concepts/event_source/)
  listening on the kafka-event `accessmanager-commit` (which is sent by accessmanager/commit)
- Cloud-Storage in expected [storage-structure](https://github.com/EFS-OpenSource/superb-data-kraken-architecture) - currently only azure supported
- [accessmanager](https://github.com/EFS-OpenSource/superb-data-kraken-accessmanager)
- [organizationmanager](https://github.com/EFS-OpenSource/superb-data-kraken-organizationmanager)
- [metadata-service](https://github.com/EFS-OpenSource/superb-data-kraken-metadata)

### Setup

You may provide a secret `auth-secret` (as referenced by the [ingest-sensor](./argo/ingest-sensor.yml)), with the following setup:

```yaml
apiVersion: v1
data:
  ACCESS_TOKEN_URI: <ACCESS_TOKEN_URI_BASE64>
  CLIENT_ID: <CLIENT_ID_BASE64>
  CLIENT_SECRET: <CLIENT_SECRET_BASE64>
kind: Secret
metadata:
  name: auth-secret
  namespace: argo-mgmt
type: Opaque
```

This secret is being refered to from [metadata_index](#metadata_index) and [move_data](#move_data).

### Configuration

The configuration of the ingest takes place in [argo/config-map.yml](./argo/config-map.yml).

As already mentioned in [skip_validation](#skip_validation) the property `SKIP_VALIDATE_ORGANIZATIONS` is a comma-separated list of organizations, that should
not be validated.

Every other configuration within this file refers to your cluster-internal domain. Aside from a possible postfix, nothing more must be configured.

### Usage


The ingest is an argo events sensor with an event-source for the accessmanager-commit-event. So the ingest is triggered, every time a dataset is committed via
accessmanager.


## Contributing


See the [Contribution Guide](./CONTRIBUTING.md).


## Changelog


See the [Changelog](./CHANGELOG.md).
