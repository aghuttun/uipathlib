"""
UiPath Orchestrator Python Client Library.

This module provides a Python client for interacting with the UiPath Orchestrator API.
It enables authentication and management of UiPath Orchestrator resources such as assets, buckets, calendars,
environments, jobs, machines, processes, queues, releases, robots, roles, schedules, and sessions via REST API calls.

Features
--------
- Authenticate with UiPath Orchestrator using client credentials.
- List, create, update, and delete assets, buckets, calendars, environments, jobs, machines, processes, queues,
releases, robots, roles, schedules, and sessions.
- Upload and delete files in storage buckets.
- Add, update, and delete queue items.
- Retrieve and filter logs and job information.
- Export API responses to JSON files for auditing or further processing.

Dependencies
------------
- requests
- pydantic
- dataclasses
- logging

Intended for use as a utility library in broader data engineering and automation workflows.
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
    Interact with the UiPath Orchestrator API using a Python client.

    Use this class to authenticate, manage assets, buckets, jobs, queues, robots, and other resources in UiPath
    Orchestrator via REST API calls. Instantiate the client with your Orchestrator credentials, then call the provided
    methods to perform operations such as listing, creating, updating, or deleting resources.

    Parameters
    ----------
    url_base : str
        The base URL for the UiPath Orchestrator API.
    client_id : str
        The client ID for authentication.
    refresh_token : str
        The refresh token or client secret for authentication.
    scope : str
        The scope for authentication.
    custom_logger : logging.Logger, optional
        Logger instance to use. If None, a default logger is created.

    Attributes
    ----------
    _logger : logging.Logger
        Logger for the client.
    _session : requests.Session
        Session object for HTTP requests.
    _configuration : UiPath.Configuration
        Configuration dataclass holding credentials and tokens.
    """

    @dataclasses.dataclass
    class Configuration:
        """
        Store configuration parameters for the UiPath client.

        Set and manage the base URL, client credentials, authentication token, and scope required for connecting to the
        UiPath Orchestrator API.

        Attributes
        ----------
        url_base : str or None
            The base URL for the UiPath Orchestrator API.
        client_id : str or None
            The client ID for authentication.
        refresh_token : str or None
            The refresh token or client secret for authentication.
        token : str or None
            The access token obtained after authentication.
        scope : str or None
            The scope for authentication.
        """

        url_base: str | None = None
        client_id: str | None = None
        refresh_token: str | None = None
        token: str | None = None
        scope: str | None = None

    @dataclasses.dataclass
    class Response:
        """
        Represent the response from a UiPath client method.

        Store the HTTP status code and the content returned by the UiPath Orchestrator API.

        Parameters
        ----------
        status_code : int
            HTTP status code returned by the API request.
        content : Any, optional
            Content of the response, typically a deserialized JSON object or None.

        Attributes
        ----------
        status_code : int
            HTTP status code of the response.
        content : Any
            Content of the response, if available.
        """

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

        Parameters
        ----------
        url_base : str
            Specify the base URL for the UiPath Orchestrator API.
        client_id : str
            Provide the client ID for authentication.
        refresh_token : str
            Provide the refresh token for authentication.
        scope : str
            Specify the scope for authentication.
        custom_logger : logging.Logger, optional
            Pass a custom logger instance to use. If None, create a default logger.

        Notes
        -----
        Set up logging, initialize the HTTP session, store credentials, and authenticate with the UiPath Orchestrator
        API.
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
        Finalize the SharePoint client instance and release resources.

        Close the internal HTTP session and log an informational message indicating cleanup.

        Parameters
        ----------
        self : SharePoint
            The SharePoint client instance.

        Returns
        -------
        None

        Notes
        -----
        This method is called when the instance is about to be destroyed. Ensure the HTTP session is closed and log
        cleanup.
        """
        self._logger.info(msg="Cleans the house at the exit")
        self._session.close()

    def is_auth(self) -> bool:
        """
        Check if authentication was successful.

        Returns
        -------
        bool
            True if authentication was successful, otherwise False.

        Notes
        -----
        Log the authentication status check.
        """
        self._logger.info(msg="Checking if authentication is being established with UiPath Orchestrator.")

        return False if self._configuration.token is None else True

    def auth(self) -> None:
        """
        Authenticate with the UiPath Orchestrator API and obtain an access token.

        Use the client credentials flow to request an access token from the UiPath identity endpoint.
        Store the access token in the configuration for use in subsequent API requests.
        Log the authentication process and HTTP response status.

        Parameters
        ----------
        self : SharePoint
            Instance of the SharePoint client.

        Returns
        -------
        None

        Raises
        ------
        requests.exceptions.RequestException
            If the HTTP request fails due to network issues, DNS resolution, or SSL errors.
        RuntimeError
            If the token endpoint returns a non-200 HTTP status code.
        ValueError
            If the response body does not contain a valid JSON access_token.
        """
        self._logger.info(msg="Authenticating with UiPath Orchestrator using client credentials.")

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

        Save the given bytes content to a file in binary mode if a file path is provided.

        Parameters
        ----------
        content : bytes
            Response content to export.
        save_as : str or None
            File path to save the JSON content. If None, do not save.

        Returns
        -------
        None
            This function does not return any value.

        Notes
        -----
        If `save_as` is specified, write the content to the file in binary mode.
        """
        if save_as is not None:
            self._logger.info(msg="Exports response to JSON file.")
            with open(file=save_as, mode="wb") as file:
                file.write(content)

    def _handle_response(
        self, response: requests.Response, model: Type[BaseModel], rtype: str = "scalar"
    ) -> dict | list[dict]:
        """
        Handle and deserialize the JSON content from an API response.

        Parameters
        ----------
        response : requests.Response
            Response object from the API request.
        model : Type[BaseModel]
            Pydantic BaseModel class for deserialization and validation.
        rtype : str, optional
            Specify "scalar" for a single record or "list" for a list of records. Default is "scalar".

        Returns
        -------
        dict or list of dict
            Deserialized content as a dictionary (for scalar) or a list of dictionaries (for list).

        Examples
        --------
        >>> self._handle_response(response, MyModel, rtype="scalar")
        {'field1': 'value1', 'field2': 'value2'}

        >>> self._handle_response(response, MyModel, rtype="list")
        [{'field1': 'value1'}, {'field1': 'value2'}]
        """
        if rtype.lower() == "scalar":
            # Deserialize json (scalar values)
            content_raw = response.json()
            # Pydantic v1 validation
            validated = model(**content_raw)
            # Convert to dict
            return validated.dict()

        # List of records
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
        Retrieve all assets from the UiPath Orchestrator.

        Parameters
        ----------
        fid : str
            Specify the folder ID for the organization unit.
        save_as : str or None, optional
            Provide the file path to save the JSON content. If None, do not save the content.

        Returns
        -------
        Response
            Return a dataclass containing the status code and the list of assets.
        """
        self._logger.info(msg="Retrieving all assets.")

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
        List all storage buckets in UiPath Orchestrator.

        Retrieve all storage buckets available in the specified organization unit (folder).
        Optionally, save the response content to a JSON file.

        Parameters
        ----------
        fid : str
            Folder ID for the organization unit.
        save_as : str or None, optional
            File path to save the JSON content. If None, do not save the content.

        Returns
        -------
        Response
            Dataclass containing the status code and the list of buckets.
        """
        self._logger.info(msg="Retrieving the list of all storage buckets.")

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
        Create a new storage bucket in UiPath Orchestrator.

        Generate a GUID using an online generator if needed:
        https://www.guidgenerator.com/online-guid-generator.aspx

        Parameters
        ----------
        fid : str
            Specify the folder ID for the organization unit.
        name : str
            Specify the name of the storage bucket.
        guid : str
            Specify the unique identifier (GUID) for the storage bucket.
        description : str, optional
            Provide a description for the storage bucket. Default is None.

        Returns
        -------
        Response
            Dataclass containing the status code and the response content.
        """
        self._logger.info(msg="Creating a new storage bucket.")
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
        Delete a storage bucket from UiPath Orchestrator.

        Parameters
        ----------
        fid : str
            Specify the folder ID for the organization unit.
        id : str
            Specify the ID of the storage bucket to delete.

        Returns
        -------
        Response
            Dataclass containing the status code and the response content.
        """
        self._logger.info(msg="Deleting the specified storage bucket.")
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
        Upload a file to a storage bucket in UiPath Orchestrator.

        Obtain a write URI for the specified file path in the target bucket and upload the local file to the remote
        storage location.

        Parameters
        ----------
        fid : str
            Specify the folder ID for the organization unit.
        id : str
            Specify the storage bucket ID.
        localpath : str
            Specify the local file path to upload.
        remotepath : str
            Specify the file name or path in the storage bucket.

        Returns
        -------
        Response
            Dataclass containing the status code and the response content.
        """
        self._logger.info(msg="Uploading file to the specified bucket.")
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
        Delete a file from a storage bucket in UiPath Orchestrator.

        Remove the specified file from the given storage bucket within the specified organization unit (folder).

        Parameters
        ----------
        fid : str
            Folder ID for the organization unit.
        id : str
            Storage bucket ID.
        filename : str
            Name of the file to delete.

        Returns
        -------
        Response
            Dataclass containing the status code and the response content.
        """
        self._logger.info(msg="Deleting the specified file from the storage bucket.")
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
        Retrieve all calendars from the UiPath Orchestrator.

        Parameters
        ----------
        fid : str
            Specify the folder ID for the organization unit.
        save_as : str, optional
            Specify the file path to save the JSON content. If None, do not save the content.

        Returns
        -------
        Response
            Dataclass containing the status code and the list of calendars.
        """
        self._logger.info(msg="Retrieving all calendars.")

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
        Retrieve all environments from the UiPath Orchestrator.

        Parameters
        ----------
        fid : str
            Specify the folder ID for the organization unit.
        save_as : str, optional
            Specify the file path to save the JSON content. If None, do not save the content.

        Returns
        -------
        Response
            Dataclass containing the status code and the list of environments.
        """
        self._logger.info(msg="Retrieving all environments.")

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
        Retrieve jobs from the UiPath Orchestrator using a filter.

        Apply an OData filter to select jobs matching specific criteria within a given organization unit (folder).
        Optionally, save the response content to a JSON file.

        Parameters
        ----------
        fid : str
            Specify the folder ID for the organization unit.
        filter : str
            Provide the OData filter condition. For example, "State eq 'Running'".
        save_as : str or None, optional
            Specify the file path to save the JSON content. If None, do not save the content.

        Returns
        -------
        Response
            Return a dataclass containing the status code and the list of jobs.
        """

        self._logger.info(msg="Retrieving jobs using the provided filter criteria.")
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
        Start a job in UiPath Orchestrator using a process key and an optional robot ID.

        Initiate a job for the specified process in the given organization unit (folder).
        If a robot ID is provided, run the job on that specific robot; otherwise, run the job on any available robot.

        Parameters
        ----------
        fid : str
            Specify the folder ID for the organization unit.
        process_key : str
            Specify the process key. Use the 'key' column from the list_releases function.
        robot_id : int, optional
            Specify the robot ID to run the job on a specific robot. If None, run the job on any available robot.

        Returns
        -------
        Response
            Return a dataclass containing the status code and the response content.
        """
        self._logger.info(msg="Initiating the process of starting a job.")
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
        Stop a job in UiPath Orchestrator using a job ID.

        Stop the specified job in the given organization unit (folder) by sending a stop request to the UiPath
        Orchestrator API.

        Parameters
        ----------
        fid : str
            Specify the folder ID for the organization unit.
        id : str
            Specify the job ID to stop.

        Returns
        -------
        Response
            Return a dataclass containing the status code and the response content.
        """
        self._logger.info(msg="Stopping the specified job.")
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
        Retrieve all machines from the UiPath Orchestrator.

        Parameters
        ----------
        fid : str
            Specify the folder ID for the organization unit.
        save_as : str, optional
            Specify the file path to save the JSON content. If None, do not save the content.

        Returns
        -------
        Response
            Dataclass containing the status code and the list of machines.
        """
        self._logger.info(msg="Retrieving a list of all machines.")

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
        Retrieve all processes from the UiPath Orchestrator.

        Parameters
        ----------
        fid : str
            Specify the folder ID for the organization unit.
        save_as : str, optional
            Specify the file path to save the JSON content. If None, do not save the content.

        Returns
        -------
        Response
            Dataclass containing the status code and the list of processes.
        """
        self._logger.info(msg="Retrieving a comprehensive list of all processes.")

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

        Parameters
        ----------
        fid : str
            Specify the folder ID for the organization unit.
        save_as : str, optional
            Specify the file path to save the JSON content. If None, do not save the content.

        Returns
        -------
        Response
            Dataclass containing the status code and the list of queues.
        """
        self._logger.info(msg="Retrieving a comprehensive list of all queues.")

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

        Parameters
        ----------
        fid : str
            Folder ID for the organization unit.
        filter : str
            OData filter condition to select the queue and item status.
            Example: "QueueDefinitionId eq 1 and Status eq 'New'"
        save_as : str or None, optional
            File path to save the JSON content. If None, do not save the content.

        Returns
        -------
        Response
            Dataclass containing the status code and the list of queue items.
        """
        self._logger.info(msg="Retrieving a list of queue items using the provided filter criteria.")
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

        Parameters
        ----------
        fid : str
            Folder ID for the organization unit.
        id : int
            ID of the queue item to retrieve (transaction ID).
        save_as : str, optional
            File path to save the JSON content. If None, do not save the content.

        Returns
        -------
        Response
            Dataclass containing the status code and the details of the queue item.
        """
        self._logger.info(msg="Retrieving details for the specified queue item from the queue.")
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

        Insert a new item into the specified queue within the given organization unit (folder).
        Set the item's reference, priority, and custom data fields. Optionally, save the response content to a JSON
        file.

        Parameters
        ----------
        fid : str
            Specify the folder ID for the organization unit.
        queue : str
            Specify the name of the queue.
        data : dict
            Provide a dictionary containing the item information.
        reference : str
            Specify a unique reference for the queue item.
        priority : str, optional
            Set the priority of the queue item. Default is "Normal".
        save_as : str or None, optional
            Specify the file path to save the JSON content. If None, do not save the content.

        Returns
        -------
        Response
            Dataclass containing the status code and the response content.
        """
        self._logger.info(msg="Adding an item to the queue.")
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

        Modify the specified queue item with new data in the given organization unit (folder).

        Parameters
        ----------
        fid : str
            Folder ID for the organization unit.
        queue : str
            Name of the queue.
            Example: queue="ElegibilityQueueNAM"
        id : int
            ID of the queue item to update.
            Example: id=1489001
        data : dict
            Dictionary containing the updated item information.
            Example: content={"PRCode": "PR1234"}

        Returns
        -------
        Response
            Dataclass containing the status code and the response content.
        """
        self._logger.info(msg="Updating a queue item in the queue.")
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

        Remove the specified queue item from the given organization unit (folder) by sending a DELETE request to the
        UiPath Orchestrator API.

        Parameters
        ----------
        fid : str
            Folder ID for the organization unit.
        id : int
            ID of the queue item to delete (transaction ID).

        Returns
        -------
        Response
            Dataclass containing the status code and the response content.
        """
        self._logger.info(msg="Deleting the specified queue item from the queue.")
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
        Retrieve all process releases from the UiPath Orchestrator.

        Parameters
        ----------
        fid : str
            Specify the folder ID for the organization unit.
        save_as : str, optional
            Specify the file path to save the JSON content. If None, do not save the content.

        Returns
        -------
        Response
            Dataclass containing the status code and the list of releases.
        """
        self._logger.info(msg="Retrieving the list of all process releases.")

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
        Retrieve all robots from the UiPath Orchestrator.

        Parameters
        ----------
        fid : str
            Specify the folder ID for the organization unit.
        save_as : str, optional
            Specify the file path to save the JSON content. If None, do not save the content.

        Returns
        -------
        Response
            Dataclass containing the status code and the list of robots.
        """
        self._logger.info(msg="Retrieving a comprehensive list of all robots.")

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
        Retrieve robot logs from the UiPath Orchestrator.

        Apply a filter to select robot logs matching specific criteria within a given organization unit (folder).
        Optionally, save the response content to a JSON file.

        Parameters
        ----------
        fid : str
            Specify the folder ID for the organization unit.
        filter : str
            Provide the OData filter condition. For example, "JobKey eq 'bde11c1e-11e1-1bb1-11d1-e11f111111db'".
        save_as : str or None, optional
            Specify the file path to save the JSON content. If None, do not save the content.

        Returns
        -------
        Response
            Dataclass containing the status code and the list of robot logs.
        """
        self._logger.info(msg="Retrieving robot logs based on the provided filter criteria.")

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
        Retrieve all roles from the UiPath Orchestrator.

        Fetch the list of all roles available in the UiPath Orchestrator instance.
        Optionally, save the response content to a JSON file.

        Parameters
        ----------
        save_as : str, optional
            File path to save the JSON content. If None, do not save the content.

        Returns
        -------
        Response
            Dataclass containing the status code and the list of roles.
        """
        self._logger.info(msg="Retrieving a comprehensive list of all roles.")

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
        Retrieve all schedules from the UiPath Orchestrator.

        Parameters
        ----------
        fid : str
            Specify the folder ID for the organization unit.
        save_as : str, optional
            Specify the file path to save the JSON content. If None, do not save the content.

        Returns
        -------
        Response
            Dataclass containing the status code and the list of schedules.
        """
        self._logger.info(msg="Retrieving a comprehensive list of all schedules.")

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
        Retrieve all sessions from the UiPath Orchestrator.

        Fetch the list of all sessions available in the specified organization unit (folder).
        Optionally, save the response content to a JSON file.

        Parameters
        ----------
        fid : str
            Specify the folder ID for the organization unit.
        save_as : str, optional
            Specify the file path to save the JSON content. If None, do not save the content.

        Returns
        -------
        Response
            Dataclass containing the status code and the list of sessions.
        """
        self._logger.info(msg="Retrieving a comprehensive list of all active sessions.")

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


# eof
