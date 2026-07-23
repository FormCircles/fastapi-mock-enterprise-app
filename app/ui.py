from html import escape

from fastapi import APIRouter, Form
from fastapi.responses import HTMLResponse, RedirectResponse

from app.api.devices import DEVICES

ALLOWED_DEVICE_STATUSES = {"online", "offline"}

router = APIRouter()

@router.get("/", response_class=HTMLResponse)
def login_page():
    return """
    <html>
      <body>
        <h1>Login</h1>
        <form method="post" action="/login">
          <input name="username" type="text" />
          <input name="password" type="password" />
          <button type="submit">Login</button>
        </form>
      </body>
    </html>
    """

@router.post("/login")
def login(username: str = Form(...), password: str = Form(...)):
    if username == "admin" and password == "password":
        response = RedirectResponse(url="/devices", status_code=303)
        response.set_cookie(key="token", value="fake-jwt-token")
        return response
    return HTMLResponse("<h1>Login Failed</h1>", status_code=401)

@router.get("/devices", response_class=HTMLResponse)
def devices_page():
    """Render the device management page."""
    return _render_devices_page()

@router.post("/devices", response_class=HTMLResponse)
def create_device_ui(
    name: str = Form(...),
    status: str = Form(...),
):
    """Create a device through the browser interface."""
    normalized_name = name.strip()

    errors = _validate_device_form(
        normalized_name,
        status,
    )

    if errors:
        return _render_devices_page(
            errors=errors,
            submitted_name=normalized_name,
            submitted_status=status,
        )

    new_id = max(
        (device["id"] for device in DEVICES),
        default=0,
    ) + 1

    DEVICES.append(
        {
            "id": new_id,
            "name": normalized_name,
            "status": status,
        }
    )

    return RedirectResponse(
        url="/devices",
        status_code=303,
    )

def _validate_device_form(
    name: str,
    device_status: str,
) -> list[str]:
    """Validate submitted device form values."""
    errors: list[str] = []

    normalized_name = name.strip()

    if not normalized_name:
        errors.append("Device name is required.")

    if device_status not in ALLOWED_DEVICE_STATUSES:
        errors.append("Status must be online or offline.")

    if any(
        device["name"].casefold() == normalized_name.casefold()
        for device in DEVICES
    ):
        errors.append("A device with this name already exists.")

    return errors

def _render_devices_page(
    *,
    errors: list[str] | None = None,
    submitted_name: str = "",
    submitted_status: str = "online",
) -> HTMLResponse:
    """Render the device list and create-device form."""
    errors = errors or []

    error_html = ""

    if errors:
        error_items = "".join(
            f"<li>{escape(message)}</li>"
            for message in errors
        )
        error_html = f"""
        <div role="alert" aria-label="Device form errors">
          <p>Unable to create device.</p>
          <ul>
            {error_items}
          </ul>
        </div>
        """

    if DEVICES:
        rows = "".join(
          f"""
          <tr data-device-id="{device["id"]}">
            <td>{device["id"]}</td>
            <td>{escape(device["name"])}</td>
            <td>{escape(device["status"])}</td>
            <td>
              <a
                href="/devices/{device["id"]}/edit"
                aria-label="Edit {escape(device["name"])}"
              >
                Edit
              </a>
            </td>
          </tr>
          """
          for device in DEVICES
        )

        device_list_html = f"""
        <table role="table" aria-label="Device list">
          <thead>
            <tr>
              <th scope="col">ID</th>
              <th scope="col">Name</th>
              <th scope="col">Status</th>
            </tr>
          </thead>
          <tbody>
            {rows}
          </tbody>
        </table>
        """
    else:
        device_list_html = """
        <p role="status">No devices found.</p>
        """

    online_selected = (
        " selected"
        if submitted_status == "online"
        else ""
    )
    offline_selected = (
        " selected"
        if submitted_status == "offline"
        else ""
    )

    return HTMLResponse(
        f"""
        <html lang="en">
          <head>
            <meta charset="utf-8" />
            <title>Devices</title>
          </head>
          <body>
            <main>
              <h1>Devices</h1>

              {error_html}

              <section aria-labelledby="create-device-heading">
                <h2 id="create-device-heading">Create Device</h2>

                <form method="post" action="/devices">
                  <div>
                    <label for="device-name">Device name</label>
                    <input
                      id="device-name"
                      name="name"
                      type="text"
                      value="{escape(submitted_name)}"
                      required
                    />
                  </div>

                  <div>
                    <label for="device-status">Status</label>
                    <select
                      id="device-status"
                      name="status"
                      required
                    >
                      <option value="online"{online_selected}>
                        Online
                      </option>
                      <option value="offline"{offline_selected}>
                        Offline
                      </option>
                    </select>
                  </div>

                  <button type="submit">Create Device</button>
                </form>
              </section>

              <section aria-labelledby="device-list-heading">
                <h2 id="device-list-heading">Device List</h2>
                {device_list_html}
              </section>
            </main>
          </body>
        </html>
        """
    )

