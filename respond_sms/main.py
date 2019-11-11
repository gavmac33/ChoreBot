from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
from google.cloud import bigquery
import pandas


app = Flask(__name__)

# Definitions of global constants
_POSITIVE_RESPONSES = ['yes', 'y', 'ye', 'complete']
_NEGATIVE_RESPONSES = ['no', 'n']
_HELP_RESPONSES = ['option', 'o', 'op', 'opt']
_MICROMANAGE_RESPONSES = ['micromanage', 'micro', 'mic', 'm']
_STATUS_RESPONSES = ['status', 's', 'st', 'sta', 'stat']
_CHORE_WHEEL_PATH = "chore-bot-257803.ChoreBot.choreWheel"

@app.route("/sms", methods=['GET', 'POST'])
def responder(useless_arg):
    phoneNum, body = parseApiCall(request.values) # dict containing data about response

    if body in _POSITIVE_RESPONSES:
        response = updateStatus(phoneNum)
    elif body in _NEGATIVE_RESPONSES:
        response = noHandler()
    elif body in _HELP_RESPONSES:
        response = help()
    elif body in _MICROMANAGE_RESPONSES:
        response = micromanage(phoneNum)
    elif body in _STATUS_RESPONSES:
        response = statusHandler(phoneNum)
    else:
        response = "I don't recognize that command." + help()

    # text person back
    text = MessagingResponse()  # prepare a response
    text.message(response)
    return str(text)

# how to add a response
# resp = MessagingResponse()
# # Add a message
# resp.message(message here)

def parseApiCall(data):
    phoneNum = data.get('From')
    body = data.get('Body').lower().strip()  # make lower and strip leading spaces
    return phoneNum, body


def noHandler():
    """
    Updates DB for a No response, and does whatever else it needs to
    :return: string to text back to user
    """
    return "ChoreBot: I'm sad that you haven't completed your chores yet. Please finish them by Sunday to make me happy :("


def statusHandler(phoneNum):
    """
    Default handler if text is neither Yes or No. Probable sends the person back
    their chore for the week
    :return:
    """

    QUERY = "SELECT * FROM `%s`" % (_CHORE_WHEEL_PATH)

    bq_client = bigquery.Client()
    query_job = bq_client.query(QUERY)  # API request
    rows_df = query_job.result().to_dataframe()  # Waits for query to finish

    for index, row in rows_df.iterrows():
        if str(row["number"]) == phoneNum:
            if row["choreStatus"]:
                return "ChoreBot: You finished doing " + str(row["chore"]) + " already. I am very happy :)"
            else:
                return "ChoreBot: Your chore for this week is " + str(row["chore"]) + ". Please finish it by Sunday or I will be angry!"

    return "ChoreBot: Error- I am unable to find your chore"


def updateStatus(phoneNum):
    """
    Default handler if text is neither Yes or No. Probable sends the person back
    their chore for the week
    :return:
    """
    QUERY = "UPDATE `%s` SET choreStatus = TRUE WHERE number = '%s'" % (_CHORE_WHEEL_PATH, phoneNum)

    bq_client = bigquery.Client()
    query_job = bq_client.query(QUERY)  # API request
    query_job.result()  # Waits for query to finish

    return "ChoreBot: Thank you for finishing your chores!"


def help():
    return '''
    ChoreBot: 
    I respond to the following options:
    Option(O): View my options
    Micromange(M): See who has and hasn't completed their chores
    Status(S): Remind yourself what your chore is, and whether you have completed it
    Complete: Mark your chore as completed
    '''

def micromanage(phoneNum):
    QUERY = "SELECT * FROM `%s`" % (_CHORE_WHEEL_PATH) # read whole database
    # Other query that should work but not using for now in line below:
    # QUERY = "SELECT groupName FROM `%s` WHERE number = '%s'" % (_CHORE_WHEEL_PATH, phoneNum)

    bq_client = bigquery.Client()
    query_job = bq_client.query(QUERY)  # API request
    rows_df = query_job.result().to_dataframe()  # Waits for query to finish

    groupName = ""
    # find groupName based on current phoneNum
    for index, row in rows_df.iterrows():
        if row["number"] == phoneNum:
            groupName = row["groupName"]
            break

    if groupName == "":
        return "ChoreBot: I'm unable to find records of you, check to see if you're registered with ChoreBot"

    msg = "ChoreBot: "
    for index, row in rows_df.iterrows():
        if groupName == row["groupName"]:
            msg += "\n%s: %s, %s" % (row["name"], row["chore"], ("COMPLETED" if row["choreStatus"] else "INCOMPLETE"))

    return msg

