use std::path::PathBuf;

use pyo3::prelude::*;
use pyo3::types::PyModule;
use serde_json::Value;

use crate::UiPath;

#[pyclass(name = "Response")]
pub struct PyResponse {
    #[pyo3(get)]
    pub status_code: u16,
    content_json: Option<String>,
}

#[pymethods]
impl PyResponse {
    #[getter]
    fn content(&self, py: Python<'_>) -> PyResult<PyObject> {
        match &self.content_json {
            Some(raw_json) => {
                let json_module = PyModule::import(py, "json")?;
                let value = json_module.call_method1("loads", (raw_json,))?;
                Ok(value.into())
            }
            None => Ok(py.None()),
        }
    }
}

#[pyclass(name = "UiPath")]
pub struct PyUiPath {
    inner: UiPath,
}

#[pymethods]
impl PyUiPath {
    #[new]
    #[pyo3(signature = (url_base, client_id, refresh_token, scope, custom_logger=None))]
    fn new(
        url_base: String,
        client_id: String,
        refresh_token: String,
        scope: String,
        custom_logger: Option<PyObject>,
    ) -> PyResult<Self> {
        let _ = custom_logger;
        let inner = UiPath::new(url_base, client_id, refresh_token, scope).map_err(into_pyerr)?;
        Ok(Self { inner })
    }

    fn is_auth(&self) -> bool {
        self.inner.is_auth()
    }

    fn auth(&mut self) -> PyResult<()> {
        self.inner.auth().map_err(into_pyerr)
    }

    #[pyo3(signature = (fid, save_as=None))]
    fn list_assets(&self, fid: String, save_as: Option<String>) -> PyResult<PyResponse> {
        let response = self
            .inner
            .list_assets(&fid, save_as.as_ref().map(PathBuf::from))
            .map_err(into_pyerr)?;
        py_response_from(response.status_code, response.content)
    }

    #[pyo3(signature = (fid, save_as=None))]
    fn list_buckets(&self, fid: String, save_as: Option<String>) -> PyResult<PyResponse> {
        let response = self
            .inner
            .list_buckets(&fid, save_as.as_ref().map(PathBuf::from))
            .map_err(into_pyerr)?;
        py_response_from(response.status_code, response.content)
    }

    #[pyo3(signature = (fid, name, guid, description=None))]
    fn create_bucket(
        &self,
        fid: String,
        name: String,
        guid: String,
        description: Option<String>,
    ) -> PyResult<PyResponse> {
        let response = self
            .inner
            .create_bucket(&fid, &name, &guid, description.as_deref())
            .map_err(into_pyerr)?;
        py_response_from(response.status_code, response.content)
    }

    fn delete_bucket(&self, fid: String, id: String) -> PyResult<PyResponse> {
        let response = self.inner.delete_bucket(&fid, &id).map_err(into_pyerr)?;
        py_response_from(response.status_code, response.content)
    }

    fn upload_bucket_file(
        &self,
        fid: String,
        id: String,
        localpath: String,
        remotepath: String,
    ) -> PyResult<PyResponse> {
        let response = self
            .inner
            .upload_bucket_file(&fid, &id, PathBuf::from(localpath), &remotepath)
            .map_err(into_pyerr)?;
        py_response_from(response.status_code, response.content)
    }

    fn delete_bucket_file(&self, fid: String, id: String, filename: String) -> PyResult<PyResponse> {
        let response = self
            .inner
            .delete_bucket_file(&fid, &id, &filename)
            .map_err(into_pyerr)?;
        py_response_from(response.status_code, response.content)
    }

    #[pyo3(signature = (fid, save_as=None))]
    fn list_calendars(&self, fid: String, save_as: Option<String>) -> PyResult<PyResponse> {
        let response = self
            .inner
            .list_calendars(&fid, save_as.as_ref().map(PathBuf::from))
            .map_err(into_pyerr)?;
        py_response_from(response.status_code, response.content)
    }

