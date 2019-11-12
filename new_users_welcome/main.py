from twilio.rest import Client
from google.cloud import bigquery
import pandas
import os

_CHORE_WHEEL_PATH = "chore-bot-257803.ChoreBot.choreWheel"

def new_users_welcome(request):
    request_json = request.get_json(silent=True)

    if request_json:
        group_name = request_json["groupName"]
    else:
        raise Exception("No group name was given")


    QUERY = "SELECT * FROM `%s` WHERE groupName = '%s'" % (_CHORE_WHEEL_PATH, group_name)

    bq_client = bigquery.Client()
    query_job = bq_client.query(QUERY)  # API request
    rows_df = query_job.result().to_dataframe()  # Waits for query to finish

    account_sid = env_vars("ACCOUNT_SID")
    auth_token = env_vars("AUTH_TOKEN")
    messaging_client = Client(account_sid, auth_token)

    msg = group_name + ", welcome to ChoreBot! I will be your new Chore Master, in charge of holding you and your suitemates accountable for your shared living space. I will send out periodic reminders of your chores, and keep track of who's bee nslacking!" \
                       "\nTo learn about some of the different things I can do, respond \"O\" for options to this message"
    for index, row in rows_df.iterrows():
        messaging_client.messages.create(
            to=row["number"],
            from_="+16155517341",
            body=msg
        )


    return group_name + " found, messages sent"



def env_vars(var):
    return os.environ.get(var, 'Specified environment variable is not set.')