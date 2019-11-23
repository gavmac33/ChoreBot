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


def new_users_welcome(request):
    request_json = request.get_json(silent=True)
    if request_json:
        group_name = request_json["GROUP_NAME"]
    else:
        raise Exception("No group name was given")

    member_docs = DATABASE.collection(_CHORE_WHEEL_PATH) \
        .where("Suite", "==", group_name) \
        .get()
    members = [member.to_dict() for member in member_docs]

    msg = ", welcome to ChoreBot! I will be your new Chore Master, in charge of holding you and your suitemates accountable for your shared living space. I will send out periodic reminders of your chores, and keep track of who's bee nslacking!" \
                       "\nTo learn about some of the different things I can do, respond \"O\" for options to this message"

    for member in members:
        SMS_CLIENT.messages.create(
            to=member["Number"],
            from_="+16155517341",
            body=member["Name"] + msg
        )

    return group_name + " found, messages sent"
