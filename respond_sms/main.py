from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
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
        response = yesHandler()
    elif body in negativeResponse:
        response = noHandler()
    else:
        response = defaultHandler()
    # text person back
    text.message(response)
    return str(text)



# how to add a response
# resp = MessagingResponse()
# # Add a message
# resp.message(message here)


# Handler functions here. Do the updating and stuff
def yesHandler():
    """
    Updates DB for a Yes response for a user
    :return: string to text back to user
    """
    return 'You replied yes'  # temporary


def noHandler():
    """
    Updates DB for a No response, and does whatever else it needs to
    :return: string to text back to user
    """
    return 'You replied no'  # temporary


def defaultHandler():
    """
    Default handler if text is neither Yes or No. Probable sends the person back
    their chore for the week
    :return:
    """
    return 'Your chore for this week is _____'  # temporary
