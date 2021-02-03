from __future__ import print_function
import sys
import schedule
import time
import pickle
import os.path
import logging
from datetime import datetime

from GmailApiModules.googleapiclient.discovery import build
from GmailApiModules.google_auth_oauthlib.flow import InstalledAppFlow
from GmailApiModules.google.auth.transport.requests import Request


# Setting up lists, collections, and variables

logging.basicConfig(filename="C:\\Users\\Xavier\\Documents\\GitHub\\GmailFilter\\Errors.Log", level=logging.ERROR)
logger = logging.getLogger()


spam_list = ["<The addresses of Emails you want to archive>"]

spam_name = ["<The names of the Emails you want to archive>"]

star_list = ["<The adresses of the Emails you want to star>"]

star_name = ["<The names of the Emails you want to star>"]


spam_class = []     # Optional to use, every filtered Email has an object created representing it automatically placed in this list.

error_class = []     # Similar to the list above, but holds emails which caused an encoding error.


time_Form = "%H:%M:%S"     # 'Form' is short for 'format,' shortened to prevent the program from running the "format" function. Show the time up to the hour.

full_Form = "%m/%d/%Y %H:%M:%S"     # See comment above. Shows the time up to the year.


MODIFIER = "modify"    # This string will be added to the end of the URL given to the SCOPES variable in order to more easily change the permissions of this program and its future variations.

"""
List of valid 'MODIFIER' strings, and how they affect the program's permissions when interacting with Gmail directly.

labels           | Allows the program to create, read, and delete the label's of individual emails.
send             | Allows the program to send messages only, does not allow the program to modify or read messages.
readonly         | Allows the program to read all resources and their metadata, blocks all writing operations
compose          | Allows the program to create, read, update and delete drafts, as well as sending messages and drafts.
insert           | Allows the program to insert and import messages exclusively
modify           | Allows the program to perform all reading/writing operations, with the exception of permanent and immediate deletion of threads and messages.
metadata         | Allows the program to read resources metadata, except for the content of message bodies and attachments.
settings.basic   | Allows the program to manange basic mail settings.
settings.sharing | Allows the program to manage sensitive mail settings, such as forwarding rules and aliases. Restricted to admin use
"""


# Defining key classes & functions

def connectFunc(modifier):    # Connects to the Gmail servers and the user's Gmail account

    SCOPES = [f'https://www.googleapis.com/auth/gmail.{modifier}']    # The URL shown to the user when the program is run for the first time determines what Gmail account the program will interact with.
                                                                      # It should be noted that the program may be automatically detected as 'unsafe' by Google depending on which permissions were granted
                                                                      # by the modifier given to the 'SCOPES' variable. This can be manually overridden in order to allow the program to continue functioning.
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

    global service                                       # The 'service' variable is made global both because it will not change based on the function used, and because it will be a key component in many actions taken 
    service = build('gmail', 'v1', credentials=creds)    # by the program.


class Email:    # The class used to represent any email message which doesn't cause a UnicodeEncodeError

    def __init__(self, details):

        self.dict = details
        self.name = details["name"]
        self.address = details["address"]
        self.subject = details["subject"]
        self.time = details['time']    # The 'time' key taken from the 'details' dictionary represents the time at which the email was filtered or starred.


class Error:    # The class used to represent any email object which does cause a UnicodeEncodeError during the filtering process, these objects are used in the error logger.

    def __init__(self, address, time):

        self.address = address
        self.time = time


def counterFunc(name_set, compare_set):    # A function which intakes 2 lists, 'compare_set' being a list of basic names/addresses to act as a benchmark, such as the 'spam_list' list, and 'name_set' being the list of actual Email/Error objects to compare, such as the 'spam_class' list.

    count_dataDict = {}    # A dictionary which has each email address from 'name_set' as a key and the number of times an object with a matching email appears in 'compare_set' as said key's paired value.

    for address in compare_set:

        count = []    # A temporary list including every Email/Error object which has a specific email address for the purpose of directly counting the number of said objects.

        for item in name_set:
            
            if item.address == address:
                count.append(item)    # Any Email/Error object with the specific address used in this iteration of the for loop will be added to this iteration's 'count' list.

        if len(count) > 0:    # If the number of Email/Error objects in the 'count' list is greater than 0:
            count_dataDict[address] = len(count)    # A new entry in the 'count_dataDict' dictionary is created.

    for key in count_dataDict:

        print(f"{key}: {count_dataDict[key]}\n")    # Lastly, the function will print out every email address/name provided in the 'name_set' alongside the number of times an object matching said address/name was present in the 'compare_set' list in the console.


