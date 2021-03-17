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


# Creating basic lists, collections, and variables

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


# Defining key classes & functions

def connectFunc(modifier="modify"): 
    """
    Runs the main code used by the Gmail API to connect to the user's Gmail account.
    Arguments:

        modifier (str, optional): A string given to the "SCOPES" variable, determines the permissions given to the program. See the chart listen in "Notes" for all valid

        strings and the permissions they allow.

    Notes:

        When ran for the first time, the user will be directed to a URL printed in the console. This URL will allow the user to officially connect the script
        to their Gmail account, but will be marked as an 'unsafe' link innitially, as this program is not officially verified by Google. 
        Chart of all valid "modifier" values:

            labels           | Allows the program to create, read, and delete the label's of individual emails.
            send             | Allows the program to send messages only, does not allow the program to modify or read messages.
            readonly         | Allows the program to read all resources and their metadata, blocks all writing operations
            compose          | Allows the program to create, read, update and delete drafts, as well as sending messages and drafts.
            insert           | Allows the program to insert and import messages exclusively
            modify           | Allows the program to perform all reading/writing operations, with the exception of permanent and immediate deletion of threads and messages.
            metadata         | Allows the program to read resources metadata, except for the content of message bodies and attachments.
            settings.basic   | Allows the program to manange basic mail settings.
            settings.sharing | Allows the program to manage sensitive mail settings, such as forwarding rules and aliases. Restricted to admin use.
            
        This chart based on the offical Gmail API page: https://developers.google.com/gmail/api/auth/scopes 
    """

    SCOPES = [f'https://www.googleapis.com/auth/gmail.{modifier}']    
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


class Email:
    """
    Stores information about a given email.

    Variables:

        details (dict): A dictionary created by the program containing the email address, subject line, sender's name, and time of filtering or starring of the given email.

    Notes:

        Keys of the "details" dict: name, address, subject, time

        Within the program, this class is used to store the info about emails that have been either archieved or starred. If the given email causes an error during either process,
        an "ErrorEmail" object is created instead.
    """

    def __init__(self, details):

        self.dict = details
        self.name = details["name"]
        self.address = details["address"]
        self.subject = details["subject"]
        self.time = details['time']   


class ErrorEmail:
    """
    Stores the information about emails which have caused an error during the filtering process. 

    Variables:

        address (str): The email address of the email responsible for the error.
        time (str): The time the given email was filtered.

    Notes:

        Stores a rather limited amount of information when compared to the "Email" class, only storing the given emails address and time archived.

        The error which causes these objects to be created is a "UnicodeEncodingError," caused when a filtered email contains certain special characters or emojis 
        in its sender's name or subject line. When the script is writing this information to the "Spam.txt" file, this error is raised, and the limited amount of info given to 
        this class is given to the file.
    """

    def __init__(self, err_details):

        self.address = err_details["address"]
        self.time = err_details["time"]


def counterFunc(name_arr, compare_arr):
    """
    Counts the number of times an Email or ErrorEmail object in a list appears that holds specific 'address' variable from a list of email addresses.

    Arguments:
        name_arr (list): A list of Email or ErrorEmail objects to have their '.address' variables compared to a list of email address strings.

        compare_arr (list): The "list of email address strings" mentioned above. Contains the strings of every email address to have Email or 
        ErrorEmail objects compared against.

    Returns:
        count_dataDict (dict): A dictionary with every email address given in the "compare_arr" argument as each key, and the number of times an Email or
        ErrorEmail object within the "name_arr" argument had the same address as their ".address" attribute as the paired value, specifically stored 
        as an integer. Note that email addresses with no matching emails found will not have an entry in thos dictionary.

    Nores:
    
        TIME COMPLEXITY:

            Note that this function is inefficient on large scales, as the time complexity is O(n*l), where n is equivalent to the first argument, and the l to 
            the second.
    """

    count_dataDict = {}   

    for address in compare_arr:

        count = []

        for item in name_set:
            
            try:
                item.address == address
                count.append(item)

            except AttributeError:
                pass   

        if len(count) > 0:    
            count_dataDict[address] = len(count)

    return count_dataDict


