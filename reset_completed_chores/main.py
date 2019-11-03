from google.cloud import bigquery

def reset_completed_chores(arg):
    run_bq_command("UPDATE `chore-bot-257803.ChoreBot.choreWheel` SET choreStatus = FALSE WHERE name IS NOT NULL;")

def run_bq_command(QUERY):
    bq_client = bigquery.Client()
    query_job = bq_client.query(QUERY)  # API request
    query_job.result()  # Waits for query to finish