class Filter:    # A class used to create personalized filters

    def __init__(self, filtered_list, filtered_name, starred_list, starred_name):

        self.filtered_list = filtered_list    # A list of email adresses, emails from senders with these email addresses will be archived 
        self.filtered_name = filtered_name    # A list of email names, emails from senders with these names will be archived

        self.starred_list = starred_list    # A list of email adresses, emails from senders with these email addresses will be starred and left unread 
        self.starred_name = starred_name    # A list of email names, emails from senders with these names will be starred and left unread 


    def filterFunc(self, message, message_dataDict):    # When presented with an individual email will check if it matches a specific list of sender's names and addresses, then automatically archives the message accordingly
        if message_dataDict['address'] in self.filtered_list or message_dataDict['name'] in self.filtered_name:
            service.users().messages().modify(userId="me", id=message["id"], body={"removeLabelIds": ["INBOX"]}).execute()
            service.users().messages().modify(userId="me", id=message["id"], body={"removeLabelIds": ["UNREAD"]}).execute()

            message_dataDict['time'] = datetime.now().strftime(time_Form)    # Defines the time at which the message was archived

            spam_class.append(Email(message_dataDict))    # Creates the individual Email object for this message, then adds it to a list of filtered messages

            with open("Spam.txt", "a") as spam_log:    # Records all the details of the filtered message as well as when it was filtered on a seperate text document, 'Spam.txt'
                try:
                    spam_log.write(f"Filtered at {message_dataDict['time']}: From {message_dataDict['name']} with the address {message_dataDict['address']}, {message_dataDict['subject']}\n\n")

                except UnicodeEncodeError:    # In the event that an email causes a UnicodeEncodeError while the message's details are being recorded on the 'Spam.txt' document:

                    spam_log.write(f"Filtered, {message_dataDict['time']}: CRITICAL ENCODING ERROR!\n\n")    # A special message is written to the 'Spam.txt' document indicating that an error ocurred.
                    error_class.append(Error(message_dataDict['address'], message_dataDict['time']))    # In addition to the regular 'Email' object created to represent the message after it was filtered, an 'Error' object is created and added to a seperate list.
                    logging.error(f"{message_dataDict['time']} - Critical encoding error, filtered, {message_dataDict['address']}")    # Finally, a message is sent to the 'Errors.Log' logging document indicating with which emails the error ocurred and when.


        elif message_dataDict['address'] in self.starred_list or message_dataDict['name'] in self.starred_name:    # The process above is repeated, however emails matching the criteria are starred rather than archived.
            service.users().messages().modify(userId="me", id=message["id"], body={"addLabelIds": ["STARRED"]}).execute()

            message_dataDict['time'] = datetime.now().strftime(time_Form)

            # In addition to the note above, starred emails do not have objects created to represent them, nor will they be recorded in a document unless they cause an Error.

            with open("Spam.txt", "a") as spam_log:
                try:
                    spam_log.write(f"Starred at {message_dataDict['time']}: From {message_dataDict['name']} with the address {message_dataDict['address']}, {message_dataDict['subject']}\n\n")

                except UnicodeEncodeError:
                    spam_log.write(f"Starred, {message_dataDict['time']}: CRITICAL ENCODING ERROR!\n\n")
                    error_class.append(Error(message_dataDict))
                    logging.error(f"{message_dataDict['time']} - Critical encoding error, starred, {message_dataDict['address'], message_dataDict['time']}")


    @staticmethod
    def analyzeDataFunc(message):    # A static method that records and summerizes the address, sender name, and subject of an Email

        email_data = service.users().messages().get(userId="me", id=message["id"]).execute()["payload"]["headers"]    # Email data is retrieved from the server for the individual message.

        dataDict = {}    # A dictionary that records the details of the message, which is then returned


        for values in email_data:    # Parces the data of the message. If certain peices of data are found, they are further broken down and recorded by the program in the following code.
            name = values["name"]

            if name == "From":

                from_details = values["value"].split()    # The string consisting of the 'From' data of the email is split into an easily parced list.


                try:
                    dataDict['address'] = from_details[-1]    # The very last item of this list is the sender's email address, which is then assigned to the 'address'  key in the 'dataDict' dictionary.

                except UnicodeEncodeError:    # In the event that encoding the address value produces an error, a replacement value is given indicating an error ocurred, and the error is logged. The same occurs with all other encoded values.
                    dataDict['address'] = "MESSAGE ENCODING ERROR"
                    logging.error(f"{datetime.now().strftime(time_Form)} - Encoding error, address")


                try:
                    dataDict['name'] = "".join(from_details[0:-1])    # All other items of the 'from_details' list are combined and recorded as the 'name' key in the 'dataDict' dictionary.

                except UnicodeEncodeError:
                    dataDict['name'] = "MESSAGE ENCODING ERROR"
                    logging.error(f"{datetime.now().strftime(time_Form)} - Encoding error, name")

                    
            elif name == "Subject":    # The 'Subject' data is directly recorded as the 'subject' key in the 'dataDict' dictionary.

                try:
                    subject = values["value"]

                except UnicodeEncodeError:
                    subject = "MESSAGE ENCODING ERROR"
                    logging.error(f"{datetime.now().strftime(time_Form)} - Encoding error, subject")


                dataDict['subject'] = subject

        return dataDict    


    def mainFunc(self, num):    # The main promary action taken by the filter, coordinates all the other disconnected parts of the filter.

        messages = service.users().messages().list(userId='me', labelIds=["INBOX"], q="is:unread").execute().get('messages', [])    # A list of all unread messages within the user's inbox are represented as this iterable.


        with open("Spam.txt", "a") as spam_log:    # The time in which the filter function is run is recorded in the 'Spam.txt' log
            spam_log.write(f"===== - Check {num} - {datetime.now().strftime(time_Form)} - =====\n\n")

        num += 1    # This 'num' integer is simply used to show how many cycles of filtering every 15 have passed in the text log.


        if not messages:
            pass

        else:

            for message in messages:
                self.filterFunc(message, self.analyzeDataFunc(message))    # The 'filterFunc' method is run, with the output of the 'analyzeDataFunc' as its 'message_dataDict' input. This is done for every message in the 'messages' list.
            
        return num


