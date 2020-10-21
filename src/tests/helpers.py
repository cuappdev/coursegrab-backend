import json


def client_get(client, session, url):
    req = client.get(url, headers={"Authorization": "Bearer " + session.session_token})
    return json.loads(req.data)


def client_post(client, session, url, body):
    req = client.post(
        url,
        data=json.dumps(body),
        content_type="application/json",
        headers={"Authorization": "Bearer " + session.session_token},
    )
    return json.loads(req.data)
