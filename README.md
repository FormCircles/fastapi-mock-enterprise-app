# FastAPI Mock Application API Contract Reference

## Purpose

This document defines the current API contract for the FastAPI Mock Application used by the Playwright Enterprise Test Framework.

The API contract serves as reference material for:

* API automation development
* Test case design
* Service validation
* Future API expansion planning

This document reflects the current implementation and does not represent new feature development work.

---

# Authentication APIs

## Login

Authenticates a user and returns a mock access token.

### Endpoint

| Method | Endpoint   |
| ------ | ---------- |
| POST   | /api/login |

### Request Body

```json
{
  "username": "admin",
  "password": "password"
}
```

### Successful Response

**HTTP 200 OK**

```json
{
  "token": "mock-jwt-token"
}
```

### Failed Response

**HTTP 401 Unauthorized**

```json
{
  "detail": "Invalid credentials"
}
```

### Notes

Current implementation supports the following credentials:

| Username | Password |
| -------- | -------- |
| admin    | password |

---

# Device Management APIs

## Get All Devices

Returns all available devices.

### Endpoint

| Method | Endpoint     |
| ------ | ------------ |
| GET    | /api/devices |

### Successful Response

**HTTP 200 OK**

```json
[
  {
    "id": 1,
    "name": "Device A",
    "status": "online"
  }
]
```

---

## Get Device By ID

Returns a specific device.

### Endpoint

| Method | Endpoint                 |
| ------ | ------------------------ |
| GET    | /api/devices/{device_id} |

### Path Parameters

| Parameter | Type    | Description              |
| --------- | ------- | ------------------------ |
| device_id | Integer | Unique device identifier |

### Successful Response

**HTTP 200 OK**

```json
{
  "id": 1,
  "name": "Device A",
  "status": "online"
}
```

### Error Response

**HTTP 404 Not Found**

```json
{
  "detail": "Device not found"
}
```

---

## Create Device

Creates a new device record.

### Endpoint

| Method | Endpoint     |
| ------ | ------------ |
| POST   | /api/devices |

### Request Body

```json
{
  "name": "New Device",
  "status": "online"
}
```

### Successful Response

**HTTP 201 Created**

```json
{
  "id": 2,
  "name": "New Device",
  "status": "online"
}
```

---

## Update Device

Updates an existing device.

### Endpoint

| Method | Endpoint                 |
| ------ | ------------------------ |
| PUT    | /api/devices/{device_id} |

### Request Body

```json
{
  "name": "Updated Device",
  "status": "offline"
}
```

### Successful Response

**HTTP 200 OK**

```json
{
  "id": 1,
  "name": "Updated Device",
  "status": "offline"
}
```

### Error Response

**HTTP 404 Not Found**

```json
{
  "detail": "Device not found"
}
```

---

## Delete Device

Deletes a device record.

### Endpoint

| Method | Endpoint                 |
| ------ | ------------------------ |
| DELETE | /api/devices/{device_id} |

### Successful Response

**HTTP 200 OK**

```json
{
  "message": "Device deleted successfully"
}
```

### Error Response

**HTTP 404 Not Found**

```json
{
  "detail": "Device not found"
}
```

---

# System APIs

## Health Check

Returns application health status.

### Endpoint

| Method | Endpoint |
| ------ | -------- |
| GET    | /health  |

### Successful Response

**HTTP 200 OK**

```json
{
  "status": "ok"
}
```

### Usage

Used by:

* Docker HEALTHCHECK
* CI/CD validation workflows
* Smoke test execution
* Runtime monitoring

---

## Version Information

Returns application version information.

### Endpoint

| Method | Endpoint |
| ------ | -------- |
| GET    | /version |

### Successful Response

**HTTP 200 OK**

```json
{
  "version": "x.y.z"
}
```

### Usage

Used by:

* Deployment verification
* Release validation
* Environment comparison testing

---

# Interactive API Documentation

When the application is running locally, FastAPI automatically generates OpenAPI and Swagger documentation.

| Interface             | URL                                |
| --------------------- | ---------------------------------- |
| Swagger UI            | http://localhost:8080/docs         |
| OpenAPI Specification | http://localhost:8080/openapi.json |

The Swagger UI should be considered the authoritative source for request and response schemas.

---

# Future API Categories

The following API groups are candidates for future expansion and are not currently implemented:

* User Management
* Role-Based Access Control (RBAC)
* Device Telemetry
* Device Configuration
* Audit Logging
* Notification Services
* Reporting APIs

These items are documented for roadmap visibility only and do not represent active API contracts.

---

# Related Documentation

* FastAPI Mock Application README
* Playwright Enterprise Test Framework
* FCAPI-45 Verify FastAPI Application Startup
* FCAPI-46 Verify FastAPI Health Endpoint
* FCAPI-47 Validate FastAPI Container Startup
* FCAPI-134 Create FastAPI API Contract Reference Page
* FCAPI-135 Document Existing Auth and Device Endpoints

---

# Future Test Utility API Contracts

## Purpose

