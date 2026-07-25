"""Validation tests for device-management browser UI."""

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


def test_create_device_rejects_blank_name():
    response = client.post(
        "/devices",
        data={
            "name": "   ",
            "status": "online",
        },
    )

    assert response.status_code == 422
    assert "Device name is required." in response.text
    assert 'data-testid="device-form-error"' in response.text


def test_create_device_rejects_invalid_status():
    response = client.post(
        "/devices",
        data={
            "name": "Camera-01",
            "status": "maintenance",
        },
    )

    assert response.status_code == 422
    assert "Status must be online or offline." in response.text


def test_create_device_rejects_duplicate_name():
    response = client.post(
        "/devices",
        data={
            "name": "router-01",
            "status": "offline",
        },
    )

    assert response.status_code == 422
    assert (
        "A device with this name already exists."
        in response.text
    )


def test_update_device_rejects_duplicate_name():
    response = client.post(
        "/devices/2/edit",
        data={
            "name": "Router-01",
            "status": "online",
        },
    )

    assert response.status_code == 422
    assert (
        "A device with this name already exists."
        in response.text
    )


def test_update_device_rejects_blank_name():
    response = client.post(
        "/devices/1/edit",
        data={
            "name": "",
            "status": "online",
        },
    )

    assert response.status_code == 422
    assert "Device name is required." in response.text


def test_update_device_rejects_invalid_status():
    response = client.post(
        "/devices/1/edit",
        data={
            "name": "Router-01",
            "status": "unknown",
        },
    )

    assert response.status_code == 422
    assert (
        "Status must be online or offline."
        in response.text
    )


def test_edit_missing_device():
    response = client.get("/devices/999/edit")

    assert response.status_code == 404