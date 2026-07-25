"""Server-rendered browser routes for the FastAPI Mock App."""

from html import escape

from fastapi import APIRouter, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse, Response

from app.api.devices import DEVICES


ALLOWED_DEVICE_STATUSES = {"online", "offline"}

SUCCESS_MESSAGES = {
    "device-created": "Device created successfully.",
    "device-updated": "Device updated successfully.",
    "device-deleted": "Device deleted successfully.",
}

router = APIRouter()


@router.get("/", response_class=HTMLResponse)
def login_page() -> HTMLResponse:
    """Render the accessible login page."""
    return HTMLResponse(
        """
        <html lang="en">
          <head>
            <meta charset="utf-8" />
            <title>Login</title>
          </head>
          <body>
            <main>
              <h1>Login</h1>

              <form method="post" action="/login">
                <div>
                  <label for="login-username">Username</label>
                  <input
                    id="login-username"
                    name="username"
                    type="text"
                    autocomplete="username"
                    data-testid="login-username"
                    required
                  />
                </div>

                <div>
                  <label for="login-password">Password</label>
                  <input
                    id="login-password"
                    name="password"
                    type="password"
                    autocomplete="current-password"
                    data-testid="login-password"
                    required
                  />
                </div>

                <button
                  type="submit"
                  data-testid="login-submit"
                >
                  Login
                </button>
              </form>
            </main>
          </body>
        </html>
        """
    )


@router.post("/login")
def login(
    username: str = Form(...),
    password: str = Form(...),
) -> Response:
    """Authenticate the browser user."""
    if username == "admin" and password == "password":
        response = RedirectResponse(
            url="/devices",
            status_code=303,
        )
        response.set_cookie(
            key="token",
            value="fake-jwt-token",
            httponly=True,
            samesite="lax",
        )
        return response

    return HTMLResponse(
        """
        <html lang="en">
          <head>
            <meta charset="utf-8" />
            <title>Login Failed</title>
          </head>
          <body>
            <main>
              <h1>Login Failed</h1>

              <div
                role="alert"
                data-testid="login-error"
              >
                Invalid username or password.
              </div>

              <a href="/">Return to login</a>
            </main>
          </body>
        </html>
        """,
        status_code=401,
    )


@router.get("/devices", response_class=HTMLResponse)
def devices_page(request: Request) -> HTMLResponse:
    """Render the device-management page."""
    success_key = request.query_params.get("success")
    success_message = SUCCESS_MESSAGES.get(success_key)

    return _render_devices_page(
        success_message=success_message,
    )


@router.post("/devices", response_class=HTMLResponse)
def create_device_ui(
    name: str = Form(""),
    status: str = Form(""),
) -> Response:
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
            status_code=422,
        )

    new_id = max(
        (int(device["id"]) for device in DEVICES),
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
        url="/devices?success=device-created",
        status_code=303,
    )


@router.get(
    "/devices/{device_id}/edit",
    response_class=HTMLResponse,
)
def edit_device_page(device_id: int) -> HTMLResponse:
    """Render a populated edit form for a device."""
    device = _find_device(device_id)

    if device is None:
        return _render_device_not_found()

    return _render_edit_device_page(device)


@router.post(
    "/devices/{device_id}/edit",
    response_class=HTMLResponse,
)
def update_device_ui(
    device_id: int,
    name: str = Form(""),
    status: str = Form(""),
) -> Response:
    """Update a device through the browser interface."""
    device = _find_device(device_id)

    if device is None:
        return _render_device_not_found()

    normalized_name = name.strip()

    errors = _validate_device_form(
        normalized_name,
        status,
        current_device_id=device_id,
    )

    if errors:
        return _render_edit_device_page(
            device,
            errors=errors,
            submitted_name=normalized_name,
            submitted_status=status,
            status_code=422,
        )

    device["name"] = normalized_name
    device["status"] = status

    return RedirectResponse(
        url="/devices?success=device-updated",
        status_code=303,
    )


@router.post("/devices/{device_id}/delete")
def delete_device_ui(
    device_id: int,
) -> Response:
    """Delete a device through the browser interface."""
    device = _find_device(device_id)

    if device is None:
        return _render_device_not_found()

    try:
        DEVICES.remove(device)
    except ValueError:
        return HTMLResponse(
            """
            <html lang="en">
              <head>
                <meta charset="utf-8" />
                <title>Delete Device Error</title>
              </head>
              <body>
                <main>
                  <h1>Unable to Delete Device</h1>

                  <div
                    role="alert"
                    data-testid="device-delete-error"
                  >
                    The device could not be deleted.
                  </div>

                  <a href="/devices">Return to devices</a>
                </main>
              </body>
            </html>
            """,
            status_code=409,
        )

    return RedirectResponse(
        url="/devices?success=device-deleted",
        status_code=303,
    )


def _validate_device_form(
    name: str,
    device_status: str,
    *,
    current_device_id: int | None = None,
) -> list[str]:
    """Validate submitted create or update values."""
    errors: list[str] = []
    normalized_name = name.strip()

    if not normalized_name:
        errors.append("Device name is required.")

    if device_status not in ALLOWED_DEVICE_STATUSES:
        errors.append("Status must be online or offline.")

    duplicate_exists = any(
        str(device["name"]).casefold() == normalized_name.casefold()
        and int(device["id"]) != current_device_id
        for device in DEVICES
    )

    if normalized_name and duplicate_exists:
        errors.append("A device with this name already exists.")

    return errors


