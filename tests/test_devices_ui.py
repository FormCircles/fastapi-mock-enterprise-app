"""Route-level tests for the device-management browser UI."""

import pytest
from fastapi.testclient import TestClient

from app.api.devices import DEVICES
from app.main import app


client = TestClient(app)


@pytest.fixture(autouse=True)
def restore_devices():
    """Restore the shared in-memory device list after each test."""
    original_devices = [
        device.copy()
        for device in DEVICES
    ]

    yield

    DEVICES.clear()
    DEVICES.extend(original_devices)


def test_login_page_has_accessible_fields():
    response = client.get("/")

    assert response.status_code == 200
    assert 'for="login-username"' in response.text
    assert 'id="login-username"' in response.text
    assert 'for="login-password"' in response.text
    assert 'id="login-password"' in response.text
    assert 'data-testid="login-submit"' in response.text


def test_invalid_login_uses_accessible_alert():
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


def test_devices_page_displays_devices():
    response = client.get("/devices")

    assert response.status_code == 200
    assert "Router-01" in response.text
    assert "Switch-01" in response.text
    assert 'data-device-id="1"' in response.text
    assert 'data-device-id="2"' in response.text


def test_devices_page_has_accessible_table():
    response = client.get("/devices")

    assert response.status_code == 200
    assert 'role="table"' in response.text
    assert 'aria-label="Device list"' in response.text
    assert 'data-testid="device-table"' in response.text
    assert '<th scope="col">ID</th>' in response.text
    assert '<th scope="col">Name</th>' in response.text
    assert '<th scope="col">Status</th>' in response.text
    assert '<th scope="col">Actions</th>' in response.text


def test_create_device_form_has_accessible_controls():
    response = client.get("/devices")

    assert response.status_code == 200
    assert 'for="device-name"' in response.text
    assert 'id="device-name"' in response.text
    assert 'data-testid="create-device-name"' in response.text
    assert 'for="device-status"' in response.text
    assert 'id="device-status"' in response.text
    assert 'data-testid="create-device-status"' in response.text
    assert 'data-testid="create-device-submit"' in response.text


def test_device_rows_have_stable_selectors():
    response = client.get("/devices")

    assert response.status_code == 200
    assert 'data-device-id="1"' in response.text
    assert 'data-testid="device-row-1"' in response.text
    assert 'data-testid="device-id-1"' in response.text
    assert 'data-testid="device-name-1"' in response.text
    assert 'data-testid="device-status-1"' in response.text


def test_device_actions_have_meaningful_accessible_names():
    response = client.get("/devices")

    assert response.status_code == 200
    assert 'aria-label="Edit Router-01"' in response.text
    assert 'aria-label="Delete Router-01"' in response.text
    assert 'data-testid="edit-device-1"' in response.text
    assert 'data-testid="delete-device-1"' in response.text


def test_create_device_through_ui():
    response = client.post(
        "/devices",
        data={
            "name": "Firewall-01",
            "status": "online",
        },
        follow_redirects=False,
    )

    assert response.status_code == 303
    assert (
        response.headers["location"]
        == "/devices?success=device-created"
    )

    created_device = next(
        device
        for device in DEVICES
        if device["name"] == "Firewall-01"
    )
    assert created_device["status"] == "online"


def test_created_device_is_displayed_with_success_feedback():
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


def test_create_device_rejects_blank_name():
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


def test_create_device_rejects_invalid_status():
    response = client.post(
        "/devices",
        data={
            "name": "Invalid-Status-Device",
            "status": "maintenance",
        },
    )

    assert response.status_code == 422
    assert 'role="alert"' in response.text
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
    assert 'role="alert"' in response.text
    assert "A device with this name already exists." in response.text


def test_edit_device_page_is_populated_and_accessible():
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


def test_update_device_through_ui():
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


def test_updated_device_is_displayed_with_success_feedback():
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
    assert 'data-testid="operation-success"' in response.text


def test_update_device_rejects_blank_name():
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


def test_update_device_rejects_invalid_status():
    response = client.post(
        "/devices/1/edit",
        data={
            "name": "Router-01",
            "status": "maintenance",
        },
    )

    assert response.status_code == 422
    assert 'data-testid="device-update-error"' in response.text
    assert "Status must be online or offline." in response.text


def test_update_device_rejects_duplicate_name():
    response = client.post(
        "/devices/1/edit",
        data={
            "name": "Switch-01",
            "status": "online",
        },
    )

    assert response.status_code == 422
    assert 'data-testid="device-update-error"' in response.text
    assert "A device with this name already exists." in response.text


def test_edit_missing_device_returns_accessible_404():
    response = client.get("/devices/999/edit")

    assert response.status_code == 404
    assert "Device Not Found" in response.text
    assert 'role="alert"' in response.text
    assert 'data-testid="device-not-found"' in response.text


def test_delete_device_through_ui():
    DEVICES.append(
        {
            "id": 99,
            "name": "Delete-Me",
            "status": "offline",
        }
    )

    response = client.post(
        "/devices/99/delete",
        follow_redirects=False,
    )

    assert response.status_code == 303
    assert (
        response.headers["location"]
        == "/devices?success=device-deleted"
    )
    assert not any(
        device["id"] == 99
        for device in DEVICES
    )


def test_deleted_device_is_removed_with_success_feedback():
    DEVICES.append(
        {
            "id": 98,
            "name": "Remove-From-List",
            "status": "online",
        }
    )

    response = client.post(
        "/devices/98/delete",
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert "Remove-From-List" not in response.text
    assert "Device deleted successfully." in response.text
    assert 'role="status"' in response.text
    assert 'data-testid="operation-success"' in response.text


def test_delete_missing_device_returns_accessible_404():
    response = client.post("/devices/99999/delete")

    assert response.status_code == 404
    assert "Device Not Found" in response.text
    assert 'role="alert"' in response.text
    assert 'data-testid="device-not-found"' in response.text


def test_delete_device_removes_only_requested_record():
    DEVICES.extend(
        [
            {
                "id": 97,
                "name": "Keep-Device",
                "status": "online",
            },
            {
                "id": 96,
                "name": "Delete-Device",
                "status": "offline",
            },
        ]
    )

    response = client.post(
        "/devices/96/delete",
        follow_redirects=False,
    )

    assert response.status_code == 303
    assert any(
        device["id"] == 97
        and device["name"] == "Keep-Device"
        for device in DEVICES
    )
    assert not any(
        device["id"] == 96
        for device in DEVICES
    )


def test_empty_state_uses_accessible_status():
    DEVICES.clear()

    response = client.get("/devices")

    assert response.status_code == 200
    assert "No devices found." in response.text
    assert 'role="status"' in response.text
    assert 'data-testid="device-empty-state"' in response.text
