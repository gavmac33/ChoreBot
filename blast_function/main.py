from twilio.rest import Client
from google.cloud import bigquery
import pandas

def blast_function(arg):
    rows_df = read_chore_wheel()

    account_sid = "ACa0d2e2a71c0083c170cda34c30576f01"
    auth_token = "5b340f0856008eebda79cd94c7e983a0"
    client = Client(account_sid, auth_token)

    for index, row in rows_df.iterrows():
        msg = "ChoreBot REMINDER:" + str(row["name"]) + ", your chore this week is " + str(row["chore"])

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

