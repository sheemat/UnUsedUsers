

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
from __future__ import print_function
import datetime
from datetime import date
from googleapiclient.discovery import build
from oauth2client.service_account import ServiceAccountCredentials


# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/admin.directory.user']

# Email of the Service Account
SERVICE_ACCOUNT_EMAIL = 'testdwd@erudite-bonbon-323517.iam.gserviceaccount.com'

# Path to the Service Account's Private Key file
SERVICE_ACCOUNT_PKCS12_FILE_PATH = '/Users/mathew.roy/mathew/tf/gcpkey/gcp.p12'


def main():
    """Shows basic usage of the Admin SDK Directory API.
    Prints the emails and names of the first 10 users in the domain.
    """
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    creds = ServiceAccountCredentials.from_p12_keyfile(
        SERVICE_ACCOUNT_EMAIL,
        SERVICE_ACCOUNT_PKCS12_FILE_PATH,
        'notasecret',
        scopes=['https://www.googleapis.com/auth/admin.directory.user'])

    user_email='admin@mathewroy.us'

    creds2 = creds.create_delegated(user_email)



    service = build('admin', 'directory_v1', credentials=creds2)

    # Call the Admin SDK Directory API
    print('Getting the first 10 users in the domain')
    results = service.users().list(customer='C03cmqlyp', maxResults=500, orderBy='email').execute()
    users = results.get('users', [])

    dateToday=datetime.datetime.today()
    print(dateToday.isoformat())


    killlist=[]

    if not users:
        print('No users in the domain.')
    else:
        print('Users:')
        for user in users:
            print (user)
            print(u'{0} ({1})'.format(user['primaryEmail'],user['name']['fullName']))
            print(user['lastLoginTime'])
            userLastLoginDate=datetime.datetime.strptime(user['lastLoginTime'], "%Y-%m-%dT%H:%M:%S.%fZ")
            print(userLastLoginDate)

            numdays=abs((dateToday - userLastLoginDate).days)
            print(numdays)
            if (numdays > 90):
                killlist.append(user['primaryEmail'])


    #print(killlist)

    for x in killlist:
        print(x)
        user = service.users().get(userKey=x).execute()
        user['suspended'] = True
        service.users().update(userKey=x, body=user).execute();



if __name__ == '__main__':
    main()