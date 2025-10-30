"""
Define Pydantic data structures for UiPath Orchestrator entities.

This module provides Pydantic models for various UiPath Orchestrator-related entities, including assets, buckets,
calendars, environments, jobs, machines, processes, queues, queue items, releases, robots, robot logs, roles, schedules,
and sessions.
Use these models to validate and serialize data exchanged with UiPath Orchestrator APIs.

Notes
-----
- All models use field aliases to match UiPath Orchestrator API field names.
- Some fields are optional and default to None if not provided.
- Validators are included where necessary to transform or extract data.
"""

from datetime import datetime
from pydantic import BaseModel, Field, validator


class ListAssets(BaseModel):
    """
    Define the data structure for list_assets() responses.

    Specify fields for UiPath Orchestrator asset metadata, including identifiers, names, external names, default value
    status, values, value scopes, value types, integer values, string values, boolean values, credential usernames,
    credential store IDs, deletability, and descriptions.

    Parameters
    ----------
    id : int
        Specify the unique identifier of the asset.
    name : str
        Specify the name of the asset.
    external_name : str, optional
        Specify the external name of the asset, if available.
    has_default_value : bool
        Indicate whether the asset has a default value.
    value : str
        Specify the value of the asset.
    value_scope : str
        Specify the scope of the asset value.
    value_type : str
        Specify the type of the asset value.
    int_value : int
        Specify the integer value of the asset.
    string_value : str
        Specify the string value of the asset.
    bool_value : bool
        Indicate the boolean value of the asset.
    credential_username : str
        Specify the username for credential assets.
    credential_store_id : int, optional
        Specify the credential store ID, if applicable.
    can_be_deleted : bool
        Indicate whether the asset can be deleted.
    description : str, optional
        Specify the description of the asset.
    """

    id: int = Field(alias="Id")
    name: str = Field(alias="Name")
    external_name: str | None = Field(alias="ExternalName", default=None)
    has_default_value: bool = Field(alias="HasDefaultValue")
    value: str = Field(alias="Value")
    value_scope: str = Field(alias="ValueScope")
    value_type: str = Field(alias="ValueType")
    int_value: int = Field(alias="IntValue")
    string_value: str = Field(alias="StringValue")
    bool_value: bool = Field(alias="BoolValue")
    credential_username: str = Field(alias="CredentialUsername")
    credential_store_id: int | None = Field(alias="CredentialStoreId", default=None)
    can_be_deleted: bool = Field(alias="CanBeDeleted")
    description: str | None = Field(alias="Description", default=None)


class ListBuckets(BaseModel):
    """
    Define the data structure for list_buckets() responses.

    Specify fields for UiPath Orchestrator bucket metadata, including identifiers, names, and descriptions.

    Parameters
    ----------
    id : int
        Specify the unique identifier of the bucket.
    identifier : str
        Specify the unique string identifier of the bucket.
    name : str
        Specify the name of the bucket.
    description : str, optional
        Specify the description of the bucket, if available.
    """

    id: int = Field(alias="Id")
    identifier: str = Field(alias="Identifier")
    name: str = Field(alias="Name")
    description: str | None = Field(alias="Description", default=None)


class ListCalendars(BaseModel):
    """
    Define the data structure for list_calendars() responses.

    Specify fields for UiPath Orchestrator calendar metadata, including identifiers, names, excluded dates, and time
    zone IDs.

    Parameters
    ----------
    id : int
        Specify the unique identifier of the calendar.
    name : str
        Specify the name of the calendar.
    excluded_dates : list
        List the dates excluded from the calendar.
    time_zone_id : str, optional
        Specify the time zone ID of the calendar, if available.
    """

    id: int = Field(alias="Id")
    name: str = Field(alias="Name")
    excluded_dates: list = Field(alias="ExcludedDates")
    time_zone_id: str | None = Field(alias="TimeZoneId", default=None)


class ListEnvironments(BaseModel):
    """
    Define the data structure for list_environments() responses.

    Specify fields for UiPath Orchestrator environment metadata, including identifiers, names, types, and descriptions.

    Parameters
    ----------
    id : int
        Specify the unique identifier of the environment.
    name : str
        Specify the name of the environment.
    type : str
        Specify the type of the environment.
    description : str, optional
        Specify the description of the environment, if available.
    """

    id: int = Field(alias="Id")
    name: str = Field(alias="Name")
    type: str = Field(alias="Type")
    description: str | None = Field(alias="Description", default=None)


