from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
from google.cloud import bigquery
import pandas


app = Flask(__name__)

positiveResponse = ['yes', 'y', 'ye', 'complete']
negativeResponse = ['no', 'n']
helpResponse = ['option', 'o', 'op', 'opt']
micromanageResponse = ['micromanage', 'micro', 'mic', 'm']
statusResponse = ['status', 's', 'st', 'sta', 'stat']

@app.route("/sms", methods=['GET', 'POST'])
def responder(useless_arg):
    phoneNum, body = parseApiCall(request.values) # dict containing data about response

    if body in positiveResponse:
        response = updateStatus(phoneNum)
    elif body in negativeResponse:
        response = noHandler()
    elif body in helpResponse:
        response = help()
    elif body in micromanageResponse:
        response = micromanage()
    elif body in statusResponse:
        response = defaultHandler(phoneNum)
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


def defaultHandler(phoneNum):
    """
    Default handler if text is neither Yes or No. Probable sends the person back
    their chore for the week
    :return:
    """
    print(phoneNum)

    QUERY = "SELECT * FROM `chore-bot-257803.ChoreBot.choreWheel`"

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
    QUERY = "UPDATE `chore-bot-257803.ChoreBot.choreWheel` SET choreStatus = TRUE WHERE number = '" + phoneNum + "'"

    bq_client = bigquery.Client()
    query_job = bq_client.query(QUERY)  # API request
    query_job.result()  # Waits for query to finish

    return "ChoreBot: Thank you for finishing your chores!"


def help():
    return '''
    ChoreBot: 
    I respond to the following options:
    option(O): View my options
    micromange(M): See who has and hasn't completed their chores
    status(S): Remind yourself what your chore is, and whether you have completed it
    complete: Mark your chore as completed
    '''

def micromanage():
    QUERY = "SELECT * FROM `chore-bot-257803.ChoreBot.choreWheel`"

    bq_client = bigquery.Client()
    query_job = bq_client.query(QUERY)  # API request
    rows_df = query_job.result().to_dataframe()  # Waits for query to finish

    names = []
    completed = []
    chores = []

    for index, row in rows_df.iterrows():
        names.append(row["name"])
        completed.append(row["choreStatus"])
        chores.append(row["chore"])

    msg = ""
    for i in range(len(names)):
        msg += "\n" + names[i] + ": " + chores[i] + ", " + ("COMPLETED" if completed[i] else "INCOMPLETE")

    return msg