def _find_device(device_id: int) -> dict[str, object] | None:
    """Return a device by ID or None when it does not exist."""
    return next(
        (
            device
            for device in DEVICES
            if device["id"] == device_id
        ),
        None,
    )

def _validate_device_form(
    name: str,
    device_status: str,
    *,
    current_device_id: int | None = None,
) -> list[str]:
    """Validate submitted device form values."""
    errors: list[str] = []
    normalized_name = name.strip()

    if not normalized_name:
        errors.append("Device name is required.")

    if device_status not in ALLOWED_DEVICE_STATUSES:
        errors.append("Status must be online or offline.")

    duplicate_exists = any(
        device["name"].casefold() == normalized_name.casefold()
        and device["id"] != current_device_id
        for device in DEVICES
    )

    if normalized_name and duplicate_exists:
        errors.append("A device with this name already exists.")

    return errors

def _render_edit_device_page(
    device: dict[str, object],
    *,
    errors: list[str] | None = None,
    submitted_name: str | None = None,
    submitted_status: str | None = None,
    status_code: int = 200,
) -> HTMLResponse:
    """Render the populated device edit form."""
    errors = errors or []

    current_name = (
        str(device["name"])
        if submitted_name is None
        else submitted_name
    )
    current_status = (
        str(device["status"])
        if submitted_status is None
        else submitted_status
    )

    error_html = ""

    if errors:
        error_items = "".join(
            f"<li>{escape(message)}</li>"
            for message in errors
        )

        error_html = f"""
        <div role="alert" aria-label="Device update errors">
          <p>Unable to update device.</p>
          <ul>
            {error_items}
          </ul>
        </div>
        """

    online_selected = (
        " selected"
        if current_status == "online"
        else ""
    )
    offline_selected = (
        " selected"
        if current_status == "offline"
        else ""
    )

    device_id = int(device["id"])

    return HTMLResponse(
        content=f"""
        <html lang="en">
          <head>
            <meta charset="utf-8" />
            <title>Edit Device</title>
          </head>
          <body>
            <main>
              <h1>Edit Device</h1>

              {error_html}

              <form
                method="post"
                action="/devices/{device_id}/edit"
              >
                <div>
                  <label for="edit-device-name">
                    Device name
                  </label>
                  <input
                    id="edit-device-name"
                    name="name"
                    type="text"
                    value="{escape(current_name)}"
                    required
                  />
                </div>

                <div>
                  <label for="edit-device-status">
                    Status
                  </label>
                  <select
                    id="edit-device-status"
                    name="status"
                    required
                  >
                    <option value="online"{online_selected}>
                      Online
                    </option>
                    <option value="offline"{offline_selected}>
                      Offline
                    </option>
                  </select>
                </div>

                <button type="submit">Save</button>
                <a href="/devices">Cancel</a>
              </form>
            </main>
          </body>
        </html>
        """,
        status_code=status_code,
    )



