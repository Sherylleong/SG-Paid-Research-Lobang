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
import json

# enter own details in json file (api id and hash can be obtained from Telegram developer tools website)
with open("info.json", "r") as f:
    json_data = json.load(f)

api_id = json_data['api_id']
api_hash = json_data['api_hash']
phone = json_data['phone']
username = json_data['username']

# Create the client and connect
#client = TelegramClient(None, username, api_id, api_hash)
client = TelegramClient('anon', api_id, api_hash)
client.start()
print("Client Created")

# Ensure you're authorized
if not client.is_user_authorized():
    client.send_code_request(phone)
    try:
        client.sign_in(phone, input('Enter the code: '))
    except SessionPasswordNeededError:
        client.sign_in(password=input('Password: '))

accepted_words = ['paynow', 'paylah', 'sgd', 'fairprice',
                  'ntuc']  # words indicating money or grocery vouchers
rejected_words = [
    'chance', 'lucky', 'grab', 'grabfood', 'grabride', 'starbucks', 'nus'
    ]  # words indicating chance, vouchers or exclusions
pr = ['pr', 'permanent', 'resident'] # open to PRs
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
#-1038947175

client.run_until_disconnected()
