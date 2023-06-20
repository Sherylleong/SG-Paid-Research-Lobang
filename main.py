from telethon import TelegramClient, events
from telethon.errors import SessionPasswordNeededError

# to get members
from telethon.tl.functions.channels import GetParticipantsRequest
from telethon.tl.types import ChannelParticipantsSearch
from telethon.tl.types import (PeerChannel)

# to get messages
from telethon.tl.functions.messages import (GetHistoryRequest)
from telethon.tl.types import (PeerChannel)

from telethon import utils
from telethon.tl import functions, types

import re
import os

from telethon.sessions import StringSession



# retrieve environment variables from heroku
api_id = os.getenv('API_ID')
api_hash = os.getenv('API_HASH')
phone = os.getenv('PHONE')
username = os.getenv('USERNAME')
session_string = os.getenv('SESSION_STRING')


# Create the client and connect
#client = TelegramClient(None, username, api_id, api_hash)
client = TelegramClient(StringSession(session_string), api_id, api_hash)

client.start()
print("Client Created")

print(client.session.save())
# Ensure you're authorized
if not client.is_user_authorized():
    client.send_code_request(phone)
    try:
        client.sign_in(phone, input('Enter the code: '))
    except SessionPasswordNeededError:
        client.sign_in(password=input('Password: '))



accepted_words = ['paynow', 'paylah', 'sgd', 'fairprice',
                  'ntuc', 'grab', 'grabride']  # words indicating money or vouchers
rejected_words = [
    'grabfood', 'starbucks'
    ]  # not interested
pr = ['pr', 'permanent', 'resident', 'residing', 'foreign', 'nationalities'] # open to PRs
citizen = ['singaporean', 'singaporeans', 'citizens', 'citizen'] # open to citizens

def filterpr(msg):
    msg_words = [word.lower() for word in msg.split()]
    for word in pr: # open to prs
        if (word in msg_words):
            return True
    for word in citizen: # open to citizens only
        if (word in msg_words):
            return False
    return True # no mention, probably open to everyone

def filter(msg):
    dollarsign = re.search("\$", msg)  # if msg contains $

    msg_words = [word.lower() for word in msg.split()]

    for word in rejected_words:  # probably lucky draw or grab vouchers
        if (word in msg_words):
            return False
    if not filterpr(msg):
        return False
    if (dollarsign != None):  # probably money
        return True
    for word in accepted_words:  # probably money or grocery vouchers
        if (word in msg_words):
            return True
    return False


@client.on(events.NewMessage(chats=['@paidstudiesNTU', '@SGResearchLobang']))
async def handler(event):
    if filter(event.raw_text):  # check if the message passes filters
        await client.forward_messages('@ntuactualpaidstudies', event.message) # channel i set up to forward the messages
    else:
        await client.send_message(entity='@testestseask', message="test") # test channel
#-1038947175

client.run_until_disconnected()