class ListJobs(BaseModel):
    """
    Define the data structure for list_jobs() responses.

    Specify fields for UiPath Orchestrator job metadata, including identifiers, keys, release names, host machine names,
    types, starting schedule IDs, creation times, start times, end times, states, and sources.

    Parameters
    ----------
    id : int
        Specify the unique identifier of the job.
    key : str
        Specify the unique key of the job.
    release_name : str
        Specify the name of the release associated with the job.
    host_machine_name : str, optional
        Specify the name of the host machine, if available.
    type : str
        Specify the type of the job.
    starting_schedule_id : int, optional
        Specify the starting schedule ID, if applicable.
    creation_time : datetime, optional
        Specify the creation time of the job, if available.
    start_time : datetime, optional
        Specify the start time of the job, if available.
    end_time : datetime, optional
        Specify the end time of the job, if available.
    state : str
        Specify the current state of the job.
    source : str
        Specify the source of the job.
    """

    id: int = Field(alias="Id")
    key: str = Field(alias="Key")
    release_name: str = Field(alias="ReleaseName")
    host_machine_name: str | None = Field(alias="HostMachineName", default=None)
    type: str = Field(alias="Type")
    starting_schedule_id: int | None = Field(alias="StartingScheduleId", default=None)
    creation_time: datetime | None = Field(alias="CreationTime", default=None)
    start_time: datetime | None = Field(alias="StartTime", default=None)
    end_time: datetime | None = Field(alias="EndTime", default=None)
    state: str = Field(alias="State")
    source: str = Field(alias="Source")


class ListMachines(BaseModel):
    """
    Define the data structure for list_machines() responses.

    Specify fields for UiPath Orchestrator machine metadata, including identifiers, names, descriptions, types,
    non-production slots, unattended slots, and robot versions.

    Parameters
    ----------
    id : int
        Specify the unique identifier of the machine.
    name : str
        Specify the name of the machine.
    description : str, optional
        Specify the description of the machine, if available.
    type : str
        Specify the type of the machine.
    non_production_slots : int
        Specify the number of non-production slots for the machine.
    unattended_slots : int
        Specify the number of unattended slots for the machine.
    robot_versions : str, optional
        Specify the robot version for the machine, if available.
    """

    id: int = Field(alias="Id")
    name: str = Field(alias="Name")
    description: str | None = Field(alias="Description", default=None)
    type: str = Field(alias="Type")
    non_production_slots: int = Field(alias="NonProductionSlots")
    unattended_slots: int = Field(alias="UnattendedSlots")
    robot_versions: str | None = Field(alias="RobotVersions", default=None)

    # @field_validator("RobotVersions", mode="before")
    # @classmethod
    @validator("robot_versions", pre=True)
    def extract_robot_version(cls, value):
        # if len(value) > 0:
        #     return value[0]["Version"]
        if isinstance(value, list) and len(value) > 0 and isinstance(value[0], dict):
            return value[0].get("Version")
        return None


class ListProcesses(BaseModel):
    """
    Define the data structure for list_processes() responses.

    Specify fields for UiPath Orchestrator process metadata, including identifiers, keys, versions, published dates,
    authors, and descriptions.

    Parameters
    ----------
    id : str
        Specify the unique identifier of the process.
    key : str
        Specify the unique key of the process.
    version : str
        Specify the version of the process.
    published : datetime
        Specify the published date of the process.
    authors : str
        Specify the authors of the process.
    description : str, optional
        Specify the description of the process, if available.
    """

    id: str = Field(alias="Id")
    # title: str = Field(alias="Title")
    key: str = Field(alias="Key")
    version: str = Field(alias="Version")
    published: datetime = Field(alias="Published")
    authors: str = Field(alias="Authors")
    description: str | None = Field(alias="Description", default=None)


class ListQueues(BaseModel):
    """
    Define the data structure for list_queues() responses.

    Specify fields for UiPath Orchestrator queue metadata, including identifiers, names, and descriptions.

    Parameters
    ----------
    id : int
        Specify the unique identifier of the queue.
    name : str
        Specify the name of the queue.
    description : str, optional
        Specify the description of the queue, if available.
    """

    id: int = Field(alias="Id")
    name: str = Field(alias="Name")
    description: str | None = Field(alias="Description", default=None)


