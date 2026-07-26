"""Validation and error-handling tests for the device-management browser UI."""

from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient

from app.api.devices import DEVICES
from app.main import app


@pytest.fixture
def client() -> Generator[TestClient, None, None]:
    """Provide an isolated FastAPI test client."""
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture(autouse=True)
def restore_devices() -> Generator[None, None, None]:
    """Restore the shared in-memory device list after each test."""
    original_devices = [device.copy() for device in DEVICES]

    yield

    DEVICES.clear()
    DEVICES.extend(original_devices)


def test_create_device_rejects_blank_name(client: TestClient) -> None:
    response = client.post(
        "/devices",
        data={
            "name": "   ",
            "status": "online",
        },
    )

    assert response.status_code == 422
    assert 'role="alert"' in response.text
    assert 'data-testid="device-form-error"' in response.text
    assert "Device name is required." in response.text


def test_create_device_rejects_invalid_status(client: TestClient) -> None:
    response = client.post(
        "/devices",
        data={
            "name": "Invalid-Status-Device",
            "status": "maintenance",
        },
    )

    assert response.status_code == 422
    assert 'role="alert"' in response.text
    assert 'data-testid="device-form-error"' in response.text
    assert "Status must be online or offline." in response.text


def test_create_device_rejects_duplicate_name(client: TestClient) -> None:
    response = client.post(
        "/devices",
        data={
            "name": "router-01",
            "status": "offline",
        },
    )

    assert response.status_code == 422
    assert 'role="alert"' in response.text
    assert 'data-testid="device-form-error"' in response.text
    assert "A device with this name already exists." in response.text


def test_update_device_rejects_blank_name(client: TestClient) -> None:
    response = client.post(
        "/devices/1/edit",
        data={
            "name": "   ",
            "status": "online",
        },
    )

    assert response.status_code == 422
    assert 'role="alert"' in response.text
    assert 'data-testid="device-update-error"' in response.text
    assert "Device name is required." in response.text

    unchanged_device = next(device for device in DEVICES if device["id"] == 1)
    assert unchanged_device["name"] == "Router-01"
    assert unchanged_device["status"] == "online"


def test_update_device_rejects_invalid_status(client: TestClient) -> None:
    response = client.post(
        "/devices/1/edit",
        data={
            "name": "Router-Updated",
            "status": "maintenance",
        },
    )

    assert response.status_code == 422
    assert 'role="alert"' in response.text
    assert 'data-testid="device-update-error"' in response.text
    assert "Status must be online or offline." in response.text

    unchanged_device = next(device for device in DEVICES if device["id"] == 1)
    assert unchanged_device["name"] == "Router-01"
    assert unchanged_device["status"] == "online"


def test_update_device_rejects_duplicate_name(client: TestClient) -> None:
    response = client.post(
        "/devices/1/edit",
        data={
            "name": "switch-01",
            "status": "offline",
        },
    )

    assert response.status_code == 422
    assert 'role="alert"' in response.text
    assert 'data-testid="device-update-error"' in response.text
    assert "A device with this name already exists." in response.text

    unchanged_device = next(device for device in DEVICES if device["id"] == 1)
    assert unchanged_device["name"] == "Router-01"
    assert unchanged_device["status"] == "online"


def test_update_device_allows_unchanged_name(client: TestClient) -> None:
    response = client.post(
        "/devices/1/edit",
        data={
            "name": "Router-01",
            "status": "offline",
        },
        follow_redirects=False,
    )

    assert response.status_code == 303
    assert response.headers["location"] == "/devices?success=device-updated"

    updated_device = next(device for device in DEVICES if device["id"] == 1)
    assert updated_device["name"] == "Router-01"
    assert updated_device["status"] == "offline"


def test_edit_missing_device_returns_not_found(client: TestClient) -> None:
    response = client.get("/devices/999/edit")

    assert response.status_code == 404


def test_update_missing_device_returns_not_found(client: TestClient) -> None:
    response = client.post(
        "/devices/999/edit",
        data={
            "name": "Missing-Device",
            "status": "online",
        },
    )

    assert response.status_code == 404


def test_delete_missing_device_returns_not_found(client: TestClient) -> None:
    response = client.post(
        "/devices/999/delete",
        follow_redirects=False,
    )

    assert response.status_code == 404
