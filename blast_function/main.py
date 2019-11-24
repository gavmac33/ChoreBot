from twilio.rest import Client
import firebase_admin
from firebase_admin import firestore
import os
import base64

fire_app = firebase_admin.initialize_app()
DATABASE = firestore.client()


def env_vars(var):
    return os.environ.get(var, 'Specified environment variable is not set.')


# Define global constants using environment variables
_CHORE_WHEEL_PATH = env_vars("CHORE_WHEEL_DB_PATH")
ACCOUNT_SID = env_vars("ACCOUNT_SID")
AUTH_TOKEN = env_vars("AUTH_TOKEN")
SMS_CLIENT = Client(ACCOUNT_SID, AUTH_TOKEN)


def blast_function(event, context):
    group_name = base64.b64decode(event['data']).decode('utf-8')

    member_docs = DATABASE.collection(_CHORE_WHEEL_PATH)\
        .where("Suite", "==", group_name)\
        .get()
    members = [member.to_dict() for member in member_docs]


    for member in members:
        msg = "ChoreBot:  REMINDER- %s, your chore this week is %s" % (member["Name"], member["Chore"])

        SMS_CLIENT.messages.create(
            to=member["Number"],
            from_="+16155517341",
            body=msg
        )
