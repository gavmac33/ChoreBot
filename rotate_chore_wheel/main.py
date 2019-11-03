from twilio.rest import Client
from google.cloud import bigquery
import pandas

def rotate_chore_wheel(arg):
    rows_df = read_chore_wheel()
    names, numbers, chores = calculate_rotation(rows_df)
    df = remake_bq(names, numbers, chores)

    account_sid = "ACa0d2e2a71c0083c170cda34c30576f01"
    auth_token = "5b340f0856008eebda79cd94c7e983a0"
    client = Client(account_sid, auth_token)

    for index, row in rows_df.iterrows():
        msg = str(row["name"]) + ", your chore for the new week is " + str(row["chore"])

        client.messages.create(
            to=str(row["number"]),
            from_="16155517341",
            body=msg
        )


def read_chore_wheel():
    QUERY = "SELECT * FROM `chore-bot-257803.ChoreBot.choreWheel`"

    bq_client = bigquery.Client()
    query_job = bq_client.query(QUERY)  # API request
    rows_df = query_job.result().to_dataframe()  # Waits for query to finish

    return rows_df


def calculate_rotation(rows_df):
    from collections import deque
    names = []
    numbers = []
    chores = deque()

    for index, row in rows_df.iterrows():
        names.append(str(row["name"]))
        numbers.append(str(row["number"]))
        chores.append(str(row["chore"]))

    # Rotate chores
    chores.append(chores.popleft())

    return names, numbers, chores


def remake_bq(names, numbers, chores):
    for name in names:
        QUERY = "DELETE FROM `chore-bot-257803.ChoreBot.choreWheel` WHERE name = '" + name + "';"

        bq_client = bigquery.Client()
        query_job = bq_client.query(QUERY)  # API request
        query_job.result()  # Waits for query to finish

    for i in range(len(names)):
        QUERY = "INSERT INTO `chore-bot-257803.ChoreBot.choreWheel` (name, number, chore) SELECT '" + names[i] + "','" + numbers[i] + "','" + chores[i] + "';"

        bq_client = bigquery.Client()
        query_job = bq_client.query(QUERY)  # API request
        query_job.result()  # Waits for query to finish

    # Get updated chores wheel as dataframe
    QUERY = "SELECT * FROM `chore-bot-257803.ChoreBot.choreWheel`"

    bq_client = bigquery.Client()
    query_job = bq_client.query(QUERY)  # API request
    rows_df = query_job.result().to_dataframe()  # Waits for query to finish

    return rows_df