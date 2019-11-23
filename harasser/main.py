from twilio.rest import Client
import firebase_admin
from firebase_admin import firestore
import os

fire_app = firebase_admin.initialize_app()
db = firestore.client()

def env_vars(var):
    return os.environ.get(var, 'Specified environment variable is not set.')

# Define global constants using environment variables
_CHORE_WHEEL_PATH = env_vars("CHORE_WHEEL_DB_PATH")
ACCOUNT_SID = env_vars("ACCOUNT_SID")
AUTH_TOKEN = env_vars("AUTH_TOKEN")
SMS_CLIENT = Client(ACCOUNT_SID, AUTH_TOKEN)


def harasser(event, context):
    argsDict = event["attributes"]

    try:
        group_name = argsDict["GROUP_NAME"]
    except:
        raise Exception("No group name was provided (add GROUP_NAME to attributes)")

    member_infos = db.collection(_CHORE_WHEEL_PATH) \
        .where("Suite", "==", group_name) \
        .get()

    for member_doc in member_infos:
        member = member_doc.to_dict()
        if not member["choreStatus"]:
            msg = "ChoreBot: %s, have you completed %s yet? (y/n)" % (member["Name"], member["Chore"])

            SMS_CLIENT.messages.create(
                to=member["Number"],
                from_="+16155517341",
                body=msg
            )

