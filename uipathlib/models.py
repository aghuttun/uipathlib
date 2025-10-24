"""
Pydantic data structures for SharePoint entities.
"""

from datetime import datetime
from pydantic import BaseModel, Field, validator


class ListAssets(BaseModel):
    """Pydantic data structure for list_assets()."""

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
    """Pydantic data structure for list_buckets()."""

    id: int = Field(alias="Id")
    identifier: str = Field(alias="Identifier")
    name: str = Field(alias="Name")
    description: str | None = Field(alias="Description", default=None)


class ListCalendars(BaseModel):
    """Pydantic data structure for list_calendars()."""

    id: int = Field(alias="Id")
    name: str = Field(alias="Name")
    excluded_dates: list = Field(alias="ExcludedDates")
    time_zone_id: str | None = Field(alias="TimeZoneId", default=None)


class ListEnvironments(BaseModel):
    """Pydantic data structure for list_environments()."""

    id: int = Field(alias="Id")
    name: str = Field(alias="Name")
    type: str = Field(alias="Type")
    description: str | None = Field(alias="Description", default=None)


class ListJobs(BaseModel):
    """Pydantic data structure for list_jobs()."""

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
    """Pydantic data structure for list_machines()."""

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
    """Pydantic data structure for list_processes()."""

    id: str = Field(alias="Id")
    # title: str = Field(alias="Title")
    key: str = Field(alias="Key")
    version: str = Field(alias="Version")
    published: datetime = Field(alias="Published")
    authors: str = Field(alias="Authors")
    description: str | None = Field(alias="Description", default=None)


class ListQueues(BaseModel):
    """Pydantic data structure for list_queues()."""

    id: int = Field(alias="Id")
    name: str = Field(alias="Name")
    description: str | None = Field(alias="Description", default=None)


class ListQueueItems(BaseModel):
    """Pydantic data structure for list_queue_items()."""

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
    """Pydantic data structure for get_queue_item()."""

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
    """Pydantic data structure for add_queue_item()."""

    id: int = Field(alias="Id")
    organization_unit_id: int = Field(alias="OrganizationUnitId")
    queue_definition_id: int = Field(alias="QueueDefinitionId")


class ListReleases(BaseModel):
    """Pydantic data structure for list_releases()."""

    id: int = Field(alias="Id")
    key: str = Field(alias="Key")
    process_key: str = Field(alias="ProcessKey")
    process_version: str = Field(alias="ProcessVersion")
    environment_id: str | None = Field(alias="EnvironmentId", default=None)


class ListRobots(BaseModel):
    """Pydantic data structure for list_robots()."""

    id: int = Field(alias="Id")
    machine_name: str | None = Field(alias="MachineName", default=None)
    name: str = Field(alias="Name")
    username: str = Field(alias="Username")
    type: str = Field(alias="Type")
    robot_environments: str = Field(alias="RobotEnvironments")


class ListRobotLogs(BaseModel):
    """Pydantic data structure for list_robot_logs()."""

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
    """Pydantic data structure for list_roles()."""

    id: int = Field(alias="Id")
    name: str = Field(alias="Name")
    display_name: str = Field(alias="DisplayName")
    type: str = Field(alias="Type")


class ListSchedules(BaseModel):
    """Pydantic data structure for list_schedules()."""

    id: int = Field(alias="Id")
    name: str = Field(alias="Name")
    package_name: str = Field(alias="PackageName")
    environment_id: str | None = Field(alias="EnvironmentId", default=None)
    environment_name: str | None = Field(alias="EnvironmentName", default=None)
    start_process_cron: str = Field(alias="StartProcessCron")
    start_process_cron_summary: str = Field(alias="StartProcessCronSummary")
    enabled: bool = Field(alias="Enabled")


class ListSessions(BaseModel):
    """Pydantic data structure for list_sessions()."""

    id: int = Field(alias="Id")
    machine_id: str = Field(alias="MachineId")
    host_machine_name: str = Field(alias="HostMachineName")
    machine_name: str = Field(alias="MachineName")
    state: str = Field(alias="State")
    reporting_time: str = Field(alias="ReportingTime")
    organization_unit_id: str | None = Field(alias="OrganizationUnitId", default=None)
    folder_name: str | None = Field(alias="FolderName", default=None)


# eom