    #[pyo3(signature = (fid, save_as=None))]
    fn list_environments(&self, fid: String, save_as: Option<String>) -> PyResult<PyResponse> {
        let response = self
            .inner
            .list_environments(&fid, save_as.as_ref().map(PathBuf::from))
            .map_err(into_pyerr)?;
        py_response_from(response.status_code, response.content)
    }

    #[pyo3(signature = (fid, filter, save_as=None))]
    fn list_jobs(&self, fid: String, filter: String, save_as: Option<String>) -> PyResult<PyResponse> {
        let response = self
            .inner
            .list_jobs(&fid, &filter, save_as.as_ref().map(PathBuf::from))
            .map_err(into_pyerr)?;
        py_response_from(response.status_code, response.content)
    }

    #[pyo3(signature = (fid, process_key, robot_id=None))]
    fn start_job(&self, fid: String, process_key: String, robot_id: Option<i64>) -> PyResult<PyResponse> {
        let response = self
            .inner
            .start_job(&fid, &process_key, robot_id)
            .map_err(into_pyerr)?;
        py_response_from(response.status_code, response.content)
    }

    fn stop_job(&self, fid: String, id: String) -> PyResult<PyResponse> {
        let response = self.inner.stop_job(&fid, &id).map_err(into_pyerr)?;
        py_response_from(response.status_code, response.content)
    }

    #[pyo3(signature = (fid, save_as=None))]
    fn list_machines(&self, fid: String, save_as: Option<String>) -> PyResult<PyResponse> {
        let response = self
            .inner
            .list_machines(&fid, save_as.as_ref().map(PathBuf::from))
            .map_err(into_pyerr)?;
        py_response_from(response.status_code, response.content)
    }

    #[pyo3(signature = (fid, save_as=None))]
    fn list_processes(&self, fid: String, save_as: Option<String>) -> PyResult<PyResponse> {
        let response = self
            .inner
            .list_processes(&fid, save_as.as_ref().map(PathBuf::from))
            .map_err(into_pyerr)?;
        py_response_from(response.status_code, response.content)
    }

    #[pyo3(signature = (fid, save_as=None))]
    fn list_queues(&self, fid: String, save_as: Option<String>) -> PyResult<PyResponse> {
        let response = self
            .inner
            .list_queues(&fid, save_as.as_ref().map(PathBuf::from))
            .map_err(into_pyerr)?;
        py_response_from(response.status_code, response.content)
    }

    #[pyo3(signature = (fid, filter, save_as=None))]
    fn list_queue_items(&self, fid: String, filter: String, save_as: Option<String>) -> PyResult<PyResponse> {
        let response = self
            .inner
            .list_queue_items(&fid, &filter, save_as.as_ref().map(PathBuf::from))
            .map_err(into_pyerr)?;
        py_response_from(response.status_code, response.content)
    }

    #[pyo3(signature = (fid, id, save_as=None))]
    fn get_queue_item(&self, fid: String, id: i64, save_as: Option<String>) -> PyResult<PyResponse> {
        let response = self
            .inner
            .get_queue_item(&fid, id, save_as.as_ref().map(PathBuf::from))
            .map_err(into_pyerr)?;
        py_response_from(response.status_code, response.content)
    }

    #[pyo3(signature = (fid, queue, data, reference, priority="Normal", save_as=None))]
    fn add_queue_item(
        &self,
        py: Python<'_>,
        fid: String,
        queue: String,
        data: &Bound<'_, PyAny>,
        reference: String,
        priority: &str,
        save_as: Option<String>,
    ) -> PyResult<PyResponse> {
        let data_value = py_any_to_json_value(py, data)?;
        let response = self
            .inner
            .add_queue_item(
                &fid,
                &queue,
                data_value,
                &reference,
                priority,
                save_as.as_ref().map(PathBuf::from),
            )
            .map_err(into_pyerr)?;
        py_response_from(response.status_code, response.content)
    }

