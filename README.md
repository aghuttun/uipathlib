# uipathlib

UiPath Cloud client package for Python powered by Rust.

- [Installation](#installation)
- [Usage](#usage)
- [Version](#version)
- [Licence](#licence)

## Installation

```bash
pip install uipathlib
```

## Usage

```python
import uipathlib

client = uipathlib.UiPath(
    url_base="https://cloud.uipath.com/my_company/Production/orchestrator_",
    client_id="<client-id>",
    refresh_token="<client-secret-or-refresh-token>",
    scope="OR.Folders.Read OR.Jobs OR.Queues OR.Execution.Read OR.Robots.Read OR.Settings.Read",
)
```

```python
# Check authentication state
print(client.is_auth())
```

```python
# List queues
response = client.list_queues(fid="<folder-id>")
if response.status_code == 200:
    print(response.content)
```

```python
# List queue items with OData filter
response = client.list_queue_items(
    fid="<folder-id>",
    filter="QueueDefinitionId eq 123456",
)
if response.status_code == 200:
    print(response.content)
```

```python
# Start job
response = client.start_job(
    fid="<folder-id>",
    process_key="<release-key>",
    robot_id=None,
)
print(response.status_code)
```

For technical and contributor documentation, see [DEV.md](DEV.md).

## Version

Recommended way to read installed package version:

```python
from importlib.metadata import version

print(version("uipathlib"))
```

Convenience attribute:

```python
import uipathlib

print(uipathlib.__version__)
```

## Licence

BSD-3-Clause Licence (see [LICENSE](LICENSE))
