from twilio.rest import Client
import firebase_admin
from firebase_admin import firestore
import base64
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


def rotate_chore_wheel(event, context):
    group_name = base64.b64decode(event['data']).decode('utf-8')

    member_docs = DATABASE.collection(_CHORE_WHEEL_PATH) \
        .where("Suite", "==", group_name) \
        .get()
    members = [member.to_dict() for member in member_docs]

    # Send messages and update chore wheel
    send_shaming_messages(members)
    rotate_chores_update_db(members)
    text_new_chores(members)


def send_shaming_messages(members):
    truants = []
    for member in members:
        if not member["choreStatus"]:
            truants.append(member)

    if len(truants) > 0:
        msg = "ChoreBot: The following people have not completed their chores from last week, making me very angry:\n"
        for truant in truants:
            msg += "%s: %s\n" % (truant["Name"], truant["Chore"])

        for member in members:
            SMS_CLIENT.messages.create(
                to=member["Number"],
                from_="+16155517341",
                body=msg
            )


def rotate_chores_update_db(members):
    # Rotate chore wheel
    sortingKey = lambda p: p["groupID"]
    members.sort(key=sortingKey)

    # Rotate chores by shifting all chores down 1
    previousChore = members[-1]["Chore"]
    for i, member in enumerate(members):
        members[i]["Chore"], previousChore = previousChore, member["Chore"]

    # Update database
    for member in members:
        DATABASE.collection(_CHORE_WHEEL_PATH)\
            .document(member["Number"])\
            .update({"choreStatus": False, "Chore": member["Chore"]})


def text_new_chores(members):
    for member in members:
        msg = "ChoreBot: %s, your chore for the new week is: %s"\
              % (member["Name"], member["Chore"])

        SMS_CLIENT.messages.create(
            to=member["Number"],
            from_="+16155517341",
            body=msg
        )