class ListQueueItems(BaseModel):
    """
    Define the data structure for list_queue_items() responses.

    Specify fields for UiPath Orchestrator queue item metadata, including identifiers, queue definition IDs, statuses,
    references, creation times, processing start and end times, retry numbers, and specific data.

    Parameters
    ----------
    id : int
        Specify the unique identifier of the queue item.
    queue_definition_id : int
        Specify the unique identifier of the queue definition.
    status : str
        Specify the status of the queue item.
    reference : str
        Specify the reference associated with the queue item.
    creation_time : datetime
        Specify the creation time of the queue item.
    start_processing : datetime, optional
        Specify the time when processing started, if available.
    end_processing : datetime, optional
        Specify the time when processing ended, if available.
    retry_number : int
        Specify the retry number for the queue item.
    specific_data : str
        Specify the specific data associated with the queue item.
    """

    id: int = Field(alias="Id")
    queue_definition_id: int = Field(alias="QueueDefinitionId")
    status: str = Field(alias="Status")
    reference: str = Field(alias="Reference")
    creation_time: datetime = Field(alias="CreationTime")
    start_processing: datetime | None = Field(alias="StartProcessing", default=None)
    end_processing: datetime | None = Field(alias="EndProcessing", default=None)
    retry_number: int = Field(alias="RetryNumber")
    specific_data: str = Field(alias="SpecificData")


class GetQueueItem(BaseModel):
    """
    Define the data structure for get_queue_item() responses.

    Specify fields for UiPath Orchestrator queue item metadata, including identifiers, queue definition IDs, statuses,
    references, creation times, processing start and end times, retry numbers, and specific data.

    Parameters
    ----------
    id : int
        Specify the unique identifier of the queue item.
    queue_definition_id : int
        Specify the unique identifier of the queue definition.
    status : str
        Specify the status of the queue item.
    reference : str
        Specify the reference associated with the queue item.
    creation_time : datetime
        Specify the creation time of the queue item.
    start_processing : datetime, optional
        Specify the time when processing started, if available.
    end_processing : datetime, optional
        Specify the time when processing ended, if available.
    retry_number : int
        Specify the retry number for the queue item.
    specific_data : str
        Specify the specific data associated with the queue item.
    """

    id: int = Field(alias="Id")
    queue_definition_id: int = Field(alias="QueueDefinitionId")
    status: str = Field(alias="Status")
    reference: str = Field(alias="Reference")
    creation_time: datetime = Field(alias="CreationTime")
    start_processing: datetime | None = Field(alias="StartProcessing", default=None)
    end_processing: datetime | None = Field(alias="EndProcessing", default=None)
    retry_number: int = Field(alias="RetryNumber")
    specific_data: str = Field(alias="SpecificData")


class AddQueueItem(BaseModel):
    """
    Define the data structure for add_queue_item() responses.

    Specify fields for UiPath Orchestrator queue item creation metadata, including identifiers, organization unit IDs,
    and queue definition IDs.

    Parameters
    ----------
    id : int
        Specify the unique identifier of the queue item.
    organization_unit_id : int
        Specify the unique identifier of the organization unit.
    queue_definition_id : int
        Specify the unique identifier of the queue definition.
    """

    id: int = Field(alias="Id")
    organization_unit_id: int = Field(alias="OrganizationUnitId")
    queue_definition_id: int = Field(alias="QueueDefinitionId")


class ListReleases(BaseModel):
    """
    Define the data structure for list_releases() responses.

    Specify fields for UiPath Orchestrator release metadata, including identifiers, keys, process keys, process
    versions, and environment IDs.

    Parameters
    ----------
    id : int
        Specify the unique identifier of the release.
    key : str
        Specify the unique key of the release.
    process_key : str
        Specify the unique key of the process.
    process_version : str
        Specify the version of the process.
    environment_id : str, optional
        Specify the environment ID associated with the release, if available.
    """

    id: int = Field(alias="Id")
    key: str = Field(alias="Key")
    process_key: str = Field(alias="ProcessKey")
    process_version: str = Field(alias="ProcessVersion")
    environment_id: str | None = Field(alias="EnvironmentId", default=None)


class ListRobots(BaseModel):
    """
    Define the data structure for list_robots() responses.

    Specify fields for UiPath Orchestrator robot metadata, including identifiers, machine names, names, usernames,
    types, and robot environments.

    Parameters
    ----------
    id : int
        Specify the unique identifier of the robot.
    machine_name : str, optional
        Specify the name of the machine associated with the robot, if available.
    name : str
        Specify the name of the robot.
    username : str
        Specify the username of the robot.
    type : str
        Specify the type of the robot.
    robot_environments : str
        Specify the environments associated with the robot.
    """

    id: int = Field(alias="Id")
    machine_name: str | None = Field(alias="MachineName", default=None)
    name: str = Field(alias="Name")
    username: str = Field(alias="Username")
    type: str = Field(alias="Type")
    robot_environments: str = Field(alias="RobotEnvironments")


