from twilio.rest import Client
from google.cloud import bigquery
from collections import deque, defaultdict
import pandas
import os

class Group:
    def __init__(self):
        self.names = []
        self.numbers = []
        self.chores = deque()
        self.choreStatus = []

    def rotate_chores(self):
        self.chores.append(self.chores.popleft())


def rotate_chore_wheel(arg):
    account_sid = env_vars("ACCOUNT_SID")
    auth_token = env_vars("AUTH_TOKEN")
    client = Client(account_sid, auth_token)

    rows_df = read_chore_wheel()
    groups = convert_df_to_dictionary(rows_df)
    send_shaming_messages(groups, client)
    rotate_chores(groups)
    rebuild_bq_database(groups)
    text_new_chores(groups, client)


def read_chore_wheel():
    QUERY = "SELECT * FROM `chore-bot-257803.ChoreBot.choreWheel`"

    bq_client = bigquery.Client()
    query_job = bq_client.query(QUERY)  # API request
    rows_df = query_job.result().to_dataframe()  # Waits for query to finish

    return rows_df

def convert_df_to_dictionary(rows_df):
    groups = defaultdict(lambda: Group())

    for index, row in rows_df.iterrows():
        groupName = str(row["groupName"])
        group = groups[groupName]

        group.names.append(str(row["name"]))
        group.numbers.append(str(row["number"]))
        group.chores.append(str(row["chore"]))
        group.choreStatus.append(row["choreStatus"])

    return groups


def send_shaming_messages(groups, messaging_client):
    for groupName in groups:
        truants = []
        group = groups[groupName]

        for i in range(len(group.choreStatus)):
            if not group.choreStatus[i]:
                truants.append((group.names[i], group.chores[i]))

        if len(truants) > 0:
            msg = "ChoreBot: The following people have not completed their chores from last week, making me very angry:\n"
            for truant in truants:
                msg += "%s: %s\n" % (truant[0], truant[1])

            for number in group.numbers:
                messaging_client.messages.create(
                    to=str(number),
                    from_="+16155517341",
                    body=msg
                )


def rotate_chores(groups):
    for groupName in groups:
        groups[groupName].rotate_chores()


def rebuild_bq_database(groups):
    # Change database one group at a time
    for groupName in groups:
        names = groups[groupName].names
        numbers = groups[groupName].numbers
        chores = groups[groupName].chores

        bq_client = bigquery.Client()

        for name in names:
            QUERY = "DELETE FROM `chore-bot-257803.ChoreBot.choreWheel` WHERE name = '" + name + "';"

            query_job = bq_client.query(QUERY)  # API request
            query_job.result()  # Waits for query to finish

        for i in range(len(names)):
            QUERY = "INSERT INTO `chore-bot-257803.ChoreBot.choreWheel` (name, number, chore, choreStatus, groupName) SELECT '%s','%s','%s', FALSE, '%s';"\
                    % (names[i], numbers[i], chores[i], groupName)

            query_job = bq_client.query(QUERY)  # API request
            query_job.result()  # Waits for query to finish


def text_new_chores(groups, messaging_client):
    for group in groups:
        currentGroup = groups[group]
        for i in range(len(currentGroup.names)):
            msg = "ChoreBot: %s, your chore for the new week is: %s" % (currentGroup.names[i], currentGroup.chores[i])

            messaging_client.messages.create(
                to=str(currentGroup.numbers[i]),
                from_="+16155517341",
                body=msg
            )


def env_vars(var):
    return os.environ.get(var, 'Specified environment variable is not set.')

