from fastapi import APIRouter, Form
from fastapi.responses import HTMLResponse, RedirectResponse

from app.api.devices import DEVICES

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
    rows = ""

    if DEVICES:
        for device in DEVICES:
            rows += f"""
            <tr
              data-device-id="{device["id"]}"
              aria-label="Device {device["name"]}"
            >
                <td>{device["id"]}</td>
                <td>{device["name"]}</td>
                <td>{device["status"]}</td>
            </tr>
            """
    else:
        rows = """
        <tr>
            <td colspan="3">
                <span role="status">
                    No devices found.
                </span>
            </td>
        </tr>
        """

    return HTMLResponse(
        f"""
        <html>
          <body>

            <h1>Devices</h1>

            <table
              role="table"
              aria-label="Device list"
            >

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

          </body>
        </html>
        """
    )
