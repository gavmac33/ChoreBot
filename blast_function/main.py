from twilio.rest import Client
import firebase_admin
from firebase_admin import firestore
from google.cloud import exceptions as gcloud_exceptions
import os


fire_app = firebase_admin.initialize_app()
DATABASE = firestore.client()

def env_vars(var):
    return os.environ.get(var, 'Specified environment variable is not set.')

# Define global constants using environment variables
_CHORE_WHEEL_PATH = env_vars("CHORE_WHEEL_DB_PATH")
ACCOUNT_SID = env_vars("ACCOUNT_SID")
AUTH_TOKEN = env_vars("AUTH_TOKEN")
SMS_CLIENT = Client(ACCOUNT_SID, AUTH_TOKEN)


def blast_function(request):
    request_json = request.get_json(silent=True)

    if request_json:
        group_name = request_json["GROUP_NAME"]
    else:
        raise Exception("No group name was given")

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




