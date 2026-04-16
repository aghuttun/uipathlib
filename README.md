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
# ASSETS
response = client.list_assets(fid="<folder-id>")
if response.status_code == 200:
    print(response.content)
```

```python
# BUCKETS
response = client.list_buckets(fid="<folder-id>")
if response.status_code == 200:
    print(response.content)
```

```python
# Create a bucket
response = client.create_bucket(
    fid="<folder-id>",
    name="Test Bucket",
    guid="f7ea20e9-971b-4c23-9979-321178a68c46",
    description="Example bucket",
)
print(response.status_code)
```

```python
# Delete a bucket
response = client.delete_bucket(
    fid="<folder-id>",
    id="<bucket-id>",
)
print(response.status_code)
```

```python
# Upload a file to a bucket
response = client.upload_bucket_file(
    fid="<folder-id>",
    id="<bucket-id>",
    localpath=r"C:\\path\\to\\file.txt",
    remotepath="file.txt",
)
print(response.status_code)
```

```python
# Delete a file from a bucket
response = client.delete_bucket_file(
    fid="<folder-id>",
    id="<bucket-id>",
    filename="file.txt",
)
print(response.status_code)
```

```python
# List jobs with filter
response = client.list_jobs(
    fid="<folder-id>",
    filter="State eq 'Running'",
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
# Get one queue item
response = client.get_queue_item(
    fid="<folder-id>",
    id=1125058579,
)
if response.status_code == 200:
    print(response.content)
```

```python
# Add a queue item
response = client.add_queue_item(
    fid="<folder-id>",
    queue="RPA_1201_Queue",
    data={
        "EmployeeId": "12345",
        "RowId": "566829607423876",
        "State": "Approved",
        "RequestId": "LR00001",
        "Language": "English",
    },
    reference="12345",
    priority="Normal",
)
print(response.status_code)
```

```python
# Update a queue item
response = client.update_queue_item(
    fid="<folder-id>",
    queue="RPA_1201_Queue",
    id=913233204,
    data={
        "EmployeeId": "54321",
        "RowId": "566829607423876",
        "State": "Approved",
        "RequestId": "LR20001",
        "Language": "English",
    },
)
print(response.status_code)
```

```python
# Delete a queue item
response = client.delete_queue_item(
    fid="<folder-id>",
    id=913233204,
)
print(response.status_code)
```

```python
# List releases
response = client.list_releases(fid="<folder-id>")
if response.status_code == 200:
    print(response.content)
```

```python
# List robots
response = client.list_robots(fid="<folder-id>")
if response.status_code == 200:
    print(response.content)
```

```python
# List robot logs with filter
response = client.list_robot_logs(
    fid="<folder-id>",
    filter="JobKey eq a111d111-b111-1f11-b11d-111adac1111d",
)
if response.status_code == 200:
    print(response.content)
```

```python
# List schedules
response = client.list_schedules(fid="<folder-id>")
if response.status_code == 200:
    print(response.content)
```

```python
# List sessions
response = client.list_sessions(fid="<folder-id>")
if response.status_code == 200:
    print(response.content)
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
