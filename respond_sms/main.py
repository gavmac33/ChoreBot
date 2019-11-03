from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
from google.cloud import bigquery
import pandas
import os

app = Flask(__name__)

positiveResponse = ['yes', 'y', 'ye']
negativeResponse = ['no', 'n']


@app.route("/sms", methods=['GET', 'POST'])
def responder(arg):
    text = MessagingResponse()  # prepare a response
    data = request.values  # dict containing data about response
    # extract the data we want
    phoneNum = request.values.get('From')
    body = request.values.get('Body').lower().strip()  # make lower and strip leading spaces
    response = ""
    if body in positiveResponse:
        response = updateStatus(phoneNum)
    elif body in negativeResponse:
        response = noHandler()
    else:
        response = defaultHandler(phoneNum)


    # text person back
    text.message(response)
    return str(text)



# how to add a response
# resp = MessagingResponse()
# # Add a message
# resp.message(message here)


def noHandler():
    """
    Updates DB for a No response, and does whatever else it needs to
    :return: string to text back to user
    """
    return 'You replied no'  # temporary


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
            return "Your chore for this week is " + str(row["chore"])

    return "Error: unable to find your chore"

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


    return "Congratulations, you have completed your chores for the week!"