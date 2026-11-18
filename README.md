# coursegrab-backend

Technologies involved include:  
Flask  
SQLite

## Virtualenv

Virtualenv setup:

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Environment Variables

It's recommended to use [`direnv`](https://direnv.net).
The required environment variables for this API are listed in envrc.template.

To use `direnv` with this repository, run the following and set the variables appropriately.

```bash
cp envrc.template .envrc
```

## Ingesting Data
Once you have set up the Virtual Environment and Environment variables (see above), running the app for the first time (see [Running the App](#running-the-app) below) will automatically ingest all classes, and should continually check to see if a new roster has been released daily. If you ever need to manually ingest a new roster (without having to wait for the cronjob to execute), you can simply restart the containers or processes running this backend.

## Style

**Flake 8**: Install [flake8](http://flake8.pycqa.org/en/latest/)

**Black**: Either use [command line tool](https://black.readthedocs.io/en/stable/installation_and_usage.html) or use [editor extension](https://black.readthedocs.io/en/stable/editor_integration.html).

If using VS Code, install the 'Python' extension and include following snippet inside `settings.json`:

```json
"python.linting.pylintEnabled": false,
"python.linting.flake8Enabled": true,
"python.formatting.provider": "black"
```

## Running the App

To run the app:

```
python src/run.py
```

## Running tests

```
pytest
```

## Migrations

### Initialize migrations

```
python src/manage.py db init
```

### Generate a migration

```
python src/manage.py db migrate -m "Message describing migration"
```

### Run the migration

```
python src/manage.py db upgrade
```

## Interactive API documentation

With the backend running, open `/docs/` (for example,
`http://127.0.0.1:5001/docs/`). Use Swagger UI’s default version selector to choose original `/api` or Firebase
`/api/v2` endpoints, then expand a category. The OpenAPI 3.0 specification is available
at `/docs/openapi.json` and can also be imported into API clients.

Use **Authorize** and paste a token without the `Bearer` prefix:

- **LegacySession**: `session_token` from `/api/session/initialize/`.
- **LegacyRefresh**: `update_token`, only for `/api/session/update/`.
- **FirebaseAuth**: Firebase ID token obtained through a client Firebase Auth SDK.

**Try it out** sends requests to the server hosting the docs, including writes to its
configured database. The legacy notification debug GET endpoints send real push
notifications. Authorization is kept in memory rather than persisted across reloads.
The UI loads pinned Swagger UI 5.35.0 assets from jsDelivr and needs internet access;
the JSON spec is served locally and external spec validation is disabled.

Maintain `src/app/docs/openapi.json` alongside controller changes. Tests compare the
spec's paths/methods with Flask's registered API routes and check authentication
schemes and references. Documented legacy error responses reflect current behavior,
including HTTP 200 with `success: false`; this docs change does not alter endpoints.

## Firebase Auth API v2

Both API versions run together:

- `/api/` keeps the existing Google-token exchange, CourseGrab session tokens,
  refresh endpoint, and device-token endpoint for existing clients.
- `/api/v2/` accepts only `Authorization: Bearer <firebase_id_token>`. It verifies
  Firebase ID tokens, revocation, and disabled-account status, and never falls back
  to legacy credentials. Google provider tokens are not Firebase ID tokens.

Both versions use the same local users, tracked sections, and notification preferences.
Course and tracking controllers are shared; authentication is selected by the matched
Flask blueprint, not by guessing the token type.

### Configuration

Set `FIREBASE_PROJECT_ID` and Application Default Credentials (for example,
`GOOGLE_APPLICATION_CREDENTIALS` pointing to a service-account JSON file outside the
repository). Credentials must support Firebase Auth user lookup. Authentication and
FCM share the default Admin app. Do not configure an auth emulator in production.

Only Google sign-in identities with verified Cornell emails or the existing
`appstoreappdev@gmail.com` / `coursegrab.droid@gmail.com` exceptions can access v2.
The pinned `firebase-admin==4.0.1` supports revocation checking but requires a separate
user lookup to reject disabled accounts. This incurs an additional lookup per request.
No broad Python/dependency upgrade is included.

### Client contract

Clients obtain Firebase ID tokens through their SDK and use `/api/v2` as the base URL.
The SDK manages authentication persistence and token refresh.

| Endpoint | Behavior |
| --- | --- |
| `GET /api/v2/users/me/` | Link/create the local user and return `data: {"user": {...}}`; no custom tokens are issued. |
| `GET /api/v2/users/tracking/` | Same tracking response as v1. |
| `POST /api/v2/sections/track/` and `/untrack/` | Same request bodies and response shapes as v1. |
| `POST /api/v2/courses/search/` | Same search contract; anonymous access remains available. |
| `GET /api/v2/courses/<int:course_id>/` | Same course contract; anonymous access remains available. |
| `GET /api/v2/sections/<catalog_num>/` | Same section contract as v1. |
| `POST /api/v2/users/notification/` | Updates the shared account's notification preference. |
| `POST /api/v2/users/devices/` | Register a device with `{"device_type": "IOS", "device_token": "..."}` (or `ANDROID`). Returns `data: {"id": 123, "device_type": "IOS"}`. |
| `PUT /api/v2/users/devices/123/` | Same body; rotate the token of an owned registration. |
| `DELETE /api/v2/users/devices/123/` | Unregister an owned device before signing out; returns `data: null`. |

Other authenticated v2 endpoints also resolve/create the local user on demand.
Repeated registration of the same user/platform/token returns the same registration ID.
A different user's registration ID returns 404, and a token registered in v2 to
another account returns 409. Unregister while signed into the old account before
switching accounts, or obtain a new push token. Clients should retain their registration
ID for rotation and logout; it is not an authentication credential.

V2 has no `/session/initialize/`, `/session/update/`, or `/users/device-token/` routes.
The original `/api` versions remain available and continue returning legacy responses.
Notification debug endpoints are not duplicated into v2.

A supplied invalid token is rejected even on anonymous-capable routes. Errors retain
`{"success": false, "data": {"errors": ["..."]}, "timestamp": ...}` for registered
controllers, with 401 for authentication, 403 for eligibility, 404 for device ownership
lookups, 409 for identity/device conflicts, 400 for invalid device input, and 503 for
Firebase service failures. Unexpected v2 controller failures return a generic 500.
Unregistered routes use Flask's normal 404 response.

### Identity, devices, and gradual rollout

Back up the database and apply `python src/manage.py db upgrade` before running this
code. The additive migration introduces unique nullable `users.firebase_uid` and
`device_registrations`, preserving existing users, sessions, and tracked courses.
No Firebase project or production data is modified by the code changes themselves.

First Firebase sign-in links a verified email to an unlinked local user with a
conditional database update. Later requests resolve by UID. Conflicts and ambiguous
case-insensitive email matches are rejected. Local IDs, names, tracked sections, and
preferences remain intact. Verified email changes for the same UID update the local
email unless it conflicts with an existing account.

Notifications read legacy session tokens and v2 registrations together, deduplicated
per platform. Explicit v2 registrations take precedence over legacy copies of the
same token. Rotation/logout clears corresponding old legacy token copies. Existing
registrations remain in the sessions table instead of being copied at migration time,
so legacy clients can continue registering and rotating devices during rollout.

Deploy the backend first, then migrate each supported client independently. Existing
clients keep using `/api`; migrated clients use `/api/v2`, Firebase ID tokens, and the
new device contract. Monitor authentication failures and linking conflicts. Retire v1
and legacy session storage only after supported clients no longer depend on them.
Do not drop the new schema as a routine rollback after v2 activity: that discards
identity mappings and new device registrations. Disable v2 client rollout instead.

Tests mock Firebase calls; real-project credentials, revoked/disabled accounts, client
sign-in, and push delivery still require a staging smoke test.

## Legacy User Sessions

All user sessions are managed with `Session` model. This allows multiple sessions to be associated with one user, allowing users to maintain sessions on multiple devices.

The big drawback of this implementation is that we allow the users to create essentially an unlimited number of sessions since there is no good way to identify the device or browser that the user is trying to sign in from. For instance, theoretically, if a user signs in from an incognito browser 5 times, that would create 5 sessions. This is not ideal because we have limitations to our backend's size.

### Refresh Sessions

To somewhat address this problem, depending on the information submitted, we refresh the existing sessions rather than creating a new one. There are two cases when a session is refreshed.

1. Frontend sends in a valid `update_token` through `/api/session/update/` POST request.
2. Frontend sends in the `device_token` through `/api/session/initialize/` GET request and there exists an old session associated with that `device_token`. This means that the user has subscribed to mobile push notifications on a specific device (i.e. we have access to `device_token`) and user is logging in from that same device. If there doesn't exist an old session, we create a new session for this device.

If we have access to the device's unique `device_token`, we can identify which device the user is trying to login from. Since we know that there can only be one instance of the app on a specific mobile device, we limit the number of sessions (=1) associated to that device.

### Clean-up Sessions

1. One way to clean up the sessions table is to delete any sessions associated with invalid device tokens.
   \
   A user's device token becomes invalid (most likely) in two cases:
      
    - if the user deletes the app from their device. Note that even if the user downloads the app again on the same device, the device token will not be identical. 
    - Whenever the token provider (i.e. Apple or Firebase) decides that they want to change the token

   If we know that the device token is invalid, there is no need to keep the associated session because it will never be used again.
   \
   We can find out if a device token is expired by examining the response when we send out a push notification to that `device_token`.

    - [IOS] [APNS response status code](https://developer.apple.com/library/archive/documentation/NetworkingInternet/Conceptual/RemoteNotificationsPG/CommunicatingwithAPNs.html#//apple_ref/doc/uid/TP40008194-CH11-SW15) for invalid device token is `410`.
    - [ANDROID] [Firebase exception](https://firebase.google.com/docs/reference/admin/python/firebase_admin.messaging#unregisterederror) for invalid device token is `UnregisteredError`. NOTE: Device token is equivalent to 'registration token' in Firebase terminology.

2. [WIP] Script to periodically clean up outdated sessions

## Original API endpoints (`/api`)

The examples below describe `/api`. See the v2 contract above for migrated clients.

### /api/session/initialize/• POST

**Body:**

```json
{
  "token": "<TOKEN received from Google>",
  "device_type": "ANDROID" || "IOS" || "WEB",
  "device_token": "123abc456def" || null
}
```

**Example Response:**

```json
{
  "success": true,
  "data": {
    "session_expiration": 1581435566,
    "session_token": "3c9e0ee538eaa570b7bc0847f18eab66703cc41f",
    "update_token": "d9c3427bd6537131a5d0e8c8fa1d59e764644c2c"
  },
  "timestamp": 1581335566
}
```

### /api/session/update/• POST

**Headers:**

```json
{
  "Authorization": "Bearer <update_token>"
}
```

**Example Response:**

```json
{
  "success": true,
  "data": {
    "session_expiration": 1581435566,
    "session_token": "3c9e0ee538eaa570b7bc0847f18eab66703cc41f",
    "update_token": "d9c3427bd6537131a5d0e8c8fa1d59e764644c2c"
  },
  "timestamp": 1581335566
}
```

### /api/users/tracking/ • GET

**Headers:**

```json
{
  "Authorization": "Bearer <access_token>"
}
```

**Example Response:**

```json
{
  "success": true,
  "data": {
    "sections": [
      {
        "catalog_num": 12401,
        "course_id": 1298,
        "course_num": 3110,
        "instructors": ["Nate Foster (jnf27)"],
        "is_tracking": true,
        "mode": "Online",
        "num_tracking": 2,
        "section": "LEC 001 / TR 12:20pm - 1:10pm",
        "status": "WAITLISTED",
        "subject_code": "CS",
        "title": "Data Structures and Functional Programming"
      },
      {
        "catalog_num": 12403,
        "course_id": 1298,
        "course_num": 4090,
        "instructors": [],
        "is_tracking": true,
        "mode": "Online",
        "num_tracking": 2,
        "section": "IND 606 / TBA",
        "status": "OPEN",
        "subject_code": "CEE",
        "title": "CEE Undergraduate Research"
      }
    ]
  },
  "timestamp": 1581335566
}
```

### /api/users/device-token/ • POST

**Headers:**

```json
{
  "Authorization": "Bearer <access_token>"
}
```

**Body:**

```json
{
  "device_token": "123abc456def"
}
```

**Example Response:**

```json
{
  "success": true,
  "data": null,
  "timestamp": 1581335566
}
```

### /api/users/notification/ • POST

**Headers:**

```json
{
  "Authorization": "Bearer <access_token>"
}
```

**Body:**

```json
{
  "notification": "ANDROID" || "IOS" || "EMAIL" || "NONE"
}
```

**Example Response:**

```json
{
  "success": true,
  "data": null,
  "timestamp": 1581335566
}
```

### /api/sections/track/ • POST

**Headers:**

```json
{
  "Authorization": "Bearer <access_token>"
}
```

**Body:**

```json
{
  "course_id": 12401
}
```

**Example Response:**

```json
{
  "success": true,
  "data": {
    "catalog_num": 12401,
    "course_id": 1298,
    "course_num": 3110,
    "instructors": ["Staff"],
    "is_tracking": true,
    "mode": "Online",
    "num_tracking": 2,
    "section": "DIS 212 / TR 12:20pm - 1:10pm",
    "status": "CLOSED",
    "subject_code": "CS",
    "title": "Data Structures and Functional Programming"
  },
  "timestamp": 1581335566
}
```

### /api/sections/untrack/ • POST

**Headers:**

```json
{
  "Authorization": "Bearer <access_token>"
}
```

**Body:**

```json
{
  "course_id": 12401
}
```

**Example Response:**

```json
{
  "success": true,
  "data": {
    "catalog_num": 12401,
    "course_id": 1298,
    "course_num": 3110,
    "instructors": ["Staff"],
    "is_tracking": false,
    "mode": "Online",
    "num_tracking": 2,
    "section": "DIS 212 / TR 12:20pm - 1:10pm",
    "status": "OPEN",
    "subject_code": "CS",
    "title": "Data Structures and Functional Programming"
  },
  "timestamp": 1581335566
}
```

### /api/courses/search/ • POST

**Headers:**
* Auth header is NOT required - allows web users to search for courses even when they are not logged in
* IMPORTANT
  * If auth header is not present
    * 'is_tracking' is always False
    * no error thrown about authentication
  * If auth header is present
    * a verification process is triggered -> checks whether the given access_token is valid
    * error could be thrown if access_token is invalid
    * 'is_tracking' depends on user's data
```json
{
  "Authorization": "Bearer <access_token>"
}
```

**Body:**

```json
{
  "query": "cs 3110"
}
```

**Example Response:**

```json
{
  "success": true,
  "data": {
    "courses": [
      {
        "subject_code": "CS",
        "course_num": 3110,
        "id": 1298,
        "title": "Object-Oriented Programming and Data Structures",
        "sections": [
          {
            "catalog_num": 12401,
            "course_id": 1298,
            "course_num": 3110,
            "instructors": ["Staff"],
            "is_tracking": false,
            "mode": "Online",
            "num_tracking": 2,
            "section": "DIS 212 / TR 12:20pm - 1:10pm",
            "status": "OPEN",
            "subject_code": "CS",
            "title": "Data Structures and Functional Programming"
          }
        ]
      }
    ],
    "query": "cs 3110"
  },
  "timestamp": 1581335566
}
```
### /api/courses/<int:course_id>/ • GET

**Headers:**
* Auth header is NOT required - allows web users to get course by id even when they are not logged in
```json
{
  "Authorization": "Bearer <access_token>"
}
```

**Example Response:**

```json
{
    "data": {
        "course_num": 3110,
        "id": 1298,
        "sections": [
            {
                "catalog_num": 10027,
                "course_id": 1298,
                "course_num": 3110,
                "instructors": [
                    "Nate Foster (jnf27)",
                    "Justin Hsu (jah659)"
                ],
                "is_tracking": false,
                "mode": "In Person",
                "num_tracking": 2,
                "section": "LEC 001 / MWF 11:20am",
                "status": "OPEN",
                "subject_code": "CS",
                "title": "Data Structures and Functional Programming"
            }
        ],
        "subject_code": "CS",
        "title": "Data Structures and Functional Programming"
    },
    "success": true,
    "timestamp": 1636588184
}
```