class ListRobotLogs(BaseModel):
    """
    Define the data structure for list_robot_logs() responses.

    Specify fields for UiPath Orchestrator robot log metadata, including identifiers, job keys, log levels, Windows
    identities, process names, timestamps, messages, robot names, and machine IDs.

    Parameters
    ----------
    id : int
        Specify the unique identifier of the robot log.
    job_key : str
        Specify the unique key of the job associated with the log.
    level : str
        Specify the log level.
    windows_identity : str
        Specify the Windows identity associated with the log.
    process_name : str
        Specify the name of the process that generated the log.
    time_stamp : str
        Specify the timestamp of the log entry.
    message : str
        Specify the log message.
    robot_name : str
        Specify the name of the robot that generated the log.
    Machine_id : int
        Specify the unique identifier of the machine associated with the log.
    """

    id: int = Field(alias="Id")
    job_key: str = Field(alias="JobKey")
    level: str = Field(alias="Level")
    windows_identity: str = Field(alias="WindowsIdentity")
    process_name: str = Field(alias="ProcessName")
    time_stamp: str = Field(alias="TimeStamp")
    message: str = Field(alias="Message")
    robot_name: str = Field(alias="RobotName")
    Machine_id: int = Field(alias="MachineId")


class ListRoles(BaseModel):
    """
    Define the data structure for list_roles() responses.

    Specify fields for UiPath Orchestrator role metadata, including identifiers, names, display names, and types.

    Parameters
    ----------
    id : int
        Specify the unique identifier of the role.
    name : str
        Specify the name of the role.
    display_name : str
        Specify the display name of the role.
    type : str
        Specify the type of the role.
    """

    id: int = Field(alias="Id")
    name: str = Field(alias="Name")
    display_name: str = Field(alias="DisplayName")
    type: str = Field(alias="Type")


class ListSchedules(BaseModel):
    """
    Define the data structure for list_schedules() responses.

    Specify fields for UiPath Orchestrator schedule metadata, including identifiers, names, package names, environment
    IDs and names, cron expressions, cron summaries, and enabled status.

    Parameters
    ----------
    id : int
        Specify the unique identifier of the schedule.
    name : str
        Specify the name of the schedule.
    package_name : str
        Specify the name of the package associated with the schedule.
    environment_id : str, optional
        Specify the environment ID associated with the schedule, if available.
    environment_name : str, optional
        Specify the environment name associated with the schedule, if available.
    start_process_cron : str
        Specify the cron expression for the schedule.
    start_process_cron_summary : str
        Specify the summary of the cron expression.
    enabled : bool
        Indicate whether the schedule is enabled.
    """

    id: int = Field(alias="Id")
    name: str = Field(alias="Name")
    package_name: str = Field(alias="PackageName")
    environment_id: str | None = Field(alias="EnvironmentId", default=None)
    environment_name: str | None = Field(alias="EnvironmentName", default=None)
    start_process_cron: str = Field(alias="StartProcessCron")
    start_process_cron_summary: str = Field(alias="StartProcessCronSummary")
    enabled: bool = Field(alias="Enabled")


class ListSessions(BaseModel):
    """
    Define the data structure for list_sessions() responses.

    Specify fields for UiPath Orchestrator session metadata, including identifiers, machine IDs, host machine names,
    machine names, states, reporting times, organization unit IDs, and folder names.

    Parameters
    ----------
    id : int
        Specify the unique identifier of the session.
    machine_id : str, optional
        Specify the unique identifier of the machine, if available.
    host_machine_name : str
        Specify the name of the host machine.
    machine_name : str, optional
        Specify the name of the machine, if available.
    state : str
        Specify the current state of the session.
    reporting_time : str
        Specify the reporting time of the session.
    organization_unit_id : str, optional
        Specify the unique identifier of the organization unit, if available.
    folder_name : str, optional
        Specify the name of the folder, if available.
    """

    id: int = Field(alias="Id")
    machine_id: str | None = Field(alias="MachineId", default=None)
    host_machine_name: str = Field(alias="HostMachineName")
    machine_name: str | None = Field(alias="MachineName", default=None)
    state: str = Field(alias="State")
    reporting_time: str = Field(alias="ReportingTime")
    organization_unit_id: str | None = Field(alias="OrganizationUnitId", default=None)
    folder_name: str | None = Field(alias="FolderName", default=None)


# eom
