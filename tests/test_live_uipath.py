"""Optional live integration test against UiPath cloud."""

import os

import pytest

import uipathlib


REQUIRED_ENV = [
    "UIPATHLIB_URL_BASE",
    "UIPATHLIB_CLIENT_ID",
    "UIPATHLIB_REFRESH_TOKEN",
    "UIPATHLIB_SCOPE",
    "UIPATHLIB_FID",
]


@pytest.mark.skipif(
    any(not os.getenv(name) for name in REQUIRED_ENV),
    reason="Missing required UIPATHLIB_* environment variables.",
)
def test_live_list_queues():
    client = uipathlib.UiPath(
        url_base=os.environ["UIPATHLIB_URL_BASE"],
        client_id=os.environ["UIPATHLIB_CLIENT_ID"],
        refresh_token=os.environ["UIPATHLIB_REFRESH_TOKEN"],
        scope=os.environ["UIPATHLIB_SCOPE"],
    )

    response = client.list_queues(fid=os.environ["UIPATHLIB_FID"])
    assert response.status_code in (200, 401, 403)
