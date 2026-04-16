use serde::Deserialize;
use serde::Serialize;
use serde_json::Value;

#[derive(Debug, Clone, Deserialize)]
pub(crate) struct AuthTokenResponse {
    pub access_token: String,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ListAssets {
    #[serde(rename = "Id")]
    pub id: i64,
    #[serde(rename = "Name")]
    pub name: String,
    #[serde(rename = "ExternalName")]
    pub external_name: Option<String>,
    #[serde(rename = "HasDefaultValue")]
    pub has_default_value: bool,
    #[serde(rename = "Value")]
    pub value: Option<String>,
    #[serde(rename = "ValueScope")]
    pub value_scope: Option<String>,
    #[serde(rename = "ValueType")]
    pub value_type: Option<String>,
    #[serde(rename = "IntValue")]
    pub int_value: Option<i64>,
    #[serde(rename = "StringValue")]
    pub string_value: Option<String>,
    #[serde(rename = "BoolValue")]
    pub bool_value: Option<bool>,
    #[serde(rename = "CredentialUsername")]
    pub credential_username: Option<String>,
    #[serde(rename = "CredentialStoreId")]
    pub credential_store_id: Option<i64>,
    #[serde(rename = "CanBeDeleted")]
    pub can_be_deleted: Option<bool>,
    #[serde(rename = "Description")]
    pub description: Option<String>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ListBuckets {
    #[serde(rename = "Id")]
    pub id: i64,
    #[serde(rename = "Identifier")]
    pub identifier: String,
    #[serde(rename = "Name")]
    pub name: String,
    #[serde(rename = "Description")]
    pub description: Option<String>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ListCalendars {
    #[serde(rename = "Id")]
    pub id: i64,
    #[serde(rename = "Name")]
    pub name: String,
    #[serde(rename = "ExcludedDates")]
    pub excluded_dates: Vec<Value>,
    #[serde(rename = "TimeZoneId")]
    pub time_zone_id: Option<String>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ListEnvironments {
    #[serde(rename = "Id")]
    pub id: i64,
    #[serde(rename = "Name")]
    pub name: String,
    #[serde(rename = "Type")]
    pub kind: String,
    #[serde(rename = "Description")]
    pub description: Option<String>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ListJobs {
    #[serde(rename = "Id")]
    pub id: i64,
    #[serde(rename = "Key")]
    pub key: String,
    #[serde(rename = "ReleaseName")]
    pub release_name: String,
    #[serde(rename = "HostMachineName")]
    pub host_machine_name: Option<String>,
    #[serde(rename = "Type")]
    pub kind: String,
    #[serde(rename = "StartingScheduleId")]
    pub starting_schedule_id: Option<i64>,
    #[serde(rename = "CreationTime")]
    pub creation_time: Option<String>,
    #[serde(rename = "StartTime")]
    pub start_time: Option<String>,
    #[serde(rename = "EndTime")]
    pub end_time: Option<String>,
    #[serde(rename = "State")]
    pub state: String,
    #[serde(rename = "Source")]
    pub source: String,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ListMachines {
    #[serde(rename = "Id")]
    pub id: i64,
    #[serde(rename = "Name")]
    pub name: String,
    #[serde(rename = "Description")]
    pub description: Option<String>,
    #[serde(rename = "Type")]
    pub kind: String,
    #[serde(rename = "NonProductionSlots")]
    pub non_production_slots: Option<i64>,
    #[serde(rename = "UnattendedSlots")]
    pub unattended_slots: Option<i64>,
    #[serde(
        rename = "RobotVersions",
        default,
        deserialize_with = "deserialize_robot_versions"
    )]
    pub robot_versions: Option<String>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ListProcesses {
    #[serde(rename = "Id")]
    pub id: String,
    #[serde(rename = "Key")]
    pub key: String,
    #[serde(rename = "Version")]
    pub version: String,
    #[serde(rename = "Published")]
    pub published: String,
    #[serde(rename = "Authors")]
    pub authors: String,
    #[serde(rename = "Description")]
    pub description: Option<String>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ListQueues {
    #[serde(rename = "Id")]
    pub id: i64,
    #[serde(rename = "Name")]
    pub name: String,
    #[serde(rename = "Description")]
    pub description: Option<String>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ListQueueItems {
    #[serde(rename = "Id")]
    pub id: i64,
    #[serde(rename = "QueueDefinitionId")]
    pub queue_definition_id: i64,
    #[serde(rename = "Status")]
    pub status: String,
    #[serde(rename = "Reference")]
    pub reference: Option<String>,
    #[serde(rename = "CreationTime")]
    pub creation_time: String,
    #[serde(rename = "StartProcessing")]
    pub start_processing: Option<String>,
    #[serde(rename = "EndProcessing")]
    pub end_processing: Option<String>,
    #[serde(rename = "RetryNumber")]
    pub retry_number: Option<i64>,
    #[serde(rename = "SpecificData")]
    pub specific_data: Option<Value>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct GetQueueItem {
    #[serde(rename = "Id")]
    pub id: i64,
    #[serde(rename = "QueueDefinitionId")]
    pub queue_definition_id: i64,
    #[serde(rename = "Status")]
    pub status: String,
    #[serde(rename = "Reference")]
    pub reference: Option<String>,
    #[serde(rename = "CreationTime")]
    pub creation_time: String,
    #[serde(rename = "StartProcessing")]
    pub start_processing: Option<String>,
    #[serde(rename = "EndProcessing")]
    pub end_processing: Option<String>,
    #[serde(rename = "RetryNumber")]
    pub retry_number: Option<i64>,
    #[serde(rename = "SpecificData")]
    pub specific_data: Option<Value>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct AddQueueItem {
    #[serde(rename = "Id")]
    pub id: i64,
    #[serde(rename = "OrganizationUnitId")]
    pub organization_unit_id: i64,
    #[serde(rename = "QueueDefinitionId")]
    pub queue_definition_id: i64,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ListReleases {
    #[serde(rename = "Id")]
    pub id: i64,
    #[serde(rename = "Key")]
    pub key: String,
    #[serde(rename = "ProcessKey")]
    pub process_key: Option<String>,
    #[serde(rename = "ProcessVersion")]
    pub process_version: Option<String>,
    #[serde(rename = "EnvironmentId")]
    pub environment_id: Option<String>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ListRobots {
    #[serde(rename = "Id")]
    pub id: i64,
    #[serde(rename = "MachineName")]
    pub machine_name: Option<String>,
    #[serde(rename = "Name")]
    pub name: String,
    #[serde(rename = "Username")]
    pub username: Option<String>,
    #[serde(rename = "Type")]
    pub kind: Option<String>,
    #[serde(rename = "RobotEnvironments")]
    pub robot_environments: Option<String>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ListRobotLogs {
    #[serde(rename = "Id")]
    pub id: i64,
    #[serde(rename = "JobKey")]
    pub job_key: Option<String>,
    #[serde(rename = "Level")]
    pub level: Option<String>,
    #[serde(rename = "WindowsIdentity")]
    pub windows_identity: Option<String>,
    #[serde(rename = "ProcessName")]
    pub process_name: Option<String>,
    #[serde(rename = "TimeStamp")]
    pub time_stamp: Option<String>,
    #[serde(rename = "Message")]
    pub message: Option<String>,
    #[serde(rename = "RobotName")]
    pub robot_name: Option<String>,
    #[serde(rename = "MachineId")]
    pub machine_id: Option<i64>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ListRoles {
    #[serde(rename = "Id")]
    pub id: i64,
    #[serde(rename = "Name")]
    pub name: String,
    #[serde(rename = "DisplayName")]
    pub display_name: Option<String>,
    #[serde(rename = "Type")]
    pub kind: Option<String>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ListSchedules {
    #[serde(rename = "Id")]
    pub id: i64,
    #[serde(rename = "Name")]
    pub name: String,
    #[serde(rename = "PackageName")]
    pub package_name: Option<String>,
    #[serde(rename = "EnvironmentId")]
    pub environment_id: Option<String>,
    #[serde(rename = "EnvironmentName")]
    pub environment_name: Option<String>,
    #[serde(rename = "StartProcessCron")]
    pub start_process_cron: Option<String>,
    #[serde(rename = "StartProcessCronSummary")]
    pub start_process_cron_summary: Option<String>,
    #[serde(rename = "Enabled")]
    pub enabled: Option<bool>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ListSessions {
    #[serde(rename = "Id")]
    pub id: i64,
    #[serde(rename = "MachineId")]
    pub machine_id: Option<String>,
    #[serde(rename = "HostMachineName")]
    pub host_machine_name: Option<String>,
    #[serde(rename = "MachineName")]
    pub machine_name: Option<String>,
    #[serde(rename = "State")]
    pub state: Option<String>,
    #[serde(rename = "ReportingTime")]
    pub reporting_time: Option<String>,
    #[serde(rename = "OrganizationUnitId")]
    pub organization_unit_id: Option<String>,
    #[serde(rename = "FolderName")]
    pub folder_name: Option<String>,
}

#[derive(Debug, Clone, Deserialize)]
pub struct ODataListResponse<T> {
    pub value: Vec<T>,
}

fn deserialize_robot_versions<'de, D>(deserializer: D) -> Result<Option<String>, D::Error>
where
    D: serde::Deserializer<'de>,
{
    let raw: Option<Value> = Option::deserialize(deserializer)?;
    match raw {
        Some(Value::Array(items)) => {
            let first = items.first();
            let version = first
                .and_then(|entry| entry.get("Version"))
                .and_then(Value::as_str)
                .map(ToOwned::to_owned);
            Ok(version)
        }
        Some(Value::String(version)) => Ok(Some(version)),
        _ => Ok(None),
    }
}
