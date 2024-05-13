import os
from google.auth.transport.requests import Request
import google.oauth2.credentials
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import json
import base64
import re
from datetime import datetime
from email.utils import parsedate_to_datetime
import httplib2
from gpt import summarizeByEmoji

class Email:
    def __init__(self, original_index, date, sender, to, subject, body, emoji):
        self.original_index = original_index
        self.date = date
        self.sender = sender
        self.to = to
        self.subject = subject
        self.body = body
        self.emoji = emoji
        self.numbers = {
            "All": None,
            "Sender": None,
            "Date": None,
            "Title": None,
            "Body": None,
        }


    def record_order_byCondition(self, condition, number):
        self.numbers[condition] = number


    def to_dict(self):
        return {
            "original_index": self.original_index,
            "date": self.date,
            "sender": self.sender,
            "to": self.to,
            "subject": self.subject,
            "body": self.body,
            "emoji": self.emoji,
            "numbers": self.numbers,
        }
    # for experiment data of inbox(readonly)
    @classmethod  
    def from_dict(cls, data):
        return cls(
            original_index=data.get("original_index"),
            date=data.get("date"),
            sender=data.get("sender"),
            to=data.get("to"),
            subject=data.get("subject"),
            body=data.get("body"),
            emoji=data.get("emoji")
        )



def get_header(headers, name):
    for h in headers:
        if h['name'].lower() == name:
            return h['value']


def base64_decode(data):
    return base64.urlsafe_b64decode(data).decode()


def base64_decode_file(data):
    return base64.urlsafe_b64decode(data.encode('UTF-8'))


def get_body(body):
    if body['size'] > 0:
        return base64_decode(body['data'])


def get_parts_body(body):
    if (body['size'] > 0
            and 'data' in body.keys()
            and 'mimeType' in body.keys()
            and body['mimeType'] == 'text/plain'):
        return base64_decode(body['data'])


def get_parts(parts):
    for part in parts:
        if part['mimeType'] == 'text/plain':
            b = base64_decode(part['body']['data'])
            if b is not None:
                return b
        if 'body' in part.keys():
            b = get_parts_body(part['body'])
            if b is not None:
                return b
        if 'parts' in part.keys():
            b = get_parts(part['parts'])
            if b is not None:
                return b


def get_attachment_id(parts):
    for part in parts:
        if part['mimeType'] == 'image/png':
            return part['body']['attachmentId'], 'png'
    return None, None

def get_user_info(creds):
    """Send a request to the UserInfo API to retrieve the user's information.

    Args:
    credentials: oauth2client.client.OAuth2Credentials instance to authorize the
                    request.
    Returns:
    User information as a dict.
    """
    user_info_service = build(
        serviceName='oauth2', version='v2',
        credentials=creds)

    user_info = None
    user_info = user_info_service.userinfo().get().execute()

    if user_info:
        return user_info['email']
    
def dict_to_credentials(cred_dict):
    return Credentials(
        token=cred_dict["token"],
        refresh_token=cred_dict["refresh_token"],
        token_uri=cred_dict["token_uri"],
        client_id=cred_dict["client_id"],
        client_secret=cred_dict["client_secret"],
        scopes=cred_dict["scopes"]
    )

def get_email_data(credentials):

    creds = dict_to_credentials(credentials)
    # scopes = ['https://mail.google.com/', 
    #           'https://www.googleapis.com/auth/gmail.readonly',
    #           'https://www.googleapis.com/auth/userinfo.email',
    #           'https://www.googleapis.com/auth/userinfo.profile']

    # emailaddress = get_user_info(creds)
    # scopes = ['https://www.googleapis.com/auth/gmail.readonly']

    # creds = None
    # # # The file token.json stores the user's access and refresh tokens, and is
    # # # created automatically when the authorization flow completes for the first
    # # # time.
    # expires_at = str(token['expires_at'])
    # token_filepath = 'record/token/' + expires_at.split('@')[0] + '-token.json'
    # if os.path.exists(token_filepath):
    #     os.remove(token_filepath)
    #     creds = Credentials.from_authorized_user_file(token_filepath, scopes)
    # # If there are no (valid) credentials available, let the user log in.
    # if not creds or not creds.valid:
    #     if creds and creds.expired and creds.refresh_token:
    #         creds.refresh(Request())
    #     else:
    #         flow = InstalledAppFlow.from_client_secrets_file(
    #         "client_secret.json", scopes
    #         )
    #         creds = flow.credentials
    #     # Save the credentials for the next run
    #     # with open(token_filepath, "w") as token:
    #     #     token.write(creds.to_json())
    emailaddress = get_user_info(creds)

    # creds = Credentials.from_authorized_user_file('token.json', scopes)
    service = build('gmail', 'v1', credentials=creds)
    messages = service.users().messages().list(
        userId='me',
        q='newer_than:3d',
        maxResults=10,
        includeSpamTrash=True
    ).execute().get('messages', [])

    emails = []

    for index, message in enumerate(messages):
        m_data = service.users().messages().get(
            userId='me',
            id=message['id']
        ).execute()
        
        headers = m_data['payload']['headers']

        date_header = get_header(headers, 'date')
        message_date = parsedate_to_datetime(date_header)

        now = datetime.now(message_date.tzinfo)

        if message_date.date() == now.date():
            formatted_date = message_date.strftime('%H:%M')
        else:
            formatted_date = message_date.strftime('%d %b')

        sender = get_header(headers, 'from')
        from_name = re.search(r"(.+?) <", sender)
        if from_name:
            from_name = from_name.group(1)

        to_date = get_header(headers, 'to')
        sub_date = get_header(headers, 'subject')\
        
        # TODO:GPT4
        emoji = summarizeByEmoji(sub_date)

        body = m_data['payload']['body']
        body_data = get_body(body)

        parts_data = None
        if 'parts' in m_data['payload']:
            parts = m_data['payload']['parts']
            parts_data = get_parts(parts)

        body_result = f"{body_data}" if body_data is not None else f"{parts_data}"

        email = Email(index, formatted_date, from_name, to_date, sub_date, body_result, emoji)
        emails.append(email)

    return emails, emailaddress


# if __name__ == '__main__':
#    main()
