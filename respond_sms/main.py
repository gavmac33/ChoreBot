from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse

app = Flask(__name__)

@app.route("/sms", methods=['GET', 'POST'])
def replyPy(arg):

    # Start our response
    resp = MessagingResponse()

    # Add a message
    resp.message("Generic response to incoming text")

    return str(resp)
