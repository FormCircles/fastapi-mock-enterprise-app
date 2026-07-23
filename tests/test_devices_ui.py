from fastapi.testclient import TestClient

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