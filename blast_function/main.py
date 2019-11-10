from twilio.rest import Client
from google.cloud import bigquery
import pandas
import os

def blast_function(arg):
    rows_df = read_chore_wheel()

    account_sid = env_vars("ACCOUNT_SID")
    auth_token = env_vars("AUTH_TOKEN")
    client = Client(account_sid, auth_token)

    for index, row in rows_df.iterrows():
        msg = "ChoreBot:  REMINDER- %s, your chore this week is %s" % (str(row["name"]), str(row["chore"]))

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


def env_vars(var):
    return os.environ.get(var, 'Specified environment variable is not set.')

