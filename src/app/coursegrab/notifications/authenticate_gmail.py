from os import environ, path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

# Gmail API scope
# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/gmail.send"]

def main():
    """Shows basic usage of the Gmail API."""
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if path.exists(environ["GMAIL_API_TOKEN"]):
        creds = Credentials.from_authorized_user_file(environ["GMAIL_API_TOKEN"], SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                environ["GMAIL_API_CREDENTIALS"], SCOPES)
            creds = flow.run_local_server(port=8080)
        # Save the credentials for the next run
        with open(environ["GMAIL_API_TOKEN"], 'w') as token:
            token.write(creds.to_json())

    service = build('gmail', 'v1', credentials=creds)
    print("\n\nSuccess!")

if __name__ == '__main__':
    main()
