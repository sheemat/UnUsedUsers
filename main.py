
from __future__ import print_function
import datetime
from google.auth import default, iam
from google.auth.transport import requests
from google.oauth2 import service_account
from googleapiclient.discovery import build
from oauth2client.service_account import ServiceAccountCredentials

CLOUD_FUNCTION = False
CF_SUSPEND = False
SCOPES = ['https://www.googleapis.com/auth/admin.directory.user']
TOKEN_URI = 'https://accounts.google.com/o/oauth2/token'
# Email of the Service Account
SERVICE_ACCOUNT_EMAIL = 'testdwd@erudite-bonbon-323517.iam.gserviceaccount.com'
# Path to the Service Account's Private Key file
SERVICE_ACCOUNT_PKCS12_FILE_PATH = '/Users/mathew.roy/mathew/tf/gcpkey/gcp.p12'
CUSTOMER_ID = 'C03cmqlyp'
G_ADMIN_USER = 'admin@mathewroy.us'


def key_credentials():
    creds = ServiceAccountCredentials.from_p12_keyfile(SERVICE_ACCOUNT_EMAIL,SERVICE_ACCOUNT_PKCS12_FILE_PATH,'notasecret',scopes=SCOPES)
    creds2 = creds.create_delegated(G_ADMIN_USER)
    return creds2


def delegated_credentials(credentials, subject, scopes):
    try:
        updated_credentials = credentials.with_subject(subject).with_scopes(scopes)
    except AttributeError:
        request = requests.Request()
    # Refresh the default credentials. This ensures that the information
    # about this account, notably the email, is populated.
        credentials.refresh(request)

    # Create an IAM signer using the default credentials.
        signer = iam.Signer(
            request,
            credentials,
            credentials.service_account_email
        )

        # Create OAuth 2.0 Service Account credentials using the IAM-based
        # signer and the bootstrap_credential's service account email.
        updated_credentials = service_account.Credentials(
            signer,
            credentials.service_account_email,
            TOKEN_URI,
            scopes=scopes,
            subject=subject
        )
    except Exception:
        raise
    return updated_credentials


def getUsers(event, context):
    creds = None
    if CLOUD_FUNCTION:
        creds, project = default()
        creds2 = delegated_credentials(creds, G_ADMIN_USER, SCOPES)
    else:
        creds2 = key_credentials()
    service = build('admin', 'directory_v1', credentials=creds2)
    print('Getting the first 500 users in the domain')
    results = service.users().list(customer=CUSTOMER_ID, maxResults=500, orderBy='email').execute()
    users = results.get('users', [])
    date_of_today = datetime.datetime.today()
    print(date_of_today.isoformat())
    kill_list = []
    if not users:
        print('No users in the domain.')
    else:
        print('Users:')
        for user in users:
            #print(user)
            print(u'{0} ({1})'.format(user['primaryEmail'], user['name']['fullName']))
            print(user['lastLoginTime'])
            userLastLoginDate = datetime.datetime.strptime(user['lastLoginTime'], "%Y-%m-%dT%H:%M:%S.%fZ")
            #print(userLastLoginDate)
            num_days = abs((date_of_today - userLastLoginDate).days)
            print(num_days)
            if num_days > 90:
                kill_list.append(user['primaryEmail'])
    if CF_SUSPEND:
        print('Suspending Eligible Users')
        for x in kill_list:
            print(x)
            user = service.users().get(userKey=x).execute()
            user['suspended'] = True
            service.users().update(userKey=x, body=user).execute();
    else:
        print('List of Eligible Users')
        print(kill_list)


if __name__ == '__main__':
    event = None
    context = None
    getUsers(event, context)
