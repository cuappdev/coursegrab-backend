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

## User Sessions

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
   A user's device token becomes invalid if the user deletes the app from their device. Note that even if the user downloads the app again on the same device, the device token will not be identical. If we know that the device token is invalid, there is no need to keep the associated session because it will never be used again.
   \
   We can find out if a device token is expired by examining the response when we send out a push notification to that `device_token`.

- [IOS] [APNS response status code](https://developer.apple.com/library/archive/documentation/NetworkingInternet/Conceptual/RemoteNotificationsPG/CommunicatingwithAPNs.html#//apple_ref/doc/uid/TP40008194-CH11-SW15) for invalid device token is `410`.
- [ANDROID] [Firebase exception](https://firebase.google.com/docs/reference/admin/python/firebase_admin.messaging#unregisterederror) for invalid device token is `UnregisteredError`. NOTE: Device token is equivalent to 'registration token' in Firebase terminology.

2. [WIP] Script to periodically clean up outdated sessions

## Endpoints

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
        "course_num": 3110,
        "instructors": ["Nate Foster (jnf27)"],
        "is_tracking": true,
        "section": "LEC 001 / TR 12:20pm - 1:10pm",
        "status": "WAITLISTED",
        "subject_code": "CS",
        "title": "Data Structures and Functional Programming"
      },
      {
        "catalog_num": 12403,
        "course_num": 4090,
        "instructors": [],
        "is_tracking": true,
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
    "course_num": 3110,
    "instructors": ["Staff"],
    "is_tracking": true,
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
    "course_num": 3110,
    "instructors": ["Staff"],
    "is_tracking": false,
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
        "title": "Object-Oriented Programming and Data Structures",
        "sections": [
          {
            "catalog_num": 12401,
            "course_num": 3110,
            "instructors": ["Staff"],
            "is_tracking": false,
            "status": "OPEN",
            "section": "DIS 212 / TR 12:20pm - 1:10pm",
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
