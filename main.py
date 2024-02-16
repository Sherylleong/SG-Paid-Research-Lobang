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

from dotenv import load_dotenv #comment when deploying with heroku
load_dotenv() #comment when deploying with heroku

# retrieve environment variables from heroku getenv
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

accepted_words = ['paynow', 'paylah', 'fairprice', 'sgd',
                  'ntuc', 'grab', 'grabride', 'capitaland', 'dollar', 'dollars']  # words indicating money or vouchers
rejected_words = [
    'grabfood'
    ]  # not interested
other = ['pr', 'permanent', 'resident', 'residing', 'foreign', 'nationalities', 'everyone'] # open to others
citizen = ['singaporean', 'singaporeans', 'citizens', 'citizen'] # open to citizens

def filterother(msg):
    pro_msg = re.sub("\W", " ", msg).lower()
    msg_words = [word.lower() for word in pro_msg.split()]
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
    pro_msg = re.sub("\W", " ", msg).lower()
    for word in rejected_words:  
        if re.search(word, pro_msg):
            return False
    for word in accepted_words: # probably money or grocery vouchers
        if re.search(word, pro_msg):
            return True
    return 

def filter(msg):
    msg = msg.replace('\n', ' ').replace('\r', '')
    requirement_text = re.search('Requirements:(.*)Reward:', msg)
    if requirement_text is not None:
        requirement_text = requirement_text.group(1)
    else: 
        requirement_text = msg

    reward_text = re.search(r'Reward:(.*?)Participate:', msg)
    if reward_text is not None:
        reward_text = reward_text.group(1)
    else: 
        reward_text = msg
    # duration_text = msg.split("Duration:")[1].split("Requirements:")[0]

    if not filterother(requirement_text):
        return False
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
@client.on(events.NewMessage(chats=['@testestseask']))
async def tester(event):
        await client.send_message(entity='@testestseask', message='up') # test bot is up using test channel
#-1038947175
client.run_until_disconnected()