class Filter:
    """
    Contains all of the information and methods used to filter one's Gmail inbox. Has the ability to function of automatically archiving and starring Emails.

    Variables:
        filtered_list (list): A list of email adresses, emails from senders with these email addresses will be archived automatically.

        filtered_name (list): A list of email names, emails from senders with these names will be archived.

        starred list (list): A list of email adresses, emails from senders with these email addresses will be starred and left unread.

        starred_name (list): A list of email names, emails from senders with these names will be starred and left unread.

    Methods:
        filterFunc(self, message, message_dataDict)

        analyzeDataFunc(message)   STATIC METHOD

        mainFunc(self, num)
    """

    def __init__(self, filtered_list, filtered_name, starred_list, starred_name):

        self.filtered_list = filtered_list
        self.filtered_name = filtered_name

        self.starred_list = starred_list
        self.starred_name = starred_name


    def filterFunc(self, message, message_dataDict):
        """
        When presented with an individual email will check if it matches a specific list of sender's names and addresses, then automatically archives or stars the message accordingly.

        Arguments:
            message: The ID which refers to a specific email in the user's inbox. Used in the Gmail API code written by Google, data type unkown. 

            message_dataDict (dict): A dictionary containing the specific details used to categorize filtered emails. Will always contain at least an email address marked with the 
            "address" key. Is meant to be recieved from the "analyzedDataFunc" method.
        """

        if message_dataDict['address'] in self.filtered_list or message_dataDict['name'] in self.filtered_name:

            service.users().messages().modify(userId="me", id=message["id"], body={"removeLabelIds": ["INBOX"]}).execute()
            service.users().messages().modify(userId="me", id=message["id"], body={"removeLabelIds": ["UNREAD"]}).execute()

            message_dataDict['time'] = datetime.now().strftime(time_Form)   

            spam_class.append(Email(message_dataDict))    

            with open("Spam.txt", "a") as spam_log:    
                try:
                    spam_log.write(f"Filtered at {message_dataDict['time']}: From {message_dataDict['name']} with the address {message_dataDict['address']}, {message_dataDict['subject']}\n\n")

                except UnicodeEncodeError: 

                    spam_log.write(f"Filtered, {message_dataDict['time']}, {message_dataDict["address"]}: CRITICAL ENCODING ERROR!\n\n")  

                    error_class.append(ErrorEmail(message_dataDict))
                    logging.error(f"{message_dataDict['time']} - Critical encoding error, filtered, {message_dataDict['address']}")  


        elif message_dataDict['address'] in self.starred_list or message_dataDict['name'] in self.starred_name:    
            service.users().messages().modify(userId="me", id=message["id"], body={"addLabelIds": ["STARRED"]}).execute()

            message_dataDict['time'] = datetime.now().strftime(time_Form)

            # Starred emails do not have objects created to represent them, nor will they be recorded in a text document. This is with the exception that the 
            # email in question raises a UnicodeEncodeError, in which case an ErrorEmail object will be createdm and the error will be logged.

            with open("Spam.txt", "a") as spam_log:
                try:
                    spam_log.write(f"Starred at {message_dataDict['time']}: From {message_dataDict['name']} with the address {message_dataDict['address']}, {message_dataDict['subject']}\n\n")

                except UnicodeEncodeError:
                    spam_log.write(f"Starred, {message_dataDict['time']}: CRITICAL ENCODING ERROR!\n\n")

                    error_class.append(ErrorEmail(message_dataDict))
                    logging.error(f"{message_dataDict['time']} - Critical encoding error, starred, {message_dataDict['address'], message_dataDict['time']}")


    @staticmethod
    def analyzeDataFunc(message):
        """
        A static method that records and summerizes the address, sender name, and subject of an individual Email in the form of a dictionary.

        Arguments:
            message: The ID which refers to a specific email in the user's inbox. Used in the Gmail API code written by Google, data type unkown. The very same "message"
            variable used in the "filterFunc" method.

        Returns:
            dict: The dictionary mentioned in the description whichholds the categorized information about the emails. 

        Notes:
            The keys of the returned dictionary are: 

            "address"
            "name"
            "subject"

            Each hold the email's from address, sender's name, and subject line, in that order.
        """

        email_data = service.users().messages().get(userId="me", id=message["id"]).execute()["payload"]["headers"]  

        dataDict = {}    

        for values in email_data:   
            name = values["name"]

            if name == "From":

                from_details = values["value"].split()    


                try:
                    dataDict['address'] = from_details[-1]    

                except UnicodeEncodeError:   
                    dataDict['address'] = "MESSAGE ENCODING ERROR"
                    logging.error(f"{datetime.now().strftime(time_Form)} - Encoding error, address")


                try:
                    dataDict['name'] = "".join(from_details[0:-1])    

                except UnicodeEncodeError:
                    dataDict['name'] = "MESSAGE ENCODING ERROR"
                    logging.error(f"{datetime.now().strftime(time_Form)} - Encoding error, name")

                    
            elif name == "Subject":    

                try:
                    subject = values["value"]

                except UnicodeEncodeError:
                    subject = "MESSAGE ENCODING ERROR"
                    logging.error(f"{datetime.now().strftime(time_Form)} - Encoding error, subject")


                dataDict['subject'] = subject

        return dataDict    


    def mainFunc(self, num):
        """
        Executes the main related methods of the "Email" class and logs the times the inbox was checked and filtered.

        Arguments:
            num (int): An integer used to mark the number of times the method has been run, used exclusively in the logging of the process the program is executing.

        Notes:
            This method essentially gathers the user's inbox info, logs the number of times it's been run, then runs the "filterFunc" method if there are unread messages
            in the inbox. The "filterFunc" method recieves the returned value "analyzeDataFunc" as its second argument.
        """

        messages = service.users().messages().list(userId='me', labelIds=["INBOX"], q="is:unread").execute().get('messages', [])

        with open("Spam.txt", "a") as spam_log:    
            spam_log.write(f"===== - Check {num} - {datetime.now().strftime(time_Form)} - =====\n\n")

        num += 1 

        if not messages:
            pass

        else:

            for message in messages:
                self.filterFunc(message, self.analyzeDataFunc(message))
            
        return num


def nukeFunc():
    """
    Completely deletes every single email in the user's inbox without checking the message's content or email address. A joke function, not recommended for serious usage.

    Notes:
        Does serve a pratical use, but does so with reckless abandon. Content is sent to the trash and will be permanently deleted, no matter the contents of the emails
        it's deleting. DO NOT USE LIGHTLY.
    """

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

if __name__ == '__main__':

    with open("Spam.txt", "a") as spam_log:
        spam_log.write(f"\n======== - {datetime.now().strftime(full_Form)} - START OF LOG - ========\n\n")    

    connectFunc()

    myFilter = Filter(spam_list, spam_name, star_list, star_name) 


# Execution of the key function(s)

    num = 1

    while True:

        num = myFilter.mainFunc(num)

        time.sleep(900)

