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

## Getting Started

These scripts are designed to automate the steps needed to create a service
account for use with Google Workspace migration & sync products. They are meant
to be executed within a [Google Cloud Shell](https://cloud.google.com/shell).
The scripts generate a service account's private key JSON file which can then be
provided to the migration or sync tool. The scripts automate the following:

*   Creates a GCP project
*   Enables APIs
*   Creates a service account
*   Authorizes the service account
*   Creates and downloads a service account key

In order to run these scripts, you must be a Google Workspace Super
Administrator. The script that you execute will depend on which tool you are
using. To get started, first select the tool that you are planning to use.

*   [Google Workspace Migration for Microsoft Exchange (GWMME)](#google-workspace-migration-for-microsoft-exchange-gwmme)
*   [Google Workspace Migrate (GWM)](#google-workspace-migrate-gwm)
*   [G Suite Password Sync](#password-sync)

## Google Workspace Migration for Microsoft Exchange (GWMME) {#google-workspace-migration-for-microsoft-exchange-gwmme}

To create an authorized service account for Google Workspace Migration for
Microsoft Exchange, copy and paste the command below in Cloud Shell.

1.  [Open Cloud Shell](https://ssh.cloud.google.com/cloudshell/editor?shellonly=true)
2.  Copy and paste the following command into Cloud Shell and press Enter.

```
python3 <(curl -s -S -L https://git.io/gwmme-create-service-account)
```

## Google Workspace Migrate (GWM) {#google-workspace-migrate-gwm}

To create an authorized service account for Google Workspace Migration, copy and
paste the command below in Cloud Shell.

1.  [Open Cloud Shell](https://ssh.cloud.google.com/cloudshell/editor?shellonly=true)
2.  Copy and paste the following command into Cloud Shell and press Enter.

```
python3 <(curl -s -S -L https://git.io/gwm-create-service-account)
```

## G Suite Password Sync {#password-sync}

To create an authorized service account for Password Sync, copy and paste the
command below in Cloud Shell.

1.  [Open Cloud Shell](https://ssh.cloud.google.com/cloudshell/editor?shellonly=true)
2.  Copy and paste the following command into Cloud Shell and press Enter.

```
python3 <(curl -s -S -L https://git.io/password-sync-create-service-account)
```

--------------------------------------------------------------------------------

*This is not an officially supported Google product.*

