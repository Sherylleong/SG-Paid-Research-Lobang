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
client = TelegramClient(StringSession(session_string), api_id, api_hash)


client.start()
print(client.session.save())
print("Client Created")
# Ensure you're authorized
if not client.is_user_authorized():
    client.send_code_request(phone)
    try:
        client.sign_in(phone, input('Enter the code: '))
    except SessionPasswordNeededError:
        client.sign_in(password=input('Password: '))



accepted_words = ['paynow', 'paylah', 'sgd', 'fairprice',
                  'ntuc', 'grab', 'grabride', 'capitaland', 'dollar']  # words indicating money or vouchers
rejected_words = [
    'grabfood'
    ]  # not interested
other = ['pr', 'permanent', 'resident', 'residing', 'foreign', 'nationalities', 'everyone'] # open to others
citizen = ['singaporean', 'singaporeans', 'citizens', 'citizen'] # open to citizens
dollar = ['$', 'sgd']

def filterother(msg):
    msg_words = [word.lower() for word in msg.split()]
    for word in other: # open to prs
        if (word in msg_words):
            return True
    for word in citizen: # open to citizens only
        if (word in msg_words):
            return False
    return True # no mention, probably open to everyone

def filterdollar(msg):
    for word in dollar:
        if re.search(word, msg) != None:
            return True



def filter(msg):
    msg_words = [word.lower() for word in msg.split()]

    for word in rejected_words:  
        if (word in msg_words):
            return False
    if not filterother(msg):
        return False
    if filterdollar(msg.lower()):  # probably money
        return True
    for word in accepted_words:  # probably money or grocery vouchers
        if (word in msg_words):
            return True
    return False


@client.on(events.NewMessage(chats=['@paidstudiesNTU', '@SGResearchLobang']))
async def handler(event):
    processed_text = re.sub(r'[^\w\s]', '', event.raw_text).lower() # remove punctuation
    if filter(processed_text):  # check if the message passes filters
        await client.forward_messages('@sgpaidresearchlobang', event.message) # channel i set up to forward the messages
    else:
        await client.send_message(entity='@testestseask', message="test") # test channel
#-1038947175

client.run_until_disconnected()
