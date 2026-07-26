"""Route-level tests for the FastAPI device-management browser UI."""

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


def test_login_page_has_accessible_fields(client: TestClient) -> None:
    response = client.get("/")

    assert response.status_code == 200
    assert 'for="login-username"' in response.text
    assert 'id="login-username"' in response.text
    assert 'for="login-password"' in response.text
    assert 'id="login-password"' in response.text
    assert 'data-testid="login-submit"' in response.text


def test_invalid_login_uses_accessible_alert(client: TestClient) -> None:
    response = client.post(
        "/login",
        data={
            "username": "invalid",
            "password": "invalid",
        },
    )

    assert response.status_code == 401
    assert 'role="alert"' in response.text
    assert 'data-testid="login-error"' in response.text
    assert "Invalid username or password." in response.text


def test_devices_page_displays_devices(client: TestClient) -> None:
    response = client.get("/devices")

    assert response.status_code == 200
    assert "Router-01" in response.text
    assert "Switch-01" in response.text
    assert 'data-device-id="1"' in response.text
    assert 'data-device-id="2"' in response.text


def test_devices_page_has_accessible_table(client: TestClient) -> None:
    response = client.get("/devices")

    assert response.status_code == 200
    assert 'role="table"' in response.text
    assert 'aria-label="Device list"' in response.text
    assert 'data-testid="device-table"' in response.text
    assert '<th scope="col">ID</th>' in response.text
    assert '<th scope="col">Name</th>' in response.text
    assert '<th scope="col">Status</th>' in response.text
    assert '<th scope="col">Actions</th>' in response.text


def test_create_device_form_has_accessible_controls(client: TestClient) -> None:
    response = client.get("/devices")

    assert response.status_code == 200
    assert 'for="device-name"' in response.text
    assert 'id="device-name"' in response.text
    assert 'data-testid="create-device-name"' in response.text
    assert 'for="device-status"' in response.text
    assert 'id="device-status"' in response.text
    assert 'data-testid="create-device-status"' in response.text
    assert 'data-testid="create-device-submit"' in response.text


def test_device_rows_have_stable_selectors(client: TestClient) -> None:
    response = client.get("/devices")

    assert response.status_code == 200
    assert 'data-device-id="1"' in response.text
    assert 'data-testid="device-row-1"' in response.text
    assert 'data-testid="device-id-1"' in response.text
    assert 'data-testid="device-name-1"' in response.text
    assert 'data-testid="device-status-1"' in response.text


def test_device_actions_have_meaningful_accessible_names(
    client: TestClient,
) -> None:
    response = client.get("/devices")

    assert response.status_code == 200
    assert 'aria-label="Edit Router-01"' in response.text
    assert 'aria-label="Delete Router-01"' in response.text
    assert 'data-testid="edit-device-1"' in response.text
    assert 'data-testid="delete-device-1"' in response.text


def test_create_device_through_ui(client: TestClient) -> None:
    response = client.post(
        "/devices",
        data={
            "name": "Firewall-01",
            "status": "online",
        },
        follow_redirects=False,
    )

    assert response.status_code == 303
    assert response.headers["location"] == "/devices?success=device-created"

    created_device = next(
        device for device in DEVICES if device["name"] == "Firewall-01"
    )
    assert created_device["status"] == "online"


def test_created_device_is_displayed_with_success_feedback(
    client: TestClient,
) -> None:
    response = client.post(
        "/devices",
        data={
            "name": "Access-Point-01",
            "status": "offline",
        },
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert "Access-Point-01" in response.text
    assert "offline" in response.text
    assert "Device created successfully." in response.text
    assert 'role="status"' in response.text
    assert 'data-testid="operation-success"' in response.text


def test_edit_device_page_is_populated_and_accessible(
    client: TestClient,
) -> None:
    response = client.get("/devices/1/edit")

    assert response.status_code == 200
    assert "Edit Device" in response.text
    assert 'value="Router-01"' in response.text
    assert 'option value="online" selected' in response.text
    assert 'for="edit-device-name"' in response.text
    assert 'for="edit-device-status"' in response.text
    assert 'data-testid="edit-device-name"' in response.text
    assert 'data-testid="edit-device-status"' in response.text
    assert 'data-testid="edit-device-save"' in response.text
    assert 'data-testid="edit-device-cancel"' in response.text


def test_update_device_through_ui(client: TestClient) -> None:
    response = client.post(
        "/devices/1/edit",
        data={
            "name": "Router-Updated",
            "status": "offline",
        },
        follow_redirects=False,
    )

    assert response.status_code == 303
    assert response.headers["location"] == "/devices?success=device-updated"

    updated_device = next(device for device in DEVICES if device["id"] == 1)
    assert updated_device["name"] == "Router-Updated"
    assert updated_device["status"] == "offline"


def test_updated_device_is_displayed_with_success_feedback(
    client: TestClient,
) -> None:
    response = client.post(
        "/devices/1/edit",
        data={
            "name": "Router-Updated",
            "status": "offline",
        },
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert "Router-Updated" in response.text
    assert "offline" in response.text
    assert "Device updated successfully." in response.text
    assert 'role="status"' in response.text
    assert 'data-testid="operation-success"' in response.text


def test_delete_device_through_ui(client: TestClient) -> None:
    response = client.post(
        "/devices/1/delete",
        follow_redirects=False,
    )

    assert response.status_code == 303
    assert response.headers["location"] == "/devices?success=device-deleted"
    assert all(device["id"] != 1 for device in DEVICES)


def test_deleted_device_is_removed_with_success_feedback(
    client: TestClient,
) -> None:
    response = client.post(
        "/devices/1/delete",
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert "Router-01" not in response.text
    assert "Device deleted successfully." in response.text
    assert 'role="status"' in response.text
    assert 'data-testid="operation-success"' in response.text
