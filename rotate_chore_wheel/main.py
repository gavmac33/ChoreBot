from twilio.rest import Client
from google.cloud import bigquery
from collections import deque, defaultdict
import pandas
import os

# Define global constants
_CHORE_WHEEL_PATH = "chore-bot-257803.ChoreBot.choreWheel"

class Person:
    def __init__(self, name, number, chore, choreStatus, groupID):
        self.name = name
        self.number = number
        self.chore = chore
        self.choreStatus = choreStatus
        self.groupID = groupID

class Group:
    def __init__(self):
        self.people = []

    def add(self, person):
        self.people.append(person)

    def rotate_chores(self):
        # Sort the people based on groupID
        sortingKey = lambda p: p.groupID
        self.people.sort(key=sortingKey)

        # Rotate chores by shifting all chores down 1
        previousChore = self.people[-1].chore
        for i in range(len(self.people)):
            newPreviousChore = self.people[i].chore
            self.people[i].chore = previousChore
            previousChore = newPreviousChore


def rotate_chore_wheel(arg):
    # Create messaging client for sending texts
    account_sid = env_vars("ACCOUNT_SID")
    auth_token = env_vars("AUTH_TOKEN")
    messaging_client = Client(account_sid, auth_token)

    # Read in data
    rows_df = read_chore_wheel()
    groups = convert_df_to_dictionary(rows_df)

    # Send messages and update chore wheel
    send_shaming_messages(groups, messaging_client)
    rotate_chores_update_db(groups)
    text_new_chores(groups, messaging_client)


def read_chore_wheel():
    QUERY = "SELECT * FROM `%s`" % (_CHORE_WHEEL_PATH)

    bq_client = bigquery.Client()
    query_job = bq_client.query(QUERY)  # API request
    rows_df = query_job.result().to_dataframe()  # Waits for query to finish

    return rows_df

def convert_df_to_dictionary(rows_df):
    groups = defaultdict(lambda: Group())

    for index, row in rows_df.iterrows():
        groupName = str(row["groupName"])
        group = groups[groupName]

        newPerson = Person(name=str(row["name"]), number=str(row["number"]),
                           chore=str(row["chore"]), choreStatus=row["choreStatus"], groupID=row["groupID"])
        group.add(newPerson)

    return groups


def send_shaming_messages(groups, messaging_client):
    for groupName in groups:
        currentGroup = groups[groupName]

        truants = []
        for person in currentGroup.people:
            if not person.choreStatus:
                truants.append(person)

        if len(truants) > 0:
            msg = "ChoreBot: The following people have not completed their chores from last week, making me very angry:\n"
            for truant in truants:
                msg += "%s: %s\n" % (truant.name, truant.chore)

            for person in currentGroup.people:
                messaging_client.messages.create(
                    to=str(person.number),
                    from_="+16155517341",
                    body=msg
                )


def rotate_chores_update_db(groups):
    bq_client = bigquery.Client()

    # Change database one group at a time
    for groupName in groups:
        currentGroup = groups[groupName]
        currentGroup.rotate_chores()

        for person in currentGroup.people:
            QUERY = "UPDATE `%s` SET choreStatus = FALSE, chore = '%s' WHERE name = '%s';"\
                    % (_CHORE_WHEEL_PATH, person.chore, person.name)

            query_job = bq_client.query(QUERY)  # API request
            query_job.result()  # Waits for query to finish


def text_new_chores(groups, messaging_client):
    for groupName in groups:
        for person in groups[groupName].people:
            msg = "ChoreBot: %s, your chore for the new week is: %s" % (person.name, person.chore)

            messaging_client.messages.create(
                to=str(person.number),
                from_="+16155517341",
                body=msg
            )


def env_vars(var):
    return os.environ.get(var, 'Specified environment variable is not set.')

