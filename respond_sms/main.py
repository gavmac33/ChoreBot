from flask import Flask, request
from twilio.rest import Client
from twilio.twiml.messaging_response import MessagingResponse
import firebase_admin
from firebase_admin import firestore
from google.cloud import exceptions as gcloud_exceptions
import os


def env_vars(request):
    return os.environ.get(request, 'Specified environment variable is not set.')

# Definitions of global constants
POSITIVE_RESPONSES = ['yes', 'y', 'ye', 'complete', 'c']
NEGATIVE_RESPONSES = ['no', 'n']
HELP_RESPONSES = ['option', 'o', 'op', 'opt']
MICROMANAGE_RESPONSES = ['micromanage', 'micro', 'mic', 'm']
STATUS_RESPONSES = ['status', 's', 'st', 'sta', 'stat']
EASTER_EGGS = ["hi chorebot", "hi chorebot!", "fuck you", "hey", "hey chorebot", "you single", "you single?"]

# Read in environment variables
CHORE_WHEEL_PATH = env_vars("CHORE_WHEEL_DB_PATH")
ACCOUNT_SID = env_vars("ACCOUNT_SID")
AUTH_TOKEN = env_vars("AUTH_TOKEN")

# Create messaging and database objects
SMS_CLIENT = Client(ACCOUNT_SID, AUTH_TOKEN)
app = Flask(__name__)
fire_app = firebase_admin.initialize_app()
DATABASE = firestore.client()


@app.route("/sms", methods=['GET', 'POST'])
def responder(useless_arg):
    phoneNum, body = parseApiCall(request.values) # dict containing data about response
    personalInfo = getPersonalInfo(phoneNum) # Get personal information about texter

    if not personalInfo:
        response = "ChoreBot: I'm sorry, I don't recognize you"
        text = MessagingResponse()  # prepare a response
        text.message("ChoreBot: " + response)
        return response

    if body.lower() in POSITIVE_RESPONSES:
        response = updateStatus(personalInfo)
    elif body.lower() in NEGATIVE_RESPONSES:
        response = noHandler(personalInfo)
    elif body.lower() in HELP_RESPONSES:
        response = help()
    elif body.lower() in MICROMANAGE_RESPONSES:
        response = micromanage(personalInfo)
    elif body.lower() in STATUS_RESPONSES:
        response = statusHandler(personalInfo)
    elif body.lower() in EASTER_EGGS:
        response = easterEggHandler(personalInfo, body.lower())
    elif body.split()[0].lower() == "poke":
        response = pokeHandler(personalInfo, body)
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
    body = data.get('Body').strip()  # make lower and strip leading spaces
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
    • Poke [name]: Poke a person in your suite to remind them to do their chore (e.g. \"Poke Gavin\")
    '''

def micromanage(personalInfo):
    member_infos = DATABASE\
        .collection(CHORE_WHEEL_PATH)\
        .where("Suite", "==", personalInfo["Suite"])\
        .get()

    msg = ""
    for member_doc in member_infos:
        member = member_doc.to_dict()
        msg += "\n• %s: %s,\n%s"\
               % (member["Name"], member["Chore"], ("COMPLETED" if member["choreStatus"] else "INCOMPLETE"))

    return msg


def easterEggHandler(personalInfo, message):
    if message == "hi chorebot":
        return "Hi " + personalInfo["Name"]
    elif message == "hi chorebot!":
        return "Hi " + personalInfo["Name"] + "!"
    elif message == "fuck you":
        return "Fuck you too, do your chores!"
    elif message == "hey" or message == "hey chorebot":
        return "hey " + personalInfo["Name"] + " ;)"
    elif message == "you single" or message == "you single?":
        return "For you, I'm single ;)"


def pokeHandler(personalInfo, messageBody):
    if len(messageBody.split()) != 2:
        return "Please send poking requests in the format \"Poke [name]\""
    else:
        whoToPoke = messageBody.split()[1].replace("[", "").replace("]", "")

    member_docs = DATABASE.collection(CHORE_WHEEL_PATH) \
        .where("Suite", "==", personalInfo["Suite"]) \
        .get()
    members = [member.to_dict() for member in member_docs]

    for member in members:
        if member["Name"].lower() == whoToPoke.lower():
            SMS_CLIENT.messages.create(
                to=member["Number"],
                from_="+16155517341",
                body="ChoreBot: %s, someone would like you to do your chore: %s"
                     % (member["Name"], member["Chore"])
            )
            return "I have passed along your concerns"

    notLocatedMessage = "I wasn't able to locate %s in your suite. These are the people I have listed in %s:"\
                        % (whoToPoke, personalInfo["Suite"])
    names = [member["Name"] for member in members]
    for name in names:
        notLocatedMessage += "\n• " + name

    return notLocatedMessage


def getPersonalInfo(phoneNum):
    try:
        return DATABASE\
            .collection(CHORE_WHEEL_PATH)\
            .document(phoneNum)\
            .get()\
            .to_dict()
    except gcloud_exceptions.NotFound:
        return None


