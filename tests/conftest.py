"""Shared pytest fixtures for FastAPI Mock App tests."""

import pytest

from app.api.devices import DEVICES


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