from __future__ import print_function
import sys
import schedule
import time
import datetime
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request


# Setting up lists/collections

spam_list = ["<The addresses of Emails you want to archive>"]

spam_name = ["<The names of the Emails you want to archive>"]

star_list = ["<The adresses of the Emails you want to star>"]

star_name = ["<The names of the Emails you want to star>"]

spam_class = []


# Connecting to Gmail servers, signing in

SCOPES = ['https://www.googleapis.com/auth/gmail.modify']

creds = None

if os.path.exists('token.pickle'):

    with open('token.pickle', 'rb') as token:
        creds = pickle.load(token)


if not creds or not creds.valid:

    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())

    else:
        flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)

        creds = flow.run_local_server(port=0)

    with open('token.pickle', 'wb') as token:
        pickle.dump(creds, token)

service = build('gmail', 'v1', credentials=creds)

with open("Spam.txt", "a") as spam_log:
    spam_log.write(f"\n======== - {(str(datetime.datetime.now()).split('.')[0]).split(' ')[1]} - START OF LOG - ========\n\n")


# Defining key classes & functions

class Email:

    def __init__(self, details):

        self.dict = details
        self.name = details["name"]
        self.address = details["address"]
        self.subject = details["subject"]
        

def counter(init_set, compare_set):

    count_data = {}

    for name in compare_set:

        count = []

        for item in init_set:
            
            if item.address == name:
                count.append(item)

        if len(count) > 0:
            count_data[name] = len(count)

    for key in count_data:

        print(f"{key}: {count_data[key]}\n")


def nuke():

    results = service.users().messages().list(userId='me', labelIds=["INBOX"]).execute()
    messages = results.get('messages', [])

    with open("Spam.txt", "a") as spam_log:
        spam_log.write(f"===== - TACTICAL NUKE, INCOMING! - {(str(datetime.datetime.now()).split('.')[0]).split(' ')[1]} - =====\n\n")


    if not messages:
        pass

    else:

        for message in messages:
            service.users().messages().modify(userId="me", id=message["id"], body={"addLabelIds": ["TRASH"]}).execute()

            service.users().messages().modify(userId="me", id=message["id"], body={"removeLabelIds": ["UNREAD"]}).execute()


def filterfunc(num):

    results = service.users().messages().list(userId='me', labelIds=["INBOX"], q="is:unread").execute()
    messages = results.get('messages', [])

    with open("Spam.txt", "a") as spam_log:
        spam_log.write(f"===== - Check {num} - {(str(datetime.datetime.now()).split('.')[0]).split(' ')[1]} - =====\n\n")

    num += 1

    if not messages:
        pass

    else:
        for message in messages:
            msg = service.users().messages().get(userId="me", id=message["id"]).execute()   

            email_data = msg["payload"]["headers"]

            message_data = {}


            for values in email_data:
                name = values["name"]


                if name == "From":

                    from_name = values["value"].split()

                    try:
                        message_data['address'] = from_name[-1]

                    except UnicodeEncodeError:
                         message_data.insert(1, "MESSAGE ENCODING ERROR")


                    try:
                        message_data['name'] = "".join(from_name[0:-1])

                    except UnicodeEncodeError:
                         message_data.insert(0, "MESSAGE ENCODING ERROR")

                
                elif name == "Subject":

                    try:
                        subject = values["value"]

                    except UnicodeEncodeError:
                         subject = "MESSAGE ENCODING ERROR"

                    message_data['subject'] = subject


            if from_name[-1] in spam_list or from_name[0:-1] in spam_name:
                service.users().messages().modify(userId="me", id=message["id"], body={"removeLabelIds": ["INBOX"]}).execute()

                service.users().messages().modify(userId="me", id=message["id"], body={"removeLabelIds": ["UNREAD"]}).execute()

                spam_class.append(Email(message_data))

                with open("Spam.txt", "a") as spam_log:

                    try:
                        spam_log.write(f"Filtered at {(str(datetime.datetime.now()).split('.')[0]).split(' ')[1]}: From {message_data['name']} with the address {message_data['address']}, {message_data['subject']}\n\n")

                    except UnicodeEncodeError:
                        spam_log.write(f"Filtered, {(str(datetime.datetime.now()).split('.')[0]).split(' ')[1]}: CRITICAL ENCODING ERROR!\n\n")


            elif from_name[-1] in star_list:
                service.users().messages().modify(userId="me", id=message["id"], body={"addLabelIds": ["STARRED"]}).execute()

                with open("Spam.txt", "a") as spam_log:

                    try:
                        spam_log.write(f"Starred at {(str(datetime.datetime.now()).split('.')[0]).split(' ')[1]}: From {message_data['name']} with the address {message_data['address']}, {message_data['subject']}\n\n")

                    except UnicodeEncodeError:
                        spam_log.write(f"Starred, {(str(datetime.datetime.now()).split('.')[0]).split(' ')[1]}: CRITICAL ENCODING ERROR!\n\n")


    return num


# Execution of the key function(s)

num = 1

if __name__ == '__main__':

   for numb in range(0, 10**10):

        num = filterfunc(num)

        time.sleep(900)