The following endpoints are planned for future implementation to support automated testing, environment preparation, and deterministic test execution.

These endpoints are not currently implemented and are documented as proposed API contracts only.

---

# Version API

## Get Application Version

Returns build and version information for the running application.

### Endpoint

| Method | Endpoint |
| ------ | -------- |
| GET    | /version |

### Successful Response

**HTTP 200 OK**

```json
{
  "application": "FastAPI Mock Application",
  "version": "1.0.0",
  "build_number": "123",
  "build_date": "2026-06-10T12:00:00Z"
}
```

### Usage

Used by:

* Deployment validation
* Environment verification
* CI/CD release testing
* Smoke test verification

### Notes

Version information should remain read-only and should not require authentication.

---

# Test Reset API

## Reset Test Environment

Resets application data to a known baseline state.

### Endpoint

| Method | Endpoint    |
| ------ | ----------- |
| POST   | /test/reset |

### Description

Removes test-created data and restores the application to a predefined default state.

This endpoint is intended for non-production environments only.

### Request Body

No request body required.

### Successful Response

**HTTP 200 OK**

```json
{
  "status": "success",
  "message": "Test environment reset completed"
}
```

### Error Response

**HTTP 500 Internal Server Error**

```json
{
  "status": "error",
  "message": "Reset operation failed"
}
```

### Usage

Used by:

* Automated regression testing
* Test environment preparation
* CI pipeline execution
* Local developer testing

### Notes

Future implementation should:

* Clear test-generated records
* Restore baseline seed data
* Be disabled in production environments

---

# Test Seed API

## Seed Test Data

Creates predefined data required for automated test execution.

### Endpoint

| Method | Endpoint   |
| ------ | ---------- |
| POST   | /test/seed |

### Request Body

```json
{
  "dataset": "default"
}
```

### Supported Datasets

| Dataset    | Description                              |
| ---------- | ---------------------------------------- |
| default    | Standard automation test data            |
| smoke      | Minimal data required for smoke tests    |
| regression | Extended data set for regression testing |

### Successful Response

**HTTP 200 OK**

```json
{
  "status": "success",
  "dataset": "default",
  "records_created": 25
}
```

### Error Response

**HTTP 400 Bad Request**

```json
{
  "status": "error",
  "message": "Unknown dataset"
}
```

### Usage

Used by:

* Automated test setup
* CI/CD execution
* Regression test preparation
* Local development validation

### Notes

Future implementation should:

* Support multiple dataset profiles
* Produce deterministic test data
* Allow repeated execution without duplication
* Be restricted to test environments

---

# Automation Workflow Example

A future automation workflow may execute the following sequence:

```text
POST /test/reset

↓

POST /test/seed

↓

GET /health

↓

GET /version

↓

Execute API Tests

↓

Execute UI Tests
```

This workflow ensures all automated tests begin from a predictable application state.

---

# Security Considerations

The following endpoints must never be exposed in production environments:

* POST /test/reset
* POST /test/seed

Recommended controls:

* Test environment only
* Internal network access only
* Authentication required
* Environment-based feature flags

These endpoints exist solely to support automated testing and environment preparation.


## Run FastAPI Mock App in Docker

The FastAPI mock application can be started locally in Docker for development, validation, and automated testing.

### Prerequisites

* Docker Desktop installed and running
* Docker configured for Linux containers

---

### Build the Docker Image

Run from the `sut/FastAPIMockApp` directory:

```bash
docker build -t fastapi-mock-enterprise-app:local .
```

---

### Start the Container

```bash
docker run -d --name fastapi-mock-enterprise-app -p 8080:8080 fastapi-mock-enterprise-app:local
```

This publishes the FastAPI service on:

```text
http://127.0.0.1:8080
```

---

### Verify the Application is Running

#### Health Endpoint

```bash
curl http://127.0.0.1:8080/health
```

Expected result:

```json
{"status":"ok"}
```

#### Swagger UI

Open in browser:

```text
http://127.0.0.1:8080/docs
```

---

### Check Container Health Status

```bash
docker inspect --format='{{.State.Health.Status}}' fastapi-mock-enterprise-app
```

Expected result:

```text
healthy
```

---

### View Container Logs

```bash
docker logs fastapi-mock-enterprise-app
```

---

### Stop and Remove the Container

```bash
docker rm -f fastapi-mock-enterprise-app
```

---

### Run Automated Startup Validation

To verify image build, startup, host accessibility, and internal container `/health` checks:

```bash
python tools/validate_container_startup.py
```

Expected result:

```text
External health check passed: http://127.0.0.1:8080/health
Internal container /health check passed.
FCAPI validation passed.
```

---

### Run from Repository Root

If starting from the parent repository root:

```bash
docker build -t fastapi-mock-enterprise-app:local -f sut/FastAPIMockApp/Dockerfile sut/FastAPIMockApp
docker run -d --name fastapi-mock-enterprise-app -p 8080:8080 fastapi-mock-enterprise-app:local
curl http://127.0.0.1:8080/health
docker rm -f fastapi-mock-enterprise-app
```
