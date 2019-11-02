import os
from twilio.rest import Client

account_sid = "ACa0d2e2a71c0083c170cda34c30576f01"
auth_token = "5b340f0856008eebda79cd94c7e983a0"

client = Client(account_sid, auth_token)
client.messages.create(
    to="+19148069621",
    from_="16155517341",
    body="Chore bot automated text"
)

client.messages.create(
    to="+15037999603",
    from_="16155517341",
    body="Chore bot automated text"
)