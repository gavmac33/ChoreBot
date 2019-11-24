import firebase_admin
from firebase_admin import firestore
import os
import datetime
import base64
from google.cloud import pubsub_v1

fire_app = firebase_admin.initialize_app()
DATABASE = firestore.client()
publisher = pubsub_v1.PublisherClient()


def env_vars(var):
    return os.environ.get(var, 'Specified environment variable is not set.')

# Define global constants using environment variables
ROTATE_SCHEDULE_PATH = env_vars("ROTATE_SCHEDULE_DB_PATH")
REMIND_SCHEDULE_PATH = env_vars("REMIND_SCHEDULE_DB_PATH")
HARASS_SCHEDULE_PATH = env_vars("HARASS_SCHEDULE_DB_PATH")
ROTATE_TOPIC = publisher.topic_path(env_vars("PROJECT_ID"), env_vars("ROTATE_FUNCTION_TOPIC"))
REMIND_TOPIC = publisher.topic_path(env_vars("PROJECT_ID"), env_vars("REMIND_FUNCTION_TOPIC"))
HARASS_TOPIC = publisher.topic_path(env_vars("PROJECT_ID"), env_vars("HARASSING_FUNCTION_TOPIC"))

def schedule(event, context):
    blast_num = base64.b64decode(event['data']).decode('utf-8')
    currentPeriod = getCurrentPeriod(blast_num)

    rotate(currentPeriod)
    remind(currentPeriod)
    harass(currentPeriod)

def getCurrentPeriod(blast_num):
    daysOfWeek = ("Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday")
    day = datetime.date.today().weekday()
    return daysOfWeek[day] + blast_num

def rotate(currentPeriod):
    member_docs = DATABASE.collection(ROTATE_SCHEDULE_PATH) \
        .where(currentPeriod, "==", True) \
        .get()
    members = [member.to_dict() for member in member_docs]

    for member in members:
        publisher.publish(ROTATE_TOPIC, member["Suite"].encode())

def remind(currentPeriod):
    member_docs = DATABASE.collection(REMIND_SCHEDULE_PATH) \
        .where(currentPeriod, "==", True) \
        .get()
    members = [member.to_dict() for member in member_docs]

    for member in members:
        publisher.publish(REMIND_TOPIC, member["Suite"].encode())

def harass(currentPeriod):
    member_docs = DATABASE.collection(HARASS_SCHEDULE_PATH) \
        .where(currentPeriod, "==", True) \
        .get()
    members = [member.to_dict() for member in member_docs]

    for member in members:
        publisher.publish(HARASS_TOPIC, member["Suite"].encode())