import json


def client_get(client, user, url):
    req = client.get(url, headers={"Authorization": "Bearer " + user.session_token})
    return json.loads(req.data)


def client_post(client, user, url, body):
    req = client.post(
        url,
        data=json.dumps(body),
        content_type="application/json",
        headers={"Authorization": "Bearer " + user.session_token},
    )
    return json.loads(req.data)
