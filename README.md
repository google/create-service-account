# Create Service Account for Google Workspace Migration Products

<!--
Copyright 2020 Google LLC

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    https://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
-->

These scripts are designed to automate the steps needed to create a service account for use with Google Workspace migration & sync products. They are meant to be executed within a Google Cloud Shell. The scripts generate a service account's private key JSON file which can then be provided to the migration or sync tool. The scripts automate the following:

*   Creates a GCP project
*   Enables APIs
*   Creates a service account
*   Authorizes the service account
*   Creates and downloads a service account key

Table of contents
=================

   * [Getting Started](#getting-started)
   * [Usage](#usage)
      * [Google Workspace Migrate (GWM)](#google-workspace-migrate-gwm)
      * [Google Workspace Migration for Microsoft Exchange (GWMME)](#google-workspace-migration-for-microsoft-exchange-gwmme)
      * [Password Sync](#password-sync)
   * [Help](#help)
      * [Bugs and Feature Requests](#bugs-and-feature-requests)
      * [Alternatives](#alternatives)

## Getting Started

In order to run these scripts, you must be a Google Workspace Super
Administrator. The script that you execute will depend on which tool you are
using. To get started, first select the tool that you are planning to use.

*   [Google Workspace Migration for Microsoft Exchange (GWMME)](#google-workspace-migration-for-microsoft-exchange-gwmme)
*   [Google Workspace Migrate (GWM)](#google-workspace-migrate-gwm)
*   [Password Sync](#password-sync)

## Usage

### Google Workspace Migration for Microsoft Exchange (GWMME)

To create an authorized service account for Google Workspace Migration for
Microsoft Exchange, copy and paste the command below in Cloud Shell.

1.  [Open Cloud Shell](https://ssh.cloud.google.com/cloudshell/editor?shellonly=true)
2.  Copy and paste the following command into Cloud Shell and press Enter.

```
python3 <(curl -s -S -L https://git.io/gwmme-create-service-account)
```

### Google Workspace Migrate (GWM)

To create an authorized service account for Google Workspace Migration, copy and
paste the command below in Cloud Shell.

1.  [Open Cloud Shell](https://ssh.cloud.google.com/cloudshell/editor?shellonly=true)
2.  Copy and paste the following command into Cloud Shell and press Enter.

```
python3 <(curl -s -S -L https://git.io/gwm-create-service-account)
```

### Password Sync

To create an authorized service account for Password Sync, copy and paste the
command below in Cloud Shell.

1.  [Open Cloud Shell](https://ssh.cloud.google.com/cloudshell/editor?shellonly=true)
2.  Copy and paste the following command into Cloud Shell and press Enter.

```
python3 <(curl -s -S -L https://git.io/password-sync-create-service-account)
```

## Help

### Bugs and Feature Requests

These scripts are not an officially supported Google product. Therefore, there is no guarantee or ETA for bug fixes or feature requests. That being said, if you think that there may be a bug or you want to request a feature, then please [create a new issue](https://github.com/google/create-service-account/issues/new/choose).

### Alternatives

If these scripts are not working for you, then you can use the manual steps instead. Select which product you are trying to create a service account for to see the manual steps
* [Google Workspace Migration for Microsoft Exchange (GWMME)](https://support.google.com/a/answer/6291304?hl=en#zippy=%2Coption-manually-create-a-service-account)
* [Google Workspace Migrate (GWM)](https://support.google.com/workspacemigrate/answer/10839762)
* [Password Sync](https://support.google.com/a/answer/7040511?hl=en#step1&step2&step3&step4&step5&#:~:text=Option%202%3A-,Manually%20create,-a%20service%20account)

--------------------------------------------------------------------------------

*This is not an officially supported Google product.*

