# uipathlib — Developer Guide

- [Overview](#overview)
- [Requirements](#requirements)
- [Version Access](#version-access)
- [Project Structure](#project-structure)
- [Building](#building)
- [API Reference](#api-reference)
- [Tests](#tests)
- [CI/CD](#cicd)
- [Publishing](#publishing)

## Overview

uipathlib is implemented in Rust using [PyO3](https://pyo3.rs/) for Python bindings and
[reqwest](https://crates.io/crates/reqwest) for UiPath Orchestrator HTTP operations.
[Maturin](https://www.maturin.rs/) is used for building and packaging.

## Requirements

- Python 3.10 or higher
- Rust stable toolchain (edition 2024 crate)
- Maturin 1.7 or higher

```bash
pip install maturin
```

Install local development dependencies:

```bash
python -m pip install -e .[dev]
```

## Version Access

Recommended:

```python
from importlib.metadata import version

print(version("uipathlib"))
```

Convenience alias:

```python
import uipathlib

print(uipathlib.__version__)
```

## Project Structure

```
uipathlib/
├── src/
│   ├── lib.rs              # Rust UiPath core implementation
│   ├── models.rs           # Rust data models (UiPath payloads)
│   └── python_bindings.rs  # PyO3 module and Python-facing wrappers
├── tests/
│   ├── test_smoke.py       # Public API smoke tests
│   └── test_live_uipath.py # Optional integration test against UiPath cloud
├── old_python_version/     # Archived pure-Python implementation
├── .github/
│   └── workflows/
│       └── CI.yml          # GitHub Actions CI/CD workflow
├── Cargo.toml              # Rust crate configuration
├── pyproject.toml          # Python packaging configuration (maturin backend)
├── README.md               # User-facing documentation
└── DEV.md                  # This file
```

## Building

Development build:

```bash
maturin develop --features python
```

Release build:

```bash
maturin develop --release --features python
```

Build wheel:

```bash
maturin build --release --features python --out dist
```

Build source distribution:

```bash
maturin sdist --out sdisthouse
```

## API Reference

### `UiPath(url_base, client_id, refresh_token, scope, custom_logger=None)`

Initialise the client and authenticate.

### Methods

- `is_auth()`
- `auth()`
- `list_assets(fid, save_as=None)`
- `list_buckets(fid, save_as=None)`
- `create_bucket(fid, name, guid, description=None)`
- `delete_bucket(fid, id)`
- `upload_bucket_file(fid, id, localpath, remotepath)`
- `delete_bucket_file(fid, id, filename)`
- `list_calendars(fid, save_as=None)`
- `list_environments(fid, save_as=None)`
- `list_jobs(fid, filter, save_as=None)`
- `start_job(fid, process_key, robot_id=None)`
- `stop_job(fid, id)`
- `list_machines(fid, save_as=None)`
- `list_processes(fid, save_as=None)`
- `list_queues(fid, save_as=None)`
- `list_queue_items(fid, filter, save_as=None)`
- `get_queue_item(fid, id, save_as=None)`
- `add_queue_item(fid, queue, data, reference, priority="Normal", save_as=None)`
- `update_queue_item(fid, queue, id, data)`
- `delete_queue_item(fid, id)`
- `list_releases(fid, save_as=None)`
- `list_robots(fid, save_as=None)`
- `list_robot_logs(fid, filter, save_as=None)`
- `list_roles(save_as=None)`
- `list_schedules(fid, save_as=None)`
- `list_sessions(fid, save_as=None)`

### Response Shape

All operations returning `Response` expose:

- `status_code`: HTTP status code.
- `content`: decoded payload (`dict`, `list`, or `None`).

### Errors

Python-facing methods raise `RuntimeError` when Rust operations fail.

## Tests

Smoke tests:

```bash
python -m pytest tests/test_smoke.py -q
```

Integration test (optional): set environment variables and run:

```bash
export UIPATHLIB_URL_BASE=<orchestrator_base_url>
export UIPATHLIB_CLIENT_ID=<client_id>
export UIPATHLIB_REFRESH_TOKEN=<client_secret_or_refresh_token>
export UIPATHLIB_SCOPE=<scope>
export UIPATHLIB_FID=<folder_id>

python -m pytest tests/test_live_uipath.py -q
```

Tests are skipped automatically if required variables are missing.

## CI/CD

The workflow in `.github/workflows/CI.yml` runs on push, pull request, tags (`v*`), and manual dispatch.

Jobs:

- `test`: wheel build + Python smoke tests + Rust tests.
- `build-wheel`: build wheels for Linux, Windows, and macOS.
- `build-sdist`: build source distribution.
- `publish-pypi`: publish tag builds to PyPI.

## Publishing

Tag and push:

```bash
git tag v0.0.13
git push origin v0.0.13
```

Manual publish:

```bash
maturin publish --release --username __token__ --password "$PYPI_API_TOKEN"
```
