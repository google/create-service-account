#!/usr/bin/python3
# Copyright 2020 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""GCP Cloud Shell script to automate creation of a service account for Password Sync.

This script streamlines the installation of Password Sync by automating the
steps required for obtaining a service account key. Specifically, this script
will:

1. Create a GCP project.
2. Enable APIs
3. Create a service account
4. Authorize the service account
5. Create and download a service account key
"""

import asyncio
import datetime
import json
import logging
import os
import pathlib
import sys
import time
import urllib.parse

from google_auth_httplib2 import Request
from httplib2 import Http

from google.auth.exceptions import RefreshError
from google.oauth2 import service_account

VERSION = "2"

# GCP project IDs must only contain lowercase letters, digits, or hyphens.
# Projct IDs must start with a letter. Spaces or punctuation are not allowed.
TOOL_NAME = "PasswordSync"
TOOL_NAME_FRIENDLY = "Password Sync"
TOOL_HELP_CENTER_URL = "https://support.google.com/a/answer/7378726"
# List of APIs to enable and verify.
APIS = [
    # If admin.googleapis.com is to be included, then it must be the first in
    # this list.
    "admin.googleapis.com"
]
# List of scopes required for service account.
SCOPES = ["https://www.googleapis.com/auth/admin.directory.user"]
DWD_URL_FORMAT = ("https://admin.google.com/ac/owl/domainwidedelegation?"
                  "overwriteClientId=true&clientIdToAdd={}&clientScopeToAdd={}")
USER_AGENT = f"{TOOL_NAME}_create_service_account_v{VERSION}"
KEY_FILE = (f"{pathlib.Path.home()}/{TOOL_NAME.lower()}-service-account-key-"
            f"{datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S')}.json")

# Zero width space character, to be used to separate URLs from punctuation.
ZWSP = "\u200b"

async def create_project():
  logging.info("Creating project...")
  project_id = f"{TOOL_NAME.lower()}-{int(time.time() * 1000)}"
  project_name = (f"{TOOL_NAME}-"
                  f"{datetime.datetime.now().strftime('%Y%m%d-%H%M%S')}")
  await retryable_command(f"gcloud projects create {project_id} "
                          f"--name {project_name} --set-as-default")
  logging.info("%s successfully created \u2705", project_id)


async def verify_tos_accepted():
  logging.info("Verifying acceptance of Terms of service...")
  tos_accepted = False
  while APIS and not tos_accepted:
    command = f"gcloud services enable {APIS[0]}"
    _, stderr, return_code = await retryable_command(
        command, max_num_retries=1, suppress_errors=True)
    if return_code:
      err_str = stderr.decode()
      if "UREQ_TOS_NOT_ACCEPTED" in err_str:
        if "universal" in err_str:
          logging.debug("Google APIs Terms of Service not accepted")
          print("You must first accept the Google APIs Terms of Service. You "
                "can accept the terms of service by clicking "
                "https://console.developers.google.com/terms/universal and "
                "clicking 'Accept'.\n")
        elif "appsadmin" in err_str:
          logging.debug("Google Apps Admin APIs Terms of Service not accepted")
          print("You must first accept the Google Apps Admin APIs Terms of "
                "Service. You can accept the terms of service by clicking "
                "https://console.developers.google.com/terms/appsadmin and "
                "clicking 'Accept'.\n")
        answer = input("If you've accepted the terms of service, press Enter "
                       "to try again or 'n' to cancel:")
        if answer.lower() == "n":
          sys.exit(0)
      else:
        logging.critical(err_str)
        sys.exit(1)
    else:
      tos_accepted = True
  logging.info("Terms of service acceptance verified \u2705")


async def enable_apis():
  logging.info("Enabling APIs...")
  # verify_tos_accepted checks the first API, so skip it here.
  enable_api_calls = map(enable_api, APIS[1:])
  await asyncio.gather(*enable_api_calls)
  logging.info("APIs successfully enabled \u2705")


async def create_service_account():
  logging.info("Creating service account...")
  service_account_name = f"{TOOL_NAME.lower()}-service-account"
  service_account_display_name = f"{TOOL_NAME} Service Account"
  await retryable_command(f"gcloud iam service-accounts create "
                          f"{service_account_name} --display-name "
                          f'"{service_account_display_name}"')
  logging.info("%s successfully created \u2705", service_account_name)


async def create_service_account_key():
  logging.info("Creating service acount key...")
  service_account_email = await get_service_account_email()
  await retryable_command(f"gcloud iam service-accounts keys create {KEY_FILE} "
                          f"--iam-account={service_account_email}")
  logging.info("Service account key successfully created \u2705")


async def authorize_service_account():
  service_account_id = await get_service_account_id()
  scopes = urllib.parse.quote(",".join(SCOPES), safe="")
  authorize_url = DWD_URL_FORMAT.format(service_account_id, scopes)
  input(f"\nBefore using {TOOL_NAME_FRIENDLY}, you must authorize the service "
        "account to perform actions on behalf of your users. You can do so by "
        f"clicking:\n\n{authorize_url}\n\nAfter clicking 'Authorize', return "
        "here and press Enter to continue.")


async def verify_service_account_authorization():
  logging.info("Verifying service account authorization...")
  admin_user_email = await get_admin_user_email()
  service_account_id = await get_service_account_id()
  scopes_are_authorized = False
  while not scopes_are_authorized:
    scope_authorization_failures = []
    for scope in SCOPES:
      scope_authorized = verify_scope_authorization(admin_user_email, scope)
      if not scope_authorized:
        scope_authorization_failures.append(scope)
    if scope_authorization_failures:
      scopes = urllib.parse.quote(",".join(SCOPES), safe="")
      authorize_url = DWD_URL_FORMAT.format(service_account_id, scopes)
      logging.info("The service account is not properly authorized.")
      logging.warning("The following scopes are missing:")
      for scope in scope_authorization_failures:
        logging.warning("\t- %s", scope)
      print("\nTo fix this, please click the following link. After clicking "
            "'Authorize', return here to try again. If you are confident "
            "that these scopes have already been added, then you may continue "
            "now. If you encouter OAuth errors in the migration tool, then "
            "you may need to wait for the changes to propagate. Propagation "
            "generally takes less than 1 hour. However, in rare cases, it can "
            "take up to 24 hours.")
      print(f"\n{authorize_url}\n")
      answer = input("Press Enter to try again, 'c' to continue, or 'n' to "
                     "cancel:")
      if answer.lower == "c":
        scopes_are_authorized = True
      if answer.lower() == "n":
        sys.exit(0)
    else:
      scopes_are_authorized = True
  logging.info("Service account successfully authorized \u2705")


async def verify_api_access():
  logging.info("Verifying API access...")
  admin_user_email = await get_admin_user_email()
  project_id = await get_project_id()
  token = get_access_token_for_scopes(admin_user_email, SCOPES)
  retry_api_verification = True
  while retry_api_verification:
    disabled_apis = {}
    disabled_services = []
    retry_api_verification = False
    for api in APIS:
      api_name = service_name = ""
      raw_api_response = ""
      if api == "admin.googleapis.com":
        # Admin SDK does not have a corresponding service.
        api_name = "Admin SDK"
        raw_api_response = execute_api_request(
            f"https://content-admin.googleapis.com/admin/directory/v1/users/{admin_user_email}?fields=isAdmin",
            token)
      if api == "calendar-json.googleapis.com":
        api_name = service_name = "Calendar"
        raw_api_response = execute_api_request(
            "https://www.googleapis.com/calendar/v3/users/me/calendarList?maxResults=1&fields=kind",
            token)
      if api == "contacts.googleapis.com":
        # Contacts does not have a corresponding service.
        api_name = "Contacts"
        raw_api_response = execute_api_request(
            "https://www.google.com/m8/feeds/contacts/a.com/full/invalid_contact",
            token)
      if api == "drive.googleapis.com":
        api_name = service_name = "Drive"
        raw_api_response = execute_api_request(
            "https://www.googleapis.com/drive/v3/files?pageSize=1&fields=kind", token)
      if api == "gmail.googleapis.com":
        api_name = service_name = "Gmail"
        raw_api_response = execute_api_request(
            "https://gmail.googleapis.com/gmail/v1/users/me/labels?fields=labels.id", token)
      if api == "tasks.googleapis.com":
        api_name = service_name = "Tasks"
        raw_api_response = execute_api_request(
            "https://tasks.googleapis.com/tasks/v1/users/@me/lists?maxResults=1&fields=kind", token)

      if is_api_disabled(raw_api_response):
        disabled_apis[api_name] = api
        retry_api_verification = True

      if service_name and is_service_disabled(raw_api_response):
        disabled_services.append(service_name)
        retry_api_verification = True

    if disabled_apis:
      disabled_api_message = (
          "The {} API is not enabled. Please enable it by clicking "
          "https://console.developers.google.com/apis/api/{}/overview?project={}."
      )
      for api_name in disabled_apis:
        api_id = disabled_apis[api_name]
        print(disabled_api_message.format(api_name, api_id, project_id))
      print("\nIf these APIs are already enabled, then you may need to wait "
            "for the changes to propagate. Propagation generally takes a few "
            "minutes. However, in rare cases, it can take up to 24 hours.\n")

    if not disabled_apis and disabled_services:
      disabled_service_message = "The {0} service is not enabled for {1}."
      for service in disabled_services:
        print(disabled_service_message.format(service, admin_user_email))
      print("\nIf this is expected, then please continue. If this is not "
            "expected, then please ensure that these services are enabled for "
            "your users by visiting "
            "https://admin.google.com/ac/appslist/core.\n")

    if retry_api_verification:
      answer = input("Press Enter to try again, 'c' to continue, or 'n' to "
                     "cancel:")
      if answer.lower() == "c":
        retry_api_verification = False
      if answer.lower() == "n":
        sys.exit(0)

  logging.info("API access verified \u2705")


async def download_service_account_key():
  command = f"cloudshell download {KEY_FILE}"
  await retryable_command(command)


async def delete_key():
  input("\nPress Enter after you have downloaded the file.")
  logging.debug(f"Deleting key file ${KEY_FILE}...")
  command = f"shred -u {KEY_FILE}"
  await retryable_command(command)  


async def enable_api(api):
  command = f"gcloud services enable {api}"
  await retryable_command(command)


def verify_scope_authorization(subject, scope):
  try:
    get_access_token_for_scopes(subject, [scope])
    return True
  except RefreshError:
    return False
  except:
    e = sys.exc_info()[0]
    logging.error("An unknown error occurred: %s", e)
    return False


def get_access_token_for_scopes(subject, scopes):
  logging.debug("Getting access token for scopes %s, user %s", scopes, subject)
  credentials = service_account.Credentials.from_service_account_file(
      KEY_FILE, scopes=scopes)
  delegated_credentials = credentials.with_subject(subject)
  request = Request(Http())
  delegated_credentials.refresh(request)
  logging.debug("Successfully obtained access token")
  return delegated_credentials.token


def execute_api_request(url, token):
  try:
    http = Http()
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "User-Agent": USER_AGENT
    }
    logging.debug("Executing API request %s", url)
    _, content = http.request(url, "GET", headers=headers)
    logging.debug("Response: %s", content.decode())
    return content
  except:
    e = sys.exc_info()[0]
    logging.error("Failed to execute API request: %s", e)
    return None


def is_api_disabled(raw_api_response):
  if raw_api_response is None:
    return True
  try:
    api_response = json.loads(raw_api_response)
    return "it is disabled" in api_response["error"]["message"]
  except:
    pass
  return False


def is_service_disabled(raw_api_response):
  if raw_api_response is None:
    return True
  try:
    api_response = json.loads(raw_api_response)
    error_reason = api_response["error"]["errors"][0]["reason"]
    if "notACalendarUser" or "notFound" or "authError" in error_reason:
      return True
  except:
    pass

  try:
    api_response = json.loads(raw_api_response)
    if "service not enabled" in api_response["error"]["message"]:
      return True
  except:
    pass

  return False


async def retryable_command(command,
                            max_num_retries=3,
                            retry_delay=5,
                            suppress_errors=False,
                            require_output=False):
  num_tries = 1
  while num_tries <= max_num_retries:
    logging.debug("Executing command (attempt %d): %s", num_tries, command)
    process = await asyncio.create_subprocess_shell(
        command,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE)
    stdout, stderr = await process.communicate()
    return_code = process.returncode

    logging.debug("stdout: %s", stdout.decode())
    logging.debug("stderr: %s", stderr.decode())
    logging.debug("Return code: %d", return_code)

    if return_code == 0:
      if not require_output or (require_output and stdout):
        return (stdout, stderr, return_code)

    if num_tries < max_num_retries:
      num_tries += 1
      await asyncio.sleep(retry_delay)
    elif suppress_errors:
      return (stdout, stderr, return_code)
    else:
      logging.critical("Failed to execute command: `%s`", stderr.decode())
      sys.exit(return_code)


async def get_project_id():
  command = "gcloud config get-value project"
  project_id, _, _ = await retryable_command(command, require_output=True)
  return project_id.decode().rstrip()


async def get_service_account_id():
  command = 'gcloud iam service-accounts list --format="value(uniqueId)"'
  service_account_id, _, _ = await retryable_command(
      command, require_output=True)
  return service_account_id.decode().rstrip()


async def get_service_account_email():
  command = 'gcloud iam service-accounts list --format="value(email)"'
  service_account_email, _, _ = await retryable_command(
      command, require_output=True)
  return service_account_email.decode().rstrip()


async def get_admin_user_email():
  command = 'gcloud auth list --format="value(account)"'
  admin_user_email, _, _ = await retryable_command(command, require_output=True)
  return admin_user_email.decode().rstrip()


def init_logger():
  # Log DEBUG level messages and above to a file
  logging.basicConfig(
      filename=f"{TOOL_NAME}_create_service_account.log",
      format="[%(asctime)s][%(levelname)s] %(message)s",
      datefmt="%FT%TZ",
      level=logging.DEBUG)

  # Log INFO level messages and above to the console
  console = logging.StreamHandler()
  console.setLevel(logging.INFO)
  formatter = logging.Formatter("%(message)s")
  console.setFormatter(formatter)
  logging.getLogger("").addHandler(console)


async def main():
  init_logger()
  os.system("clear")
  response = input(
      "Welcome! This script will create and authorize the resources that are "
      f"necessary to use {TOOL_NAME_FRIENDLY}. The following steps will be "
      "performed on your behalf:\n\n1. Create a Google Cloud Platform project\n"
      "2. Enable APIs\n3. Create a service account\n4. Authorize the service "
      "account\n5. Create a service account key\n\nIn the end, you will be "
      "prompted to download the service account key. This key can then be used "
      f"for {TOOL_NAME}.\n\nIf you would like to perform these steps manually, "
      f"then you can follow the instructions at {TOOL_HELP_CENTER_URL}{ZWSP}."
      "\n\nPress Enter to continue or 'n' to exit:")

  if response.lower() == "n":
    sys.exit(0)

  await create_project()
  await verify_tos_accepted()
  await enable_apis()
  await create_service_account()
  await authorize_service_account()
  await create_service_account_key()
  await verify_service_account_authorization()
  await verify_api_access()
  await download_service_account_key()
  await delete_key()

  logging.info("Done! \u2705")
  print("\nIf you have already downloaded the file, then you may close this "
        "page. Please remember that this file is highly sensitve. Any person "
        "who gains access to the key file will then have full access to all "
        "resources to which the service account has access. You should treat "
        "it just like you would a password.")


if __name__ == "__main__":
  asyncio.run(main())
