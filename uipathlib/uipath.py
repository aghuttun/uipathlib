"""
This library provides a Python client for interacting with the UiPath Orchestrator API.
"""

# import base64
import dataclasses
import json
import logging
from typing import Any, Type
import requests
from pydantic import BaseModel, parse_obj_as
from .models import (
    ListAssets,
    ListBuckets,
    ListCalendars,
    ListEnvironments,
    ListJobs,
    ListMachines,
    ListProcesses,
    ListQueues,
    ListQueueItems,
    GetQueueItem,
    AddQueueItem,
    ListReleases,
    ListRobots,
    ListRobotLogs,
    ListRoles,
    ListSchedules,
    ListSessions,
)

# Creates a logger for this module
logger = logging.getLogger(__name__)


class UiPath(object):
    """
    UiPath client to interact with UiPath Orchestrator via API.
    """

    @dataclasses.dataclass
    class Configuration:
        """Configuration dataclass for UiPath client."""

        url_base: str | None = None
        client_id: str | None = None
        refresh_token: str | None = None
        token: str | None = None
        scope: str | None = None

    @dataclasses.dataclass
    class Response:
        """Response dataclass for UiPath client methods."""

        status_code: int
        content: Any = None

    def __init__(
        self,
        url_base: str,
        client_id: str,
        refresh_token: str,
        scope: str,
        custom_logger: logging.Logger | None = None,
    ) -> None:
        """
        Initialize the UiPath Cloud client with the provided credentials and configuration.

        Args:
            url_base (str): The base URL for the UiPath Orchestrator API.
            client_id (str): The client ID for authentication.
            refresh_token (str): The refresh token for authentication.
            scope (str): The scope for the authentication.
            custom_logger (logging.Logger, optional): Logger instance to use. If None, a default logger is created.
        """
        # Init logging
        # Use provided logger or create a default one
        self._logger = custom_logger or logging.getLogger(name=__name__)

        # Init variables
        self._session: requests.Session = requests.Session()

        # Credentials/Configuration
        self._configuration = self.Configuration(
            url_base=url_base,
            client_id=client_id,
            refresh_token=refresh_token,
            token=None,
            scope=scope,
        )

        # Authenticate
        self.auth()

    def __del__(self) -> None:
        """
        Cleans the house at the exit.
        """
        self._logger.info(msg="Cleans the house at the exit")
        self._session.close()

    def is_auth(self) -> bool:
        """
        Check whether authentication was successful.

        Returns:
            bool: If true, then authentication was successful.
        """
        self._logger.info(msg="Gets authentication status")
        return False if self._configuration.token is None else True

    def auth(self) -> None:
        """
        Authentication.

        This method performs the authentication process to obtain an access token using the client credentials flow. The
        token is stored in the Configuration dataclass for subsequent API requests.
        """
        self._logger.info(msg="Authentication")

        # Request headers
        # headers = {"Connection": "keep-alive",
        #            "Content-Type": "application/json"}
        headers = {
            "Connection": "keep-alive",
            "Content-Type": "application/x-www-form-urlencoded",
        }

        # Authorization URL
        # url_auth = "https://account.uipath.com/oauth/token"
        url_auth = "https://cloud.uipath.com/adidas/identity_/connect/token"

        # Request body
        # body = {"grant_type": "refresh_token",
        #         "client_id": self._configuration.client_id,
        #         "refresh_token": self._configuration.refresh_token}

        # Personal Access Tokens
        # body = "grant_type=client_credentials&" \
        #         f"client_id={self._configuration.client_id}&" \
        #         f"client_secret={self._configuration.refresh_token}&" \
        #         f"scope={self._configuration.scope}"

        body = {
            "grant_type": "client_credentials",
            "client_id": self._configuration.client_id,
            "client_secret": self._configuration.refresh_token,
            "scope": self._configuration.scope,
        }

        # Request
        response = self._session.post(url=url_auth, data=body, headers=headers)

        # Log response code
        self._logger.info(msg=f"HTTP Status Code {response.status_code}")

        # Return valid response
        if response.status_code == 200:
            self._configuration.token = json.loads(response.content.decode("utf-8"))["access_token"]

    def _export_to_json(self, content: bytes, save_as: str | None) -> None:
        """
        Export response content to a JSON file.

        This method takes the content to be exported and saves it to a specified file in JSON format. If the `save_as`
        parameter is provided, the content will be written to that file.

        Args:
            content (bytes): The content to be exported, typically the response content from an API call.
            save_as (str): The file path where the JSON content will be saved. If None, the content will not be saved.
        """
        if save_as is not None:
            self._logger.info(msg="Exports response to JSON file.")
            with open(file=save_as, mode="wb") as file:
                file.write(content)

    def _handle_response(
        self, response: requests.Response, model: Type[BaseModel], rtype: str = "scalar"
    ) -> dict | list[dict]:
        """
        Handle and deserializes the JSON content from an API response.

        This method processes the response from an API request and deserializes the JSON content into a Pydantic
        BaseModel or a list of BaseModel instances, depending on the response type.

        Args:
            response (requests.Response): The response object from the API request.
            model (Type[BaseModel]): The Pydantic BaseModel class to use for deserialization and validation.
            rtype (str, optional): The type of response to handle. Use "scalar" for a single record and "list" for a
              list of records. Defaults to "scalar".

        Returns:
            dict or list[dict]: The deserialized content as a dictionary (scalar) or a list of dictionaries (list).
        """
        if rtype.lower() == "scalar":
            # Deserialize json (scalar values)
            content_raw = response.json()
            # Pydantic v1 validation
            validated = model(**content_raw)
            # Convert to dict
            return validated.dict()
        else:
            # Deserialize json
            content_raw = response.json()["value"]
            # Pydantic v1 validation
            validated_list = parse_obj_as(list[model], content_raw)
            # return [dict(data) for data in parse_obj_as(list[model], content_raw)]
            # Convert to a list of dicts
            return [item.dict() for item in validated_list]

    # ASSETS
    def list_assets(self, fid: str, save_as: str | None = None) -> Response:
        """
        Retrieve a list of all assets from the UiPath Orchestrator.

        Args:
            fid (str): The folder ID for the organization unit.
            save_as (str, optional): The file path where the JSON content will be saved. If None, the content will not
              be saved.

        Returns:
            Response: A dataclass containing the status code and the list of assets.
        """
        self._logger.info(msg="Gets a list of all assets")

        # Configuration
        token = self._configuration.token
        url_base = self._configuration.url_base

        # Request headers
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}",
            "X-UIPATH-OrganizationUnitID": fid,
        }

        # Request query
        url_query = rf"{url_base}/odata/Assets"

        # Query parameters
        # Pydantic v1
        alias_list = [field.alias for field in ListAssets.__fields__.values() if field.field_info.alias is not None]
        params = {"$select": ",".join(alias_list)}

        # Request
        response = self._session.get(url=url_query, headers=headers, params=params, verify=True)

        # Log response code
        self._logger.info(msg=f"HTTP Status Code {response.status_code}")

        # Output
        content = None
        if response.status_code == 200:
            self._logger.info(msg="Request successful")

            # Export response to json file
            self._export_to_json(content=response.content, save_as=save_as)

            # Deserialize json
            content = self._handle_response(response=response, model=ListAssets, rtype="list")

        return self.Response(status_code=response.status_code, content=content)

    # BUCKETS
    def list_buckets(self, fid: str, save_as: str | None = None) -> Response:
        """
        Buckets - Get all.

        Get the UiPath Orchestrator buckets.

        Args:
            fid (str): The folder ID for the organization unit.
            save_as (str, optional): The file path where the JSON content will be saved. If None, the content will not
              be saved.

        Returns:
            Response: A dataclass containing the status code and the list of buckets.
        """
        self._logger.info(msg="Gets a list of all buckets")

        # Configuration
        token = self._configuration.token
        url_base = self._configuration.url_base

        # Request headers
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}",
            "X-UIPATH-OrganizationUnitID": fid,
        }

        # Request query
        url_query = rf"{url_base}/odata/Buckets"

        # Query parameters
        # Pydantic v1
        alias_list = [field.alias for field in ListBuckets.__fields__.values() if field.field_info.alias is not None]
        params = {"$select": ",".join(alias_list)}

        # Request
        response = self._session.get(url=url_query, headers=headers, params=params, verify=True)

        # Log response code
        self._logger.info(msg=f"HTTP Status Code {response.status_code}")

        # Output
        content = None
        if response.status_code == 200:
            self._logger.info(msg="Request successful")

            # Export response to json file
            self._export_to_json(content=response.content, save_as=save_as)

            # Deserialize json
            content = self._handle_response(response=response, model=ListBuckets, rtype="list")

        return self.Response(status_code=response.status_code, content=content)

    def create_bucket(self, fid: str, name: str, guid: str, description: str | None = None) -> Response:
        """
        Create a new Storage Bucket in UiPath Orchestrator.

        GUID generator: https://www.guidgenerator.com/online-guid-generator.aspx

        Args:
            fid (str): The folder ID for the organization unit.
            name (str): The name of the Storage Bucket.
            guid (str): The unique identifier (GUID) for the Storage Bucket.
            description (str, optional): A description for the Storage Bucket. Defaults to None.

        Returns:
            Response: A dataclass containing the status code and the response content.
        """
        self._logger.info(msg="Create bucket")
        self._logger.info(msg=name)

        # Configuration
        token = self._configuration.token
        url_base = self._configuration.url_base

        # Request headers
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}",
            "X-UIPATH-OrganizationUnitID": fid,
        }

        # Description
        description = "" if description is None else description

        # Request query
        url_query = rf"{url_base}/odata/Buckets"

        # Body
        body = {
            "Name": name,
            "Description": description,
            "Identifier": guid,
            "StorageProvider": None,
            "StorageParameters": None,
            "StorageContainer": None,
            "CredentialStoreId": None,
            "ExternalName": None,
            "Password": None,
            "FoldersCount": 0,
            "Id": 0,
        }

        # Request
        response = self._session.post(url=url_query, json=body, headers=headers, verify=True)

        # Log response code
        self._logger.info(msg=f"HTTP Status Code {response.status_code}")

        content = None
        if response.status_code == 201:
            self._logger.info(msg="Request successful")

        return self.Response(status_code=response.status_code, content=content)

    def delete_bucket(self, fid: str, id: str) -> Response:
        """
        Delete a Storage Bucket from UiPath Orchestrator.

        Args:
            fid (str): The folder ID for the organization unit.
            id (str): The ID of the Storage Bucket to delete.

        Returns:
            Response: A dataclass containing the status code and the response content.
        """
        self._logger.info(msg="Deletes storage bucket")
        self._logger.info(msg=id)

        # Configuration
        token = self._configuration.token
        url_base = self._configuration.url_base

        # Request headers
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}",
            "X-UIPATH-OrganizationUnitID": fid,
        }

        # Request query
        url_query = rf"{url_base}/odata/Buckets({id})"

        # Request
        response = self._session.delete(url=url_query, headers=headers, verify=True)

        # Log response code
        self._logger.info(msg=f"HTTP Status Code {response.status_code}")

        # Output
        content = None
        if response.status_code == 204:
            self._logger.info(msg="Request successful")

        return self.Response(status_code=response.status_code, content=content)

    def upload_bucket_file(self, fid: str, id: str, localpath: str, remotepath: str) -> Response:
        """
        Upload a file to a Storage Bucket.

        Args:
            fid (str): The folder ID for the organization unit.
            id (str): Storage bucket ID (example: 2).
            localpath (str): The local file to copy.
            remotepath (str): File name in Storage Bucket.
              Example: remotepath="PR123.json".

        Returns:
            Response: A dataclass containing the status code and the response content.
        """
        self._logger.info(msg="Uploads file to bucket")
        self._logger.info(msg=id)
        self._logger.info(msg=localpath)
        self._logger.info(msg=remotepath)

        # Configuration
        token = self._configuration.token
        url_base = self._configuration.url_base

        # Request headers
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}",
            "X-UIPATH-OrganizationUnitID": fid,
        }

        # Request query
        server_conf = "UiPath.Server.Configuration.OData"
        url_query = rf"{url_base}/odata/Buckets({id})/{server_conf}.GetWriteUri?path={remotepath}&expiryInMinutes=0"

        # Request
        response = self._session.get(url=url_query, headers=headers, verify=True)

        # Log response code
        self._logger.info(msg=f"HTTP Status Code {response.status_code}")

        # Output
        content = None
        if response.status_code == 200:
            # Extract URI
            uri = response.json()["Uri"]
            # Body
            with open(file=localpath, mode="rb") as file:
                # Upload file
                headers = {"x-ms-blob-type": "BlockBlob"}
                response = self._session.put(url=uri, headers=headers, data=file, verify=True)

                # Successful upload
                if response.status_code == 200:
                    self._logger.info(msg="File uploaded successfully")

        return self.Response(status_code=response.status_code, content=content)

    def delete_bucket_file(self, fid: str, id: str, filename: str) -> Response:
        """
        Delete a file from a Storage Bucket.

        Args:
            fid (str): The folder ID for the organization unit.
            id (str): Storage bucket ID.
            filename (str): The name of the file to delete.

        Returns:
            Response: A dataclass containing the status code and the response content.
        """
        self._logger.info(msg="Delete bucket file")
        self._logger.info(msg=filename)

        # Configuration
        token = self._configuration.token
        url_base = self._configuration.url_base

        # Request headers
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}",
            "X-UIPATH-OrganizationUnitID": fid,
        }

        # Request query
        url_query = rf"{url_base}/odata/Buckets({id})/UiPath.Server.Configuration.OData.DeleteFile?path={filename}"

        # Request
        response = self._session.delete(url=url_query, headers=headers, verify=True)

        # Log response code
        self._logger.info(msg=f"HTTP Status Code {response.status_code}")

        # Output
        content = None
        if response.status_code == 204:
            self._logger.info(msg="Request successful")

        return self.Response(status_code=response.status_code, content=content)

    # CALENDARS
    def list_calendars(self, fid: str, save_as: str | None = None) -> Response:
        """
        Get the UiPath Orchestrator calendars.

        Args:
            fid (str): The folder ID for the organization unit.
            save_as (str, optional): The file path where the JSON content will be saved. If None, the content will not
              be saved.

        Returns:
            Response: A dataclass containing the status code and the list of calendars.
        """
        self._logger.info(msg="Gets a list of all calendars")

        # Configuration
        token = self._configuration.token
        url_base = self._configuration.url_base

        # Request headers
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}",
            "X-UIPATH-OrganizationUnitID": fid,
        }

        # Request query
        url_query = rf"{url_base}/odata/Calendars"

        # Query parameters
        # Pydantic v1
        alias_list = [field.alias for field in ListCalendars.__fields__.values() if field.field_info.alias is not None]
        params = {"$select": ",".join(alias_list)}

        # Request
        response = self._session.get(url=url_query, headers=headers, params=params, verify=True)

        # Log response code
        self._logger.info(msg=f"HTTP Status Code {response.status_code}")

        # Output
        content = None
        if response.status_code == 200:
            self._logger.info(msg="Request successful")

            # Export response to json file
            self._export_to_json(content=response.content, save_as=save_as)

            # Deserialize json
            content = self._handle_response(response=response, model=ListCalendars, rtype="list")

        return self.Response(status_code=response.status_code, content=content)

    # ENVIRONMENTS
    def list_environments(self, fid: str, save_as: str | None = None) -> Response:
        """
        Get the UiPath Orchestrator environments.

        Args:
            fid (str): The folder ID for the organization unit.
            save_as (str, optional): The file path where the JSON content will be saved. If None, the content will not
              be saved.

        Returns:
            Response: A dataclass containing the status code and the list of environments.
        """
        self._logger.info(msg="Gets a list of all environments")

        # Configuration
        token = self._configuration.token
        url_base = self._configuration.url_base

        # Request headers
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}",
            "X-UIPATH-OrganizationUnitID": fid,
        }

        # Request query
        url_query = rf"{url_base}/odata/Environments"

        # Query parameters
        # Pydantic v1
        alias_list = [
            field.alias
            for field in ListEnvironments.__fields__.values()
            if field.field_info.alias is not None
        ]
        params = {"$select": ",".join(alias_list)}

        # Request
        response = self._session.get(url=url_query, headers=headers, params=params, verify=True)

        # Log response code
        self._logger.info(msg=f"HTTP Status Code {response.status_code}")

        # Output
        content = None
        if response.status_code == 200:
            self._logger.info(msg="Request successful")

            # Export response to json file
            self._export_to_json(content=response.content, save_as=save_as)

            # Deserialize json
            content = self._handle_response(response=response, model=ListEnvironments, rtype="list")

        return self.Response(status_code=response.status_code, content=content)

    # JOBS
    def list_jobs(self, fid: str, filter: str, save_as: str | None = None) -> Response:
        """
        Get UiPath Orchestrator jobs.

        Filter use connetion: https://www.odata.org/documentation/odata-version-2-0/uri-conventions/

        Args:
            fid (str): The folder ID for the organization unit.
            filter (str): Condition to be used. Example: State eq 'Running'.
            save_as (str, optional): Name of the JSON file that contains the request response.

        Returns:
            Response: A dataclass containing the status code and the list of jobs.
        """
        self._logger.info(msg="Gets a list of all jobs based on the applied filter")
        self._logger.info(msg=filter)

        # Configuration
        token = self._configuration.token
        url_base = self._configuration.url_base

        # Request headers
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}",
            "X-UIPATH-OrganizationUnitID": fid,
        }

        # Request query
        url_query = rf"{url_base}/odata/Jobs"

        # Query parameters
        # Pydantic v1
        alias_list = [field.alias for field in ListJobs.__fields__.values() if field.field_info.alias is not None]
        params = {"$select": ",".join(alias_list), "$filter": filter}

        # Request
        response = self._session.get(url=url_query, headers=headers, params=params, verify=True)

        # Log response code
        self._logger.info(msg=f"HTTP Status Code {response.status_code}")

        # Output
        content = None
        if response.status_code == 200:
            self._logger.info(msg="Request successful")

            # Export response to json file
            self._export_to_json(content=response.content, save_as=save_as)

            # Deserialize json
            content = self._handle_response(response=response, model=ListJobs, rtype="list")

        return self.Response(status_code=response.status_code, content=content)

    def start_job(self, fid: str, process_key: str, robot_id: int | None = None) -> Response:
        """
        Start a job using a process key and a robot id.

        Args:
            fid (str): The folder ID for the organization unit.
            process_key (str): Process key. list_releases function, column KEY.
            robot_id (int, optional): Robot ID code or runs the job on all robots if None.

        Returns:
            Response: A dataclass containing the status code and the response content.
        """
        self._logger.info(msg="Starts the job")
        self._logger.info(msg=process_key)
        self._logger.info(msg=robot_id)

        # Configuration
        token = self._configuration.token
        url_base = self._configuration.url_base

        # Request headers
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}",
            "X-UIPATH-OrganizationUnitID": fid,
        }

        # Request query
        url_query = rf"{url_base}/odata/Jobs/UiPath.Server.Configuration.OData.StartJobs"

        # Body
        # case-sensitive
        # Strategy field - This dictates how the process should be run and has
        # 3 options:
        #  * Specific - The process will run on a specific set of robots, whose
        #               IDs are indicated in the RobotIds field.
        #  * JobsCount - The process will run x times, where x is the value of
        #                the JobsCount field. Use this strategy if
        #                you don't care on which robots the job runs.
        #                Orchestrator will automatically allocate the work
        #                to any available robots.
        #  * All - The process will run once on all robots.
        # Source: Manual, Time Trigger, Agent, Queue Trigger
        if robot_id is not None:
            body = {
                "startInfo": {
                    "ReleaseKey": process_key,
                    "Strategy": "Specific",
                    "RobotIds": [robot_id],
                    "JobsCount": 0,
                    "Source": "Manual",
                }
            }
        else:
            body = {
                "startInfo": {
                    "ReleaseKey": process_key,
                    "Strategy": "JobsCount",
                    "JobsCount": 1,
                    "Source": "Manual",
                }
            }

        # Request
        response = self._session.post(url=url_query, json=body, headers=headers, verify=True)
        # print(response.content)

        # Log response code
        self._logger.info(msg=f"HTTP Status Code {response.status_code}")

        return self.Response(status_code=response.status_code, content=None)

    def stop_job(self, fid: str, id: str) -> Response:
        """
        Stop a job using a job id.

        Args:
            fid (str): The folder ID for the organization unit.
            id (str): Job Id.

        Returns:
            Response: A dataclass containing the status code and the response content.
        """
        self._logger.info(msg="Stops a job")
        self._logger.info(msg=id)

        # Configuration
        token = self._configuration.token
        url_base = self._configuration.url_base

        # Request headers
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}",
            "X-UIPATH-OrganizationUnitID": fid,
        }

        # Request query
        url_query = rf"{url_base}/odata/Jobs({id})/UiPath.Server.Configuration.OData.StopJob"

        # Body
        body = {"strategy": "2"}

        # Request
        response = self._session.post(url=url_query, json=body, headers=headers, verify=True)

        # Log response code
        self._logger.info(msg=f"HTTP Status Code {response.status_code}")

        # Output
        content = None
        if response.status_code == 200:
            self._logger.info(msg="Request successful")

        return self.Response(status_code=response.status_code, content=content)

    # MACHINES
    def list_machines(self, fid: str, save_as: str | None = None) -> Response:
        """
        Machines - Get all.

        Get the machines from the UiPath Orchestrator.

        Args:
            fid (str): The folder ID for the organization unit.
            save_as (str, optional): Name of the JSON file that contains the request response.

        Returns:
            Response: A dataclass containing the status code and the list of machines.
        """
        self._logger.info(msg="Gets a list of all machines")

        # Configuration
        token = self._configuration.token
        url_base = self._configuration.url_base

        # Request headers
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}",
            "X-UIPATH-OrganizationUnitID": fid,
        }

        # Request query
        url_query = rf"{url_base}/odata/Machines"

        # Query parameters
        # Pydantic v1
        alias_list = [field.alias for field in ListMachines.__fields__.values() if field.field_info.alias is not None]
        params = {"$select": ",".join(alias_list)}

        # Request
        response = self._session.get(url=url_query, headers=headers, params=params, verify=True)

        # Log response code
        self._logger.info(msg=f"HTTP Status Code {response.status_code}")

        # Output
        content = None
        if response.status_code == 200:
            self._logger.info(msg="Request successful")

            # Export response to json file
            self._export_to_json(content=response.content, save_as=save_as)

            # Deserialize json
            content = self._handle_response(response=response, model=ListMachines, rtype="list")

        return self.Response(status_code=response.status_code, content=content)

    # PROCESSES
    def list_processes(self, fid: str, save_as: str | None = None) -> Response:
        """
        Get UiPath Orchestrator processes.

        Args:
            fid (str): The folder ID for the organization unit.
            save_as (str, optional): Name of the JSON file that contains the request response.

        Returns:
            Response: A dataclass containing the status code and the list of processes.
        """
        self._logger.info(msg="Gets a list of all processes")

        # Configuration
        token = self._configuration.token
        url_base = self._configuration.url_base

        # Request headers
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}",
            "X-UIPATH-OrganizationUnitID": fid,
        }

        # Request query
        url_query = rf"{url_base}/odata/Processes"

        # Query parameters
        # Pydantic v1
        alias_list = [field.alias for field in ListProcesses.__fields__.values() if field.field_info.alias is not None]
        params = {"$select": ",".join(alias_list)}

        # Request
        response = self._session.get(url=url_query, headers=headers, params=params, verify=True)

        # Log response code
        self._logger.info(msg=f"HTTP Status Code {response.status_code}")

        # Output
        content = None
        if response.status_code == 200:
            self._logger.info(msg="Request successful")

            # Export response to json file
            self._export_to_json(content=response.content, save_as=save_as)

            # Deserialize json
            content = self._handle_response(response=response, model=ListProcesses, rtype="list")

        return self.Response(status_code=response.status_code, content=content)

    # QUEUES
    def list_queues(self, fid: str, save_as: str | None = None) -> Response:
        """
        Retrieve all queues from the UiPath Orchestrator.

        Args:
            fid (str): The folder ID for the organization unit.
            save_as (str, optional): The file path where the JSON content will be saved. If None, the content will not
              be saved.

        Returns:
            Response: A dataclass containing the status code and the list of queues.
        """
        self._logger.info(msg="Gets a list of all queues")

        # Configuration
        token = self._configuration.token
        url_base = self._configuration.url_base

        # Request headers
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}",
            "X-UIPATH-OrganizationUnitID": fid,
        }

        # Request query
        url_query = rf"{url_base}/odata/QueueDefinitions"

        # Query parameters
        # Pydantic v1
        alias_list = [field.alias for field in ListQueues.__fields__.values() if field.field_info.alias is not None]
        params = {"$select": ",".join(alias_list)}

        # Request
        response = self._session.get(url=url_query, headers=headers, params=params, verify=True)

        # Log response code
        self._logger.info(msg=f"HTTP Status Code {response.status_code}")

        # Output
        content = None
        if response.status_code == 200:
            self._logger.info(msg="Request successful")

            # Export response to json file
            self._export_to_json(content=response.content, save_as=save_as)

            # Deserialize json
            content = self._handle_response(response=response, model=ListQueues, rtype="list")

        return self.Response(status_code=response.status_code, content=content)

    def list_queue_items(self, fid: str, filter: str, save_as: str | None = None) -> Response:
        """
        Retrieve all queue items from the UiPath Orchestrator based on the specified filter.

        Args:
            fid (str): The folder ID for the organization unit.
            filter (str): The filter condition to select the queue and item status.
              Example: "QueueDefinitionId eq 1 and Status eq 'New'"
            save_as (str, optional): The file path where the JSON content will be saved. If None, the content will not
              be saved.

        Returns:
            Response: A dataclass containing the status code and the list of queue items.
        """
        self._logger.info(msg="Gets a list of queue items using filter")
        self._logger.info(msg=filter)

        # Configuration
        token = self._configuration.token
        url_base = self._configuration.url_base

        # Request headers
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}",
            "X-UIPATH-OrganizationUnitID": fid,
        }

        # Request query
        url_query = rf"{url_base}/odata/QueueItems"

        # Query parameters
        # Pydantic v1
        alias_list = [field.alias for field in ListQueueItems.__fields__.values() if field.field_info.alias is not None]
        params = {"$select": ",".join(alias_list), "$filter": filter}

        # Request
        response = self._session.get(url=url_query, headers=headers, params=params, verify=True)

        # Log response code
        self._logger.info(msg=f"HTTP Status Code {response.status_code}")

        # Output
        content = None
        if response.status_code == 200:
            self._logger.info(msg="Request successful")

            # Export response to json file
            self._export_to_json(content=response.content, save_as=save_as)

            # Deserialize json
            content = self._handle_response(response=response, model=ListQueueItems, rtype="list")

        return self.Response(status_code=response.status_code, content=content)

    def get_queue_item(self, fid: str, id: int, save_as: str | None = None) -> Response:
        """
        Retrieve the details of a specific queue item from the UiPath Orchestrator.

        Args:
            fid (str): The folder ID for the organization unit.
            id (int): The ID of the queue item to retrieve (transaction ID).
            save_as (str, optional): The file path where the JSON content will be saved. If None, the content will not
              be saved.

        Returns:
            Response: A dataclass containing the status code and the details of the queue item.
        """
        self._logger.info(msg="Gets queue item details from queue")
        self._logger.info(msg=id)

        # Configuration
        token = self._configuration.token
        url_base = self._configuration.url_base

        # Request headers
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}",
            "X-UIPATH-OrganizationUnitID": fid,
        }

        # Request query
        url_query = rf"{url_base}/odata/QueueItems({id})"

        # Query parameters
        # Pydantic v1
        alias_list = [field.alias for field in GetQueueItem.__fields__.values() if field.field_info.alias is not None]
        params = {"$select": ",".join(alias_list)}

        # Request
        response = self._session.get(url=url_query, headers=headers, params=params, verify=True)

        # Log response code
        self._logger.info(msg=f"HTTP Status Code {response.status_code}")

        # Output
        content = None
        if response.status_code == 200:
            self._logger.info(msg="Request successful")

            # Export response to json file
            self._export_to_json(content=response.content, save_as=save_as)

            # Deserialize json
            content = self._handle_response(response=response, model=GetQueueItem, rtype="scalar")

        return self.Response(status_code=response.status_code, content=content)

    def add_queue_item(
        self,
        fid: str,
        queue: str,
        data: dict,
        reference: str,
        priority: str = "Normal",
        save_as: str | None = None,
    ) -> Response:
        """
        Add an item to a UiPath Orchestrator queue.

        Example: add_queue_item(fid="123",
                                queue="ElegibilityQueueNAM",
                                data={"PRCode": "PR1234"},
                                reference="PR1234",
                                priority="Normal")

        Args:
            fid (str): The folder ID for the organization unit.
            queue (str): The name of the queue.
            data (dict): A dictionary containing the item information.
            reference (str): A unique reference for the queue item.
            priority (str, optional): The priority of the queue item. Defaults to "Normal".
            save_as (str, optional): The file path where the JSON content will be saved. If None, the content will not
              be saved.

        Returns:
            Response: A dataclass containing the status code and the response content.
        """
        self._logger.info(msg="Adds item to queue")
        self._logger.info(msg=queue)
        self._logger.info(msg=reference)

        # Configuration
        token = self._configuration.token
        url_base = self._configuration.url_base

        # Request headers
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}",
            "X-UIPATH-OrganizationUnitID": fid,
        }

        # Request query
        url_query = rf"{url_base}/odata/Queues/UiPathODataSvc.AddQueueItem"

        # Query parameters
        # Pydantic v1
        alias_list = [field.alias for field in AddQueueItem.__fields__.values() if field.field_info.alias is not None]
        params = {"$select": ",".join(alias_list)}

        # Body
        # DueDate: null -> DueDate: None
        body = {
            "itemData": {
                "Name": queue,
                "Priority": priority,  # Normal, High
                "DeferDate": None,
                "DueDate": None,
                "Reference": reference,
                "SpecificContent": data,
            }
        }

        # Request
        # .encode("utf-8")
        response = self._session.post(url=url_query, json=body, headers=headers, params=params, verify=True)

        # Log response code
        self._logger.info(msg=f"HTTP Status Code {response.status_code}")

        # Unique reference violation
        if response.status_code == 409:
            self._logger.warning(f"Item with reference {reference} already in the queue")

        # Output
        content = None
        if response.status_code == 201:
            self._logger.info(msg="Request successful")

            # Export response to json file
            self._export_to_json(content=response.content, save_as=save_as)

            # Deserialize json
            content = self._handle_response(response=response, model=AddQueueItem, rtype="scalar")

        return self.Response(status_code=response.status_code, content=content)

    def update_queue_item(self, fid: str, queue: str, id: int, data: dict) -> Response:
        """
        Update an item in a UiPath Orchestrator queue.

        Args:
            fid (str): The folder ID for the organization unit.
            queue (str): The name of the queue.
              Example: queue="ElegibilityQueueNAM"
            id (int): The ID of the queue item to update.
              Example: id=1489001
            data (dict): A dictionary containing the updated item information.
              Example: content={"PRCode": "PR1234"}

        Returns:
            Response: A dataclass containing the status code and the response content.
        """
        self._logger.info(msg="Updates queue item in the queue")
        self._logger.info(msg=queue)

        # Configuration
        token = self._configuration.token
        url_base = self._configuration.url_base

        # Request headers
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}",
            "X-UIPATH-OrganizationUnitID": fid,
        }

        # Request query
        url_query = rf"{url_base}/odata/QueueItems({id})"

        # Body
        body = {
            "Name": queue,
            "Priority": "High",
            "SpecificContent": data,
            "DeferDate": None,
            "DueDate": None,
            "RiskSlaDate": None,
        }

        # Request
        # do not remove encode: data=body.encode("utf-8")
        # test in the future the body: dict and data=json.dumps(body)
        response = self._session.put(url=url_query, json=body, headers=headers, verify=True)

        # Log response code
        self._logger.info(msg=f"HTTP Status Code {response.status_code}")

        # Output
        content = None
        if response.status_code == 200:
            self._logger.info(msg="Request successful")

        return self.Response(status_code=response.status_code, content=content)

    def delete_queue_item(self, fid: str, id: int) -> Response:
        """
        Delete an item from a UiPath Orchestrator queue.

        Args:
            fid (str): The folder ID for the organization unit.
            id (int): The ID of the queue item to delete (transaction ID).

        Returns:
            Response: A dataclass containing the status code and the response content.
        """
        self._logger.info(msg="Deletes queue item")
        self._logger.info(msg=id)

        # Configuration
        token = self._configuration.token
        url_base = self._configuration.url_base

        # Request headers
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}",
            "X-UIPATH-OrganizationUnitID": fid,
        }

        # Request query
        url_query = rf"{url_base}/odata/QueueItems({id})"

        # Request
        response = self._session.delete(url=url_query, headers=headers, verify=True)

        # Log response code
        self._logger.info(msg=f"HTTP Status Code {response.status_code}")

        # Output
        content = None
        if response.status_code == 204:
            self._logger.info(msg="Request successful")

        return self.Response(status_code=response.status_code, content=content)

    # RELEASES
    def list_releases(self, fid: str, save_as: str | None = None) -> Response:
        """
        Retrieve a list of all process releases from the UiPath Orchestrator.

        Args:
            fid (str): The folder ID for the organization unit.
            save_as (str, optional): The file path where the JSON content will be saved. If None, the content will not
              be saved.

        Returns:
            Response: A dataclass containing the status code and the list of releases.
        """
        self._logger.info(msg="Gets list of releases")

        # Configuration
        token = self._configuration.token
        url_base = self._configuration.url_base

        # Request headers
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}",
            "X-UIPATH-OrganizationUnitID": fid,
        }

        # Request query
        url_query = rf"{url_base}/odata/Releases"

        # Query parameters
        # Pydantic v1
        alias_list = [field.alias for field in ListReleases.__fields__.values() if field.field_info.alias is not None]
        params = {"$select": ",".join(alias_list)}

        # Request
        response = self._session.get(url=url_query, headers=headers, params=params, verify=True)

        # Log response code
        self._logger.info(msg=f"HTTP Status Code {response.status_code}")

        # Output
        content = None
        if response.status_code == 200:
            self._logger.info(msg="Request successful")

            # Export response to json file
            self._export_to_json(content=response.content, save_as=save_as)

            # Deserialize json
            content = self._handle_response(response=response, model=ListReleases, rtype="list")

        return self.Response(status_code=response.status_code, content=content)

    # ROBOTS
    def list_robots(self, fid: str, save_as: str | None = None) -> Response:
        """
        Retrieve a list of all robots from the UiPath Orchestrator.

        Args:
            fid (str): The folder ID for the organization unit.
            save_as (str, optional): The file path where the JSON content will be saved. If None, the content will not
              be saved.

        Returns:
            Response: A dataclass containing the status code and the list of robots.
        """
        self._logger.info(msg="Gets a list of all robots")

        # Configuration
        token = self._configuration.token
        url_base = self._configuration.url_base

        # Request headers
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}",
            "X-UIPATH-OrganizationUnitID": fid,
        }

        # Request query
        url_query = rf"{url_base}/odata/Robots"

        # Query parameters
        # Pydantic v1
        alias_list = [field.alias for field in ListRobots.__fields__.values() if field.field_info.alias is not None]
        params = {"$select": ",".join(alias_list)}

        # Request
        response = self._session.get(url=url_query, headers=headers, params=params, verify=True)

        # Log response code
        self._logger.info(msg=f"HTTP Status Code {response.status_code}")

        # Output
        content = None
        if response.status_code == 200:
            self._logger.info(msg="Request successful")

            # Export response to json file
            self._export_to_json(content=response.content, save_as=save_as)

            # Deserialize json
            content = self._handle_response(response=response, model=ListRobots, rtype="list")

        return self.Response(status_code=response.status_code, content=content)

    def list_robot_logs(self, fid: str, filter: str, save_as: str | None = None) -> Response:
        """
        Retrieve a list of robot logs from the UiPath Orchestrator.

        Example: get_robot_logs(fid="123",
                                filter="JobKey eq 'bde11c1e-11e1-1bb1-11d1-e11f111111db'")

        Args:
            fid (str): The folder ID for the organization unit.
            filter (str): The filter condition to apply to the API call.
              Example: "JobKey eq 'bde11c1e-11e1-1bb1-11d1-e11f111111db'"
            save_as (str, optional): The file path where the JSON content will be saved. If None, the content will not
              be saved.

        Returns:
            Response: A dataclass containing the status code and the list of robot logs.
        """
        self._logger.info(msg="Gets a list of robot logs")

        # Configuration
        token = self._configuration.token
        url_base = self._configuration.url_base

        # Request headers
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}",
            "X-UIPATH-OrganizationUnitID": fid,
        }

        # Request query
        url_query = rf"{url_base}/odata/RobotLogs"

        # Query parameters
        # Pydantic v1
        # ?$top=10
        # last log line for robot X
        #   ?$top=1&$filter=RobotName eq 'Porto_Prod_2'&$orderby=TimeStamp desc
        # ?$filter=Level eq 'Error' or Level eq 'Fatal'
        # ?$filter=Level eq UiPath.Core.Enums.LogLevel%27Fatal%27
        # ?$filter=TimeStamp gt 2021-10-12T00:00:00.000Z and Level eq 'Error' or Level eq 'Fatal'
        # ?$filter=JobKey eq 98f59394-45e7-4da6-a695-50c70f4d87e3
        alias_list = [field.alias for field in ListRobotLogs.__fields__.values() if field.field_info.alias is not None]
        params = {"$select": ",".join(alias_list), "$filter": filter}

        # Request
        response = self._session.get(url=url_query, headers=headers, params=params, verify=True)

        # Log response code
        self._logger.info(msg=f"HTTP Status Code {response.status_code}")

        # Output
        content = None
        if response.status_code == 200:
            self._logger.info(msg="Request successful")

            # Export response to json file
            self._export_to_json(content=response.content, save_as=save_as)

            # Deserialize json
            content = self._handle_response(response=response, model=ListRobotLogs, rtype="list")

        return self.Response(status_code=response.status_code, content=content)

    # ROLES
    def list_roles(self, save_as: str | None = None) -> Response:
        """
        Retrieve a list of all roles from the UiPath Orchestrator.

        Args:
            save_as (str, optional): The file path where the JSON content will be saved. If None, the content will not
              be saved.

        Returns:
            Response: A dataclass containing the status code and the list of roles.
        """
        self._logger.info(msg="Gets a list of all roles")

        # Configuration
        token = self._configuration.token
        url_base = self._configuration.url_base

        # Request headers
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}",
        }

        # Request query
        url_query = rf"{url_base}/odata/Roles"

        # Query parameters
        # Pydantic v1
        alias_list = [field.alias for field in ListRoles.__fields__.values() if field.field_info.alias is not None]
        params = {"$select": ",".join(alias_list)}

        # Request
        response = self._session.get(url=url_query, headers=headers, params=params, verify=True)
        # print(response.content)

        # Log response code
        self._logger.info(msg=f"HTTP Status Code {response.status_code}")

        # Output
        content = None
        if response.status_code == 200:
            self._logger.info(msg="Request successful")

            # Export response to json file
            self._export_to_json(content=response.content, save_as=save_as)

            # Deserialize json
            content = self._handle_response(response=response, model=ListRoles, rtype="list")

        return self.Response(status_code=response.status_code, content=content)

    # SCHEDULES
    def list_schedules(self, fid: str, save_as: str | None = None) -> Response:
        """
        Retrieve a list of all schedules from the UiPath Orchestrator.

        Args:
            fid (str): The folder ID for the organization unit.
            save_as (str, optional): The file path where the JSON content will be saved. If None, the content will not
              be saved.

        Returns:
            Response: A dataclass containing the status code and the list of schedules.
        """
        self._logger.info(msg="Gets a list of all schedules")

        # Configuration
        token = self._configuration.token
        url_base = self._configuration.url_base

        # Request headers
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}",
            "X-UIPATH-OrganizationUnitID": fid,
        }

        # Request query
        url_query = rf"{url_base}/odata/ProcessSchedules"

        # Query parameters
        # Pydantic v1
        alias_list = [field.alias for field in ListSchedules.__fields__.values() if field.field_info.alias is not None]
        params = {"$select": ",".join(alias_list)}

        # Request
        response = self._session.get(url=url_query, headers=headers, params=params, verify=True)

        # Log response code
        self._logger.info(msg=f"HTTP Status Code {response.status_code}")

        # Output
        content = None
        if response.status_code == 200:
            self._logger.info(msg="Request successful")

            # Export response to json file
            self._export_to_json(content=response.content, save_as=save_as)

            # Deserialize json
            content = self._handle_response(response=response, model=ListSchedules, rtype="list")

        return self.Response(status_code=response.status_code, content=content)

    # SESSIONS
    def list_sessions(self, fid: str, save_as: str | None = None) -> Response:
        """
        Retrieve a list of all sessions from the UiPath Orchestrator.

        Args:
            fid (str): The folder ID for the organization unit.
            save_as (str, optional): The file path where the JSON content will be saved.
                                     If None, the content will not be saved.

        Returns:
            Response: A dataclass containing the status code and the list of sessions.
        """
        self._logger.info(msg="Gets a list of all sessions")

        # Configuration
        token = self._configuration.token
        url_base = self._configuration.url_base

        # Request headers
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}",
            "X-UIPATH-OrganizationUnitID": fid,
        }

        # Request query
        url_query = rf"{url_base}/odata/Sessions"

        # Query parameters
        # Pydantic v1
        alias_list = [field.alias for field in ListSessions.__fields__.values() if field.field_info.alias is not None]
        params = {"$select": ",".join(alias_list)}

        # Request
        response = self._session.get(url=url_query, headers=headers, params=params, verify=True)

        # Log response code
        self._logger.info(msg=f"HTTP Status Code {response.status_code}")

        # Output
        content = None
        if response.status_code == 200:
            self._logger.info(msg="Request successful")

            # Export response to json file
            self._export_to_json(content=response.content, save_as=save_as)

            # Deserialize json
            content = self._handle_response(response=response, model=ListSessions, rtype="list")

        return self.Response(status_code=response.status_code, content=content)


# eom
