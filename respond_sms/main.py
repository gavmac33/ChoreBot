from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
import firebase_admin
from firebase_admin import firestore
from google.cloud import exceptions as gcloud_exceptions
import os


app = Flask(__name__)
fire_app = firebase_admin.initialize_app()
DATABASE = firestore.client()

def env_vars(request):
    return os.environ.get(request, 'Specified environment variable is not set.')

# Definitions of global constants
_POSITIVE_RESPONSES = ['yes', 'y', 'ye', 'complete', 'c']
_NEGATIVE_RESPONSES = ['no', 'n']
_HELP_RESPONSES = ['option', 'o', 'op', 'opt']
_MICROMANAGE_RESPONSES = ['micromanage', 'micro', 'mic', 'm']
_STATUS_RESPONSES = ['status', 's', 'st', 'sta', 'stat']
_CHORE_WHEEL_PATH = env_vars("CHORE_WHEEL_DB_PATH")


@app.route("/sms", methods=['GET', 'POST'])
def responder(useless_arg):
    phoneNum, body = parseApiCall(request.values) # dict containing data about response
    personalInfo = getPersonalInfo(phoneNum) # Get personal information about texter

    if not personalInfo:
        response = "ChoreBot: I'm sorry, I don't recognize you"
        text = MessagingResponse()  # prepare a response
        text.message("ChoreBot: " + response)
        return response

    if body in _POSITIVE_RESPONSES:
        response = updateStatus(personalInfo)
    elif body in _NEGATIVE_RESPONSES:
        response = noHandler(personalInfo)
    elif body in _HELP_RESPONSES:
        response = help()
    elif body in _MICROMANAGE_RESPONSES:
        response = micromanage(personalInfo)
    elif body in _STATUS_RESPONSES:
        response = statusHandler(personalInfo)
    else:
        response = "I don't recognize that command." + help()

    # text person back
    text = MessagingResponse()  # prepare a response
    text.message("ChoreBot: " + response)
    return str(text)

# how to add a response
# resp = MessagingResponse()
# # Add a message
# resp.message(message here)

def parseApiCall(data):
    phoneNum = data.get('From')
    body = data.get('Body').lower().strip()  # make lower and strip leading spaces
    return phoneNum, body


def noHandler(personalInfo):
    """
    Updates DB for a No response, and does whatever else it needs to
    :return: string to text back to user
    """
    return "I'm disappointed in you %s. Please finish %s by Sunday to make me happy :("\
           % (personalInfo["Name"], personalInfo["Chore"])


def statusHandler(personalInfo):
    """
    Default handler if text is neither Yes or No. Probable sends the person back
    their chore for the week
    :return:
    """

    if personalInfo["choreStatus"]:
        return "You finished doing %s already. I am very happy :)"\
               % (personalInfo["Chore"])
    else:
        return "Your chore for this week is %s. Please finish it by Sunday or I will be angry!"\
               % (personalInfo["Chore"])



def updateStatus(personalInfo):
    """
    Default handler if text is neither Yes or No. Probable sends the person back
    their chore for the week
    :return:
    """
    DATABASE\
        .collection("ChoreWheel")\
        .document(personalInfo["Number"])\
        .update({"choreStatus": True})

    return "Thank you for finishing your chores!"


def help():
    return '''I respond to the following options:
    • Option(O): View my options
    • Micromange(M): See who has and hasn't completed their chores
    • Status(S): Remind yourself what your chore is, and whether you have completed it
    • Complete(C): Mark your chore as completed
    '''

def micromanage(personalInfo):
    member_infos = DATABASE\
        .collection(_CHORE_WHEEL_PATH)\
        .where("Suite", "==", personalInfo["Suite"])\
        .get()

    msg = ""
    for member_doc in member_infos:
        member = member_doc.to_dict()
        msg += "\n• %s: %s,\n%s"\
               % (member["Name"], member["Chore"], ("COMPLETED" if member["choreStatus"] else "INCOMPLETE"))

    return msg


def getPersonalInfo(phoneNum):
    try:
        return DATABASE\
            .collection(_CHORE_WHEEL_PATH)\
            .document(phoneNum)\
            .get()\
            .to_dict()
    except gcloud_exceptions.NotFound:
        return None


