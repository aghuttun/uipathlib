mod models;
#[cfg(feature = "python")]
mod python_bindings;

pub use models::*;

use std::fs;
use std::path::Path;

use reqwest::blocking::{Client, RequestBuilder, Response as HttpResponse};
use reqwest::header::{AUTHORIZATION, CONTENT_TYPE, HeaderMap, HeaderValue};
use reqwest::{Method, StatusCode};
use serde_json::{Value, json};
use thiserror::Error;

use models::AuthTokenResponse;

#[derive(Debug, Clone)]
pub struct Configuration {
    pub url_base: String,
    pub client_id: String,
    pub refresh_token: String,
    pub token: Option<String>,
    pub scope: String,
}

#[derive(Debug, Clone)]
pub struct Response<T> {
    pub status_code: u16,
    pub content: Option<T>,
}

#[derive(Debug)]
pub struct UiPath {
    configuration: Configuration,
    client: Client,
}

#[derive(Debug, Error)]
pub enum UiPathError {
    #[error("HTTP error: {0}")]
    Http(#[from] reqwest::Error),
    #[error("I/O error: {0}")]
    Io(#[from] std::io::Error),
    #[error("JSON error: {0}")]
    Json(#[from] serde_json::Error),
    #[error("missing bearer token; authenticate first")]
    MissingToken,
    #[error("invalid header value: {0}")]
    InvalidHeader(#[from] reqwest::header::InvalidHeaderValue),
}

impl UiPath {
    pub fn new(
        url_base: impl Into<String>,
        client_id: impl Into<String>,
        refresh_token: impl Into<String>,
        scope: impl Into<String>,
    ) -> Result<Self, UiPathError> {
        let client = Client::builder().build()?;
        let mut this = Self {
            configuration: Configuration {
                url_base: url_base.into().trim_end_matches('/').to_string(),
                client_id: client_id.into(),
                refresh_token: refresh_token.into(),
                token: None,
                scope: scope.into(),
            },
            client,
        };

        this.auth()?;
        Ok(this)
    }

    pub fn is_auth(&self) -> bool {
        self.configuration.token.is_some()
    }

    pub fn auth(&mut self) -> Result<(), UiPathError> {
        let url_auth = "https://cloud.uipath.com/adidas/identity_/connect/token";
        let response = self
            .client
            .post(url_auth)
            .header(CONTENT_TYPE, "application/x-www-form-urlencoded")
            .form(&[
                ("grant_type", "client_credentials"),
                ("client_id", self.configuration.client_id.as_str()),
                ("client_secret", self.configuration.refresh_token.as_str()),
                ("scope", self.configuration.scope.as_str()),
            ])
            .send()?;

        if response.status() == StatusCode::OK {
            let token: AuthTokenResponse = response.json()?;
            self.configuration.token = Some(token.access_token);
        }

        Ok(())
    }

    fn export_to_json(&self, content: &[u8], save_as: Option<impl AsRef<Path>>) -> Result<(), UiPathError> {
        if let Some(path) = save_as {
            fs::write(path, content)?;
        }
        Ok(())
    }

    fn token(&self) -> Result<&str, UiPathError> {
        self.configuration
            .token
            .as_deref()
            .ok_or(UiPathError::MissingToken)
    }

    fn headers(&self, fid: Option<&str>) -> Result<HeaderMap, UiPathError> {
        let mut headers = HeaderMap::new();
        headers.insert(CONTENT_TYPE, HeaderValue::from_static("application/json"));
        headers.insert(
            AUTHORIZATION,
            HeaderValue::from_str(&format!("Bearer {}", self.token()?))?,
        );

        if let Some(fid_value) = fid {
            headers.insert(
                "X-UIPATH-OrganizationUnitID",
                HeaderValue::from_str(fid_value)?,
            );
        }

        Ok(headers)
    }

    fn request_json(
        &self,
        method: Method,
        path: &str,
        fid: Option<&str>,
        query: Option<&[(String, String)]>,
        body: Option<&Value>,
    ) -> Result<HttpResponse, UiPathError> {
        let mut request: RequestBuilder = self
            .client
            .request(
                method,
                format!("{}/{}", self.configuration.url_base, path.trim_start_matches('/')),
            )
            .headers(self.headers(fid)?);

        if let Some(params) = query {
            request = request.query(params);
        }

        if let Some(payload) = body {
            request = request.json(payload);
        }

        Ok(request.send()?)
    }

    pub fn list_assets(&self, fid: &str, save_as: Option<impl AsRef<Path>>) -> Result<Response<Value>, UiPathError> {
        self.list_endpoint(fid, "odata/Assets", None, save_as)
    }

    pub fn list_buckets(&self, fid: &str, save_as: Option<impl AsRef<Path>>) -> Result<Response<Value>, UiPathError> {
        self.list_endpoint(fid, "odata/Buckets", None, save_as)
    }

    pub fn create_bucket(
        &self,
        fid: &str,
        name: &str,
        guid: &str,
        description: Option<&str>,
    ) -> Result<Response<Value>, UiPathError> {
        let body = json!({
            "Name": name,
            "Description": description.unwrap_or(""),
            "Identifier": guid,
            "StorageProvider": null,
            "StorageParameters": null,
            "StorageContainer": null,
            "CredentialStoreId": null,
            "ExternalName": null,
            "Password": null,
            "FoldersCount": 0,
            "Id": 0
        });

        let response = self.request_json(Method::POST, "odata/Buckets", Some(fid), None, Some(&body))?;
        Ok(Response {
            status_code: response.status().as_u16(),
            content: None,
        })
    }

    pub fn delete_bucket(&self, fid: &str, id: &str) -> Result<Response<Value>, UiPathError> {
        let response = self.request_json(
            Method::DELETE,
            &format!("odata/Buckets({id})"),
            Some(fid),
            None,
            None,
        )?;

        Ok(Response {
            status_code: response.status().as_u16(),
            content: None,
        })
    }

    pub fn upload_bucket_file(
        &self,
        fid: &str,
        id: &str,
        localpath: impl AsRef<Path>,
        remotepath: &str,
    ) -> Result<Response<Value>, UiPathError> {
        let path = format!(
            "odata/Buckets({id})/UiPath.Server.Configuration.OData.GetWriteUri?path={remotepath}&expiryInMinutes=0"
        );
        let write_uri_resp = self.request_json(Method::GET, &path, Some(fid), None, None)?;
        let status = write_uri_resp.status().as_u16();

        if status != 200 {
            return Ok(Response {
                status_code: status,
                content: None,
            });
        }

        let body = write_uri_resp.json::<Value>()?;
        let Some(uri) = body.get("Uri").and_then(Value::as_str) else {
            return Ok(Response {
                status_code: 500,
                content: None,
            });
        };

        let data = fs::read(localpath)?;
        let response = self
            .client
            .put(uri)
            .header("x-ms-blob-type", "BlockBlob")
            .body(data)
            .send()?;

        Ok(Response {
            status_code: response.status().as_u16(),
            content: None,
        })
    }

    pub fn delete_bucket_file(&self, fid: &str, id: &str, filename: &str) -> Result<Response<Value>, UiPathError> {
        let response = self.request_json(
            Method::DELETE,
            &format!("odata/Buckets({id})/UiPath.Server.Configuration.OData.DeleteFile?path={filename}"),
            Some(fid),
            None,
            None,
        )?;

        Ok(Response {
            status_code: response.status().as_u16(),
            content: None,
        })
    }

    pub fn list_calendars(
        &self,
        fid: &str,
        save_as: Option<impl AsRef<Path>>,
    ) -> Result<Response<Value>, UiPathError> {
        self.list_endpoint(fid, "odata/Calendars", None, save_as)
    }

    pub fn list_environments(
        &self,
        fid: &str,
        save_as: Option<impl AsRef<Path>>,
    ) -> Result<Response<Value>, UiPathError> {
        self.list_endpoint(fid, "odata/Environments", None, save_as)
    }

    pub fn list_jobs(
        &self,
        fid: &str,
        filter: &str,
        save_as: Option<impl AsRef<Path>>,
    ) -> Result<Response<Value>, UiPathError> {
        self.list_endpoint(
            fid,
            "odata/Jobs",
            Some(vec![("$filter".to_string(), filter.to_string())]),
            save_as,
        )
    }

    pub fn start_job(&self, fid: &str, process_key: &str, robot_id: Option<i64>) -> Result<Response<Value>, UiPathError> {
        let body = if let Some(robot_id_value) = robot_id {
            json!({
                "startInfo": {
                    "ReleaseKey": process_key,
                    "Strategy": "Specific",
                    "RobotIds": [robot_id_value],
                    "JobsCount": 0,
                    "Source": "Manual"
                }
            })
        } else {
            json!({
                "startInfo": {
                    "ReleaseKey": process_key,
                    "Strategy": "JobsCount",
                    "JobsCount": 1,
                    "Source": "Manual"
                }
            })
        };

        let response = self.request_json(
            Method::POST,
            "odata/Jobs/UiPath.Server.Configuration.OData.StartJobs",
            Some(fid),
            None,
            Some(&body),
        )?;

        Ok(Response {
            status_code: response.status().as_u16(),
            content: None,
        })
    }

    pub fn stop_job(&self, fid: &str, id: &str) -> Result<Response<Value>, UiPathError> {
        let body = json!({ "strategy": "2" });
        let response = self.request_json(
            Method::POST,
            &format!("odata/Jobs({id})/UiPath.Server.Configuration.OData.StopJob"),
            Some(fid),
            None,
            Some(&body),
        )?;

        Ok(Response {
            status_code: response.status().as_u16(),
            content: None,
        })
    }

    pub fn list_machines(
        &self,
        fid: &str,
        save_as: Option<impl AsRef<Path>>,
    ) -> Result<Response<Value>, UiPathError> {
        self.list_endpoint(fid, "odata/Machines", None, save_as)
    }

    pub fn list_processes(
        &self,
        fid: &str,
        save_as: Option<impl AsRef<Path>>,
    ) -> Result<Response<Value>, UiPathError> {
        self.list_endpoint(fid, "odata/Processes", None, save_as)
    }

    pub fn list_queues(&self, fid: &str, save_as: Option<impl AsRef<Path>>) -> Result<Response<Value>, UiPathError> {
        self.list_endpoint(fid, "odata/QueueDefinitions", None, save_as)
    }

    pub fn list_queue_items(
        &self,
        fid: &str,
        filter: &str,
        save_as: Option<impl AsRef<Path>>,
    ) -> Result<Response<Value>, UiPathError> {
        self.list_endpoint(
            fid,
            "odata/QueueItems",
            Some(vec![("$filter".to_string(), filter.to_string())]),
            save_as,
        )
    }

    pub fn get_queue_item(
        &self,
        fid: &str,
        id: i64,
        save_as: Option<impl AsRef<Path>>,
    ) -> Result<Response<Value>, UiPathError> {
        let response = self.request_json(
            Method::GET,
            &format!("odata/QueueItems({id})"),
            Some(fid),
            None,
            None,
        )?;

        let status_code = response.status().as_u16();
        let bytes = response.bytes()?;
        self.export_to_json(bytes.as_ref(), save_as)?;

        let content = if status_code == 200 {
            serde_json::from_slice::<Value>(bytes.as_ref()).ok()
        } else {
            None
        };

        Ok(Response {
            status_code,
            content,
        })
    }

    pub fn add_queue_item(
        &self,
        fid: &str,
        queue: &str,
        data: Value,
        reference: &str,
        priority: &str,
        save_as: Option<impl AsRef<Path>>,
    ) -> Result<Response<Value>, UiPathError> {
        let body = json!({
            "itemData": {
                "Name": queue,
                "Priority": priority,
                "DeferDate": null,
                "DueDate": null,
                "Reference": reference,
                "SpecificContent": data
            }
        });

        let response = self.request_json(
            Method::POST,
            "odata/Queues/UiPathODataSvc.AddQueueItem",
            Some(fid),
            None,
            Some(&body),
        )?;

        let status_code = response.status().as_u16();
        let bytes = response.bytes()?;
        self.export_to_json(bytes.as_ref(), save_as)?;

        let content = if status_code == 201 {
            serde_json::from_slice::<Value>(bytes.as_ref()).ok()
        } else {
            None
        };

        Ok(Response {
            status_code,
            content,
        })
    }

    pub fn update_queue_item(
        &self,
        fid: &str,
        queue: &str,
        id: i64,
        data: Value,
    ) -> Result<Response<Value>, UiPathError> {
        let body = json!({
            "Name": queue,
            "Priority": "High",
            "SpecificContent": data,
            "DeferDate": null,
            "DueDate": null,
            "RiskSlaDate": null
        });

        let response = self.request_json(
            Method::PUT,
            &format!("odata/QueueItems({id})"),
            Some(fid),
            None,
            Some(&body),
        )?;

        Ok(Response {
            status_code: response.status().as_u16(),
            content: None,
        })
    }

    pub fn delete_queue_item(&self, fid: &str, id: i64) -> Result<Response<Value>, UiPathError> {
        let response = self.request_json(
            Method::DELETE,
            &format!("odata/QueueItems({id})"),
            Some(fid),
            None,
            None,
        )?;

        Ok(Response {
            status_code: response.status().as_u16(),
            content: None,
        })
    }

    pub fn list_releases(
        &self,
        fid: &str,
        save_as: Option<impl AsRef<Path>>,
    ) -> Result<Response<Value>, UiPathError> {
        self.list_endpoint(fid, "odata/Releases", None, save_as)
    }

    pub fn list_robots(&self, fid: &str, save_as: Option<impl AsRef<Path>>) -> Result<Response<Value>, UiPathError> {
        self.list_endpoint(fid, "odata/Robots", None, save_as)
    }

    pub fn list_robot_logs(
        &self,
        fid: &str,
        filter: &str,
        save_as: Option<impl AsRef<Path>>,
    ) -> Result<Response<Value>, UiPathError> {
        self.list_endpoint(
            fid,
            "odata/RobotLogs",
            Some(vec![("$filter".to_string(), filter.to_string())]),
            save_as,
        )
    }

    pub fn list_roles(&self, save_as: Option<impl AsRef<Path>>) -> Result<Response<Value>, UiPathError> {
        let response = self.request_json(Method::GET, "odata/Roles", None, None, None)?;
        self.finish_list_response(response, save_as)
    }

    pub fn list_schedules(
        &self,
        fid: &str,
        save_as: Option<impl AsRef<Path>>,
    ) -> Result<Response<Value>, UiPathError> {
        self.list_endpoint(fid, "odata/ProcessSchedules", None, save_as)
    }

    pub fn list_sessions(
        &self,
        fid: &str,
        save_as: Option<impl AsRef<Path>>,
    ) -> Result<Response<Value>, UiPathError> {
        self.list_endpoint(fid, "odata/Sessions", None, save_as)
    }

    fn list_endpoint(
        &self,
        fid: &str,
        path: &str,
        query: Option<Vec<(String, String)>>,
        save_as: Option<impl AsRef<Path>>,
    ) -> Result<Response<Value>, UiPathError> {
        let response = self.request_json(Method::GET, path, Some(fid), query.as_deref(), None)?;
        self.finish_list_response(response, save_as)
    }

    fn finish_list_response(
        &self,
        response: HttpResponse,
        save_as: Option<impl AsRef<Path>>,
    ) -> Result<Response<Value>, UiPathError> {
        let status_code = response.status().as_u16();
        let bytes = response.bytes()?;
        self.export_to_json(bytes.as_ref(), save_as)?;

        let content = if status_code == 200 {
            let value = serde_json::from_slice::<Value>(bytes.as_ref())?;
            value.get("value").cloned().or(Some(value))
        } else {
            None
        };

        Ok(Response {
            status_code,
            content,
        })
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn response_shape() {
        let response: Response<Value> = Response {
            status_code: 200,
            content: Some(json!({"ok": true})),
        };
        assert_eq!(response.status_code, 200);
        assert!(response.content.is_some());
    }
}