    fn update_queue_item(
        &self,
        py: Python<'_>,
        fid: String,
        queue: String,
        id: i64,
        data: &Bound<'_, PyAny>,
    ) -> PyResult<PyResponse> {
        let data_value = py_any_to_json_value(py, data)?;
        let response = self
            .inner
            .update_queue_item(&fid, &queue, id, data_value)
            .map_err(into_pyerr)?;
        py_response_from(response.status_code, response.content)
    }

    fn delete_queue_item(&self, fid: String, id: i64) -> PyResult<PyResponse> {
        let response = self.inner.delete_queue_item(&fid, id).map_err(into_pyerr)?;
        py_response_from(response.status_code, response.content)
    }

    #[pyo3(signature = (fid, save_as=None))]
    fn list_releases(&self, fid: String, save_as: Option<String>) -> PyResult<PyResponse> {
        let response = self
            .inner
            .list_releases(&fid, save_as.as_ref().map(PathBuf::from))
            .map_err(into_pyerr)?;
        py_response_from(response.status_code, response.content)
    }

    #[pyo3(signature = (fid, save_as=None))]
    fn list_robots(&self, fid: String, save_as: Option<String>) -> PyResult<PyResponse> {
        let response = self
            .inner
            .list_robots(&fid, save_as.as_ref().map(PathBuf::from))
            .map_err(into_pyerr)?;
        py_response_from(response.status_code, response.content)
    }

    #[pyo3(signature = (fid, filter, save_as=None))]
    fn list_robot_logs(&self, fid: String, filter: String, save_as: Option<String>) -> PyResult<PyResponse> {
        let response = self
            .inner
            .list_robot_logs(&fid, &filter, save_as.as_ref().map(PathBuf::from))
            .map_err(into_pyerr)?;
        py_response_from(response.status_code, response.content)
    }

    #[pyo3(signature = (save_as=None))]
    fn list_roles(&self, save_as: Option<String>) -> PyResult<PyResponse> {
        let response = self
            .inner
            .list_roles(save_as.as_ref().map(PathBuf::from))
            .map_err(into_pyerr)?;
        py_response_from(response.status_code, response.content)
    }

    #[pyo3(signature = (fid, save_as=None))]
    fn list_schedules(&self, fid: String, save_as: Option<String>) -> PyResult<PyResponse> {
        let response = self
            .inner
            .list_schedules(&fid, save_as.as_ref().map(PathBuf::from))
            .map_err(into_pyerr)?;
        py_response_from(response.status_code, response.content)
    }

    #[pyo3(signature = (fid, save_as=None))]
    fn list_sessions(&self, fid: String, save_as: Option<String>) -> PyResult<PyResponse> {
        let response = self
            .inner
            .list_sessions(&fid, save_as.as_ref().map(PathBuf::from))
            .map_err(into_pyerr)?;
        py_response_from(response.status_code, response.content)
    }
}

#[pymodule]
fn uipathlib(_py: Python<'_>, module: &Bound<'_, PyModule>) -> PyResult<()> {
    module.add_class::<PyUiPath>()?;
    module.add_class::<PyResponse>()?;
    module.add("__version__", env!("CARGO_PKG_VERSION"))?;
    Ok(())
}

fn py_response_from(status_code: u16, content: Option<Value>) -> PyResult<PyResponse> {
    let content_json = match content {
        Some(value) => Some(serde_json::to_string(&value).map_err(into_pyerr)?),
        None => None,
    };

    Ok(PyResponse {
        status_code,
        content_json,
    })
}

fn py_any_to_json_value(py: Python<'_>, value: &Bound<'_, PyAny>) -> PyResult<Value> {
    let json = PyModule::import(py, "json")?;
    let serialized = json.call_method1("dumps", (value,))?;
    let serialized_str: String = serialized.extract()?;
    serde_json::from_str(&serialized_str).map_err(into_pyerr)
}

fn into_pyerr<E>(error: E) -> PyErr
where
    E: std::fmt::Display,
{
    pyo3::exceptions::PyRuntimeError::new_err(error.to_string())
}
