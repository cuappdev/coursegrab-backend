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
The required environment variables for this API are the following:
```bash
export ANDROID_CLIENT_ID=""
export IOS_CLIENT_ID=""
export DB_FILENAME=""
export PORT=5000
```

To use `direnv` with this repository, run the following and set the variables appropriately.

```bash
cp envrc.template .envrc
```

## Style
**Flake 8**: Install [flake8](http://flake8.pycqa.org/en/latest/)

**Black**: Either use [command line tool](https://black.readthedocs.io/en/stable/installation_and_usage.html) or use [editor extension](https://black.readthedocs.io/en/stable/editor_integration.html). 

If using VS Code, install the 'Python' extension and include following snippet inside `settings.json`:
```  json
"python.linting.pylintEnabled": false,
"python.linting.flake8Enabled": true,
"python.formatting.provider": "black"
```

## Running the App
To run the app:

```
python src/run.py
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

## Endpoints
### /api/session/initialize/• POST
**Body:**
```json
{
  "token": "<TOKEN received from Google>",
  "is_ios": true
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
  }
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
  }
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
  "data": [
    {
      "catalog_num": 12401,
      "course_num": 3110,
      "section": "DIS 212 / TR 12:20pm - 1:10pm",
      "status": "WAITLISTED",
      "subject_code": "CS",
      "title": "Data Structures and Functional Programming"
    },
    {
      "catalog_num": 12403,
      "course_num": 4090,
      "section": "IND 606 / TBA",
      "status": "OPEN",
      "subject_code": "CEE",
      "title": "CEE Undergraduate Research"
    }
  ],
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
  "is_ios": true,
  "device_token": "123abc456def"
}
```
**Example Response:**
```json
{
  "success": true,
  "data": null
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
    "section": "DIS 212 / TR 12:20pm - 1:10pm",
    "status": "CLOSED",
    "subject_code": "CS",
    "title": "Data Structures and Functional Programming"
  }
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
    "section": "DIS 212 / TR 12:20pm - 1:10pm",
    "status": "OPEN",
    "subject_code": "CS",
    "title": "Data Structures and Functional Programming"
  }
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
    "subject_code": "CS",
    "course_num": 3110,
    "title": "Object-Oriented Programming and Data Structures",
    "sections": [
        {
            "catalog_num": 12401,
            "course_num": 3110,
            "status": "OPEN",
            "subject_code": "CS",
            "title": "Data Structures and Functional Programming"
        }
    ]
  }
}
```