def nukeFunc():    # This is a completely optional and currently unused function which comepletely wipes the contents of a user's inbox. Was mostly created for shits and giggles.

    messages = service.users().messages().list(userId='me', labelIds=["INBOX"], q="is:unread").execute().get('messages', [])


    with open("Spam.txt", "a") as spam_log:
        spam_log.write(f"===== - TACTICAL NUKE, INCOMING! - {datetime.now().strftime(full_Form)}  - =====\n\n")


    if not messages:
        pass

    else:

        for message in messages:
            service.users().messages().modify(userId="me", id=message["id"], body={"addLabelIds": ["TRASH"]}).execute()

            service.users().messages().modify(userId="me", id=message["id"], body={"removeLabelIds": ["UNREAD"]}).execute()


# Basic Setup for Primary Functions

if __name__ == '__main__':    # The following execution of functions is placed after this statement in order to prevent the program from connecting to the Gmail server's and begin filtering emails when imported into other programs.

    with open("Spam.txt", "a") as spam_log:
        spam_log.write(f"\n======== - {datetime.now().strftime(full_Form)} - START OF LOG - ========\n\n")    # Whenever the program is run at all, this message is added to the text log. This shows the full date rather than just the time it was executed.

    connectFunc(MODIFIER)

    myFilter = Filter(spam_list, spam_name, star_list, star_name)    # The filter object is created, and the preset lists containing all the major filtering/starring information is sent to the class for this instance to be created.


# Execution of the key function(s)

    num = 1

    while True:

        num = myFilter.mainFunc(num)    # The 'mainFunc' method is run every 15 minutes in order to effectively filter constantly throught the day.

        time.sleep(900)    # The amount of time between each iteration of this for loop is determined by the argument given to this 'sleep' function. The argument is an integer, and is the number of seconds during which the program is to remain inactive.
