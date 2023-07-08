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
import string

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
                  'ntuc', 'grab', 'grabride', 'capitaland', 'dollar', 'sgd']  # words indicating money or vouchers
rejected_words = [
    'grabfood'
    ]  # not interested
other = ['pr', 'permanent', 'resident', 'residing', 'foreign', 'nationalities', 'everyone'] # open to others
citizen = ['singaporean', 'singaporeans', 'citizens', 'citizen'] # open to citizens

def filterother(msg):
    msg_words = [word.lower() for word in msg.split()]
    for word in other: # open to prs
        if (word in msg_words):
            return True
    for word in citizen: # open to citizens only
        if (word in msg_words):
            return False
    return True # no mention, probably open to everyone

def filtermoney(msg):
    if re.search("\$", msg):
        return True
    return False

def filterkeywords(msg):
    msg_words = [word.lower() for word in msg.split()]
    for word in rejected_words:  
        if (word in msg_words):
            return False
    for word in accepted_words: # probably money or grocery vouchers
        if (word in msg_words):
            return True
    return False

def filter(msg):
    pro_msg = msg.translate(str.maketrans('', '', string.punctuation)).lower()
    requirement_text = msg.split("Requirements:")[1].split("Reward:")[0]
    reward_text = msg.split("Reward:")[1].split("Participate:")[0]
    duration_text = msg.split("Duration:")[1].split("Requirements:")[0]

    msg_words = pro_msg.split()


    if not filterother(requirement_text):
        return False
    if filterkeywords:
        return True
    if filtermoney(reward_text):  # probably money
        return True
    if filterkeywords(reward_text):
        return True
    return False
@client.on(events.NewMessage(chats=['@paidstudiesNTU', '@SGResearchLobang']))
async def handler(event):
    if filter(event.raw_text):  # check if the message passes filters
        await client.forward_messages('@sgpaidresearchlobang', event.message) # channel i set up to forward the messages
    else:
        await client.send_message(entity='@testestseask', message=event.message) # test channel
#-1038947175

client.run_until_disconnected()
