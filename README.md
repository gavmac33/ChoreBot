# ChoreBot

### Project Overview:
A bot to send out automated chores reminders every week. The bot is a twist on the classic chores wheel, automatically rotating chores and sending reminders to hold roommates accountable.

### Project Outline:
ChoreBot uses Google Cloud Platform to remember whose chore is whose, and to send out reminders. ChoreBot stores data about suite member names and phone numbers, suite chores, and who has completed their weekly chores in Google Cloud BigQuery.
ChoreBot schedules reminders and chore rotations using Google Cloud Scheduler. ChoreBot uses Google Cloud Functions to execute Python scripts that query data, send SMS, and respond to SMS.
Finally, ChoreBot uses Twilio to handle all incoming and outgoing SMS.

### Code Overview:
The scripts in this repo are the Google Cloud Functions that run ChatBot. They are called either by a scheduled event (Google Cloud Scheduler), or by the Twilio API when ChatBot receives a text.


#### blast_function:
Sends a quick chores blast, kindly reminding suite members of their chores duties.

#### harasser:
Sends a message to everyone who has not marked their chores as COMPLETE yet, asking them whether they have completed their chores yet. Their response is handled by `respond_sms`. Users who have completed their chores are not harassed.

#### reset_completed_chores:
Resets chore flags to "incomplete".

#### respond_sms:
Responds to all user messages. User may choose one of several options: <br />
`Option`: view all options <br />
`Micromanage`: view everyone's chores and whether they have been completed <br />
`Status`: view your own chore, and whether it has been marked complete <br />
respond_sms also handles user input about whether they have completed their chore (in response to `harasser`'s questioning)
