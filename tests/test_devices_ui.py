import pytest
from fastapi.testclient import TestClient

from app.api.devices import DEVICES
from app.main import app


client = TestClient(app)


def test_devices_page_displays_devices():
    response = client.get("/devices")

    assert response.status_code == 200

    assert "Router-01" in response.text
    assert "Switch-01" in response.text

    assert 'data-device-id="1"' in response.text
    assert 'data-device-id="2"' in response.text


def test_devices_page_has_accessible_table():
    response = client.get("/devices")

    assert 'role="table"' in response.text
    assert 'aria-label="Device list"' in response.text
    assert "<th" in response.text

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
    assert response.headers["location"] == "/devices"

    created_device = next(
        device
        for device in DEVICES
        if device["name"] == "Firewall-01"
    )

    assert created_device["status"] == "online"

def test_created_device_is_displayed_on_devices_page():
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

def test_create_device_rejects_blank_name():
    response = client.post(
        "/devices",
        data={
            "name": "   ",
            "status": "online",
        },
    )

    assert response.status_code == 200
    assert 'role="alert"' in response.text
    assert "Device name is required." in response.text

def test_create_device_rejects_duplicate_name():
    DEVICES.append(
        {
            "id": 99,
            "name": "Duplicate-Device",
            "status": "online",
        }
    )

    response = client.post(
        "/devices",
        data={
            "name": "duplicate-device",
            "status": "offline",
        },
    )

    assert response.status_code == 200
    assert 'role="alert"' in response.text
    assert "A device with this name already exists." in response.text

    matching_devices = [
        device
        for device in DEVICES
        if device["name"].casefold() == "duplicate-device"
    ]

    assert len(matching_devices) == 1


def test_create_device_rejects_invalid_status():
    response = client.post(
        "/devices",
        data={
            "name": "Invalid-Status-Device",
            "status": "maintenance",
        },
    )

    assert response.status_code == 200
    assert 'role="alert"' in response.text
    assert "Status must be online or offline." in response.text

def _render_devices_page(
    *,
    errors: list[str] | None = None,
    submitted_name: str = "",
    submitted_status: str = "online",
    status_code: int = 200,
) -> HTMLResponse:
    return HTMLResponse(
        content=...,
        status_code=status_code,
)

def test_devices_page_displays_edit_action():
    response = client.get("/devices")

    assert response.status_code == 200
    assert "/devices/1/edit" in response.text
    assert 'aria-label="Edit Router-01"' in response.text


def test_edit_device_page_is_populated():
    response = client.get("/devices/1/edit")

    assert response.status_code == 200
    assert "Edit Device" in response.text
    assert 'value="Router-01"' in response.text
    assert 'option value="online" selected' in response.text

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
    assert response.headers["location"] == "/devices"

    device = next(
        device
        for device in DEVICES
        if device["id"] == 1
    )

    assert device["name"] == "Router-Updated"
    assert device["status"] == "offline"

def test_updated_device_is_displayed():
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
    assert "Device name is required." in response.text

    device = next(
        device
        for device in DEVICES
        if device["id"] == 1
    )

    assert device["name"] == "Router-01"

def test_update_device_rejects_invalid_status():
    response = client.post(
        "/devices/1/edit",
        data={
            "name": "Router-01",
            "status": "maintenance",
        },
    )

    assert response.status_code == 422
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
    assert "A device with this name already exists." in response.text

    device = next(
        device
        for device in DEVICES
        if device["id"] == 1
    )

    assert device["name"] == "Router-01"

def test_edit_missing_device_returns_404():
    response = client.get("/devices/999/edit")

    assert response.status_code == 404
    assert "Device Not Found" in response.text
    assert 'role="alert"' in response.text