def _find_device(
    device_id: int,
) -> dict[str, object] | None:
    """Return a device by stable ID."""
    return next(
        (
            device
            for device in DEVICES
            if int(device["id"]) == device_id
        ),
        None,
    )


def _render_devices_page(
    *,
    errors: list[str] | None = None,
    submitted_name: str = "",
    submitted_status: str = "online",
    success_message: str | None = None,
    status_code: int = 200,
) -> HTMLResponse:
    """Render the device list and accessible create form."""
    errors = errors or []

    success_html = ""

    if success_message:
        success_html = f"""
        <div
          role="status"
          data-testid="operation-success"
        >
          {escape(success_message)}
        </div>
        """

    error_html = ""

    if errors:
        error_items = "".join(
            f"<li>{escape(message)}</li>"
            for message in errors
        )
        error_html = f"""
        <div
          role="alert"
          aria-label="Device form errors"
          data-testid="device-form-error"
        >
          <p>Unable to create device.</p>
          <ul>
            {error_items}
          </ul>
        </div>
        """

    if DEVICES:
        rows = "".join(
            _render_device_row(device)
            for device in DEVICES
        )

        device_list_html = f"""
        <table
          role="table"
          aria-label="Device list"
          data-testid="device-table"
        >
          <thead>
            <tr>
              <th scope="col">ID</th>
              <th scope="col">Name</th>
              <th scope="col">Status</th>
              <th scope="col">Actions</th>
            </tr>
          </thead>
          <tbody>
            {rows}
          </tbody>
        </table>
        """
    else:
        device_list_html = """
        <p
          role="status"
          data-testid="device-empty-state"
        >
          No devices found.
        </p>
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
        content=f"""
        <html lang="en">
          <head>
            <meta charset="utf-8" />
            <title>Devices</title>
          </head>
          <body>
            <main>
              <h1>Devices</h1>

              {success_html}
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
                      data-testid="create-device-name"
                      required
                    />
                  </div>

                  <div>
                    <label for="device-status">Status</label>
                    <select
                      id="device-status"
                      name="status"
                      data-testid="create-device-status"
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

                  <button
                    type="submit"
                    data-testid="create-device-submit"
                  >
                    Create Device
                  </button>
                </form>
              </section>

              <section aria-labelledby="device-list-heading">
                <h2 id="device-list-heading">Device List</h2>
                {device_list_html}
              </section>
            </main>
          </body>
        </html>
        """,
        status_code=status_code,
    )


def _render_device_row(
    device: dict[str, object],
) -> str:
    """Render one device row with stable automation selectors."""
    device_id = int(device["id"])
    device_name = escape(str(device["name"]))
    device_status = escape(str(device["status"]))

    return f"""
    <tr
      data-device-id="{device_id}"
      data-testid="device-row-{device_id}"
    >
      <td data-testid="device-id-{device_id}">
        {device_id}
      </td>
      <td data-testid="device-name-{device_id}">
        {device_name}
      </td>
      <td data-testid="device-status-{device_id}">
        {device_status}
      </td>
      <td>
        <form
          method="get"
          action="/devices/{device_id}/edit"
        >
          <button
            type="submit"
            aria-label="Edit {device_name}"
            data-testid="edit-device-{device_id}"
          >
            Edit
          </button>
        </form>

        <form
          method="post"
          action="/devices/{device_id}/delete"
          onsubmit="return confirm('Delete {device_name}?')"
        >
          <button
            type="submit"
            aria-label="Delete {device_name}"
            data-testid="delete-device-{device_id}"
          >
            Delete
          </button>
        </form>
      </td>
    </tr>
    """


def _render_edit_device_page(
    device: dict[str, object],
    *,
    errors: list[str] | None = None,
    submitted_name: str | None = None,
    submitted_status: str | None = None,
    status_code: int = 200,
) -> HTMLResponse:
    """Render the accessible, populated device edit form."""
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
        <div
          role="alert"
          aria-label="Device update errors"
          data-testid="device-update-error"
        >
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
                    data-testid="edit-device-name"
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
                    data-testid="edit-device-status"
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

                <button
                  type="submit"
                  data-testid="edit-device-save"
                >
                  Save
                </button>

                <a
                  href="/devices"
                  data-testid="edit-device-cancel"
                >
                  Cancel
                </a>
              </form>
            </main>
          </body>
        </html>
        """,
        status_code=status_code,
    )


def _render_device_not_found() -> HTMLResponse:
    """Render a safe and accessible missing-device response."""
    return HTMLResponse(
        """
        <html lang="en">
          <head>
            <meta charset="utf-8" />
            <title>Device Not Found</title>
          </head>
          <body>
            <main>
              <h1>Device Not Found</h1>

              <div
                role="alert"
                data-testid="device-not-found"
              >
                The requested device does not exist.
              </div>

              <a href="/devices">Return to devices</a>
            </main>
          </body>
        </html>
        """,
        status_code=404,
    )
