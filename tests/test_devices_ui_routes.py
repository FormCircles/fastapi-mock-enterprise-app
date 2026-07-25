"""Route-level tests for device-management browser UI."""

import pytest
from fastapi.testclient import TestClient

from app.api.devices import DEVICES
from app.main import app


client = TestClient(app)


@pytest.fixture(autouse=True)
def restore_devices():
    """Restore shared in-memory device list after each test."""
    original_devices = [
        device.copy()
        for device in DEVICES
    ]

    yield

    DEVICES.clear()
    DEVICES.extend(original_devices)


def test_devices_page_renders():
    response = client.get("/devices")

    assert response.status_code == 200
    assert "Router-01" in response.text
    assert "Switch-01" in response.text
    assert 'data-testid="device-table"' in response.text


def test_empty_device_list_renders_status_message():
    DEVICES.clear()

    response = client.get("/devices")

    assert response.status_code == 200
    assert "No devices found." in response.text
    assert 'role="status"' in response.text


def test_create_device_success():
    response = client.post(
        "/devices",
        data={
            "name": "Camera-01",
            "status": "online",
        },
        follow_redirects=False,
    )

    assert response.status_code == 303
    assert (
        response.headers["location"]
        == "/devices?success=device-created"
    )

    device = next(
        device
        for device in DEVICES
        if device["name"] == "Camera-01"
    )

    assert device["status"] == "online"


def test_edit_device_page_renders_existing_device():
    response = client.get("/devices/1/edit")

    assert response.status_code == 200
    assert "Edit Device" in response.text
    assert 'value="Router-01"' in response.text


def test_update_device_success():
    response = client.post(
        "/devices/1/edit",
        data={
            "name": "Router-Updated",
            "status": "offline",
        },
        follow_redirects=False,
    )

    assert response.status_code == 303
    assert (
        response.headers["location"]
        == "/devices?success=device-updated"
    )

    device = next(
        device
        for device in DEVICES
        if device["id"] == 1
    )

    assert device["name"] == "Router-Updated"
    assert device["status"] == "offline"


def test_delete_device_success():
    response = client.post(
        "/devices/1/delete",
        follow_redirects=False,
    )

    assert response.status_code == 303
    assert (
        response.headers["location"]
        == "/devices?success=device-deleted"
    )

    assert not any(
        device["id"] == 1
        for device in DEVICES
    )


def test_delete_missing_device():
    response = client.post(
        "/devices/999/delete",
        follow_redirects=False,
    )

    assert response.status_code == 404