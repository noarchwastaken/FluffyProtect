#!/usr/bin/python3

"""
FluffyProtect - Telegram group anti-spam for humans.

This program is released under the public domain with WTFPL.
You just DO WHAT THE FUCK YOU WANT TO.
"""

import os

from flask import Flask, redirect, request
from requests import get

# The API key is now set using an environment variable
try:
    API_KEY = os.environ['FPROTECT_API_KEY']
except KeyError:
    print('FPROTECT_API_KEY not set')
    exit(1)

# Change this if you use your own Telegram bot API server
API_LINK = 'https://api.telegram.org/bot{}/'.format(API_KEY)

app = Flask(__name__)

@app.route('/' + API_KEY, methods=['POST'])
def listen_for_updates():
    update = request.get_json()

    if 'new_chat_members' in update['message']:
        # get the chat from Telegram's request
        chat_id = update['message']['chat']['id']

        update_link(chat_id)

    return('ok')


@app.route('/<chat_id>')
def client_request(chat_id):
    # Flask passes chat_id as a string
    chat_id = int(chat_id)

    return(redirect(get_link(chat_id), code=302))


def query_api(method, chat_id):
    api_request = get(API_LINK + method,
                      {'chat_id': str(chat_id)})

    api_response = api_request.json()

    if api_response['ok']:
        return api_response
    elif (api_response['error_code']):
        # Raise Exception with error given by Telegram
        raise Exception(api_response['description'])
    else:
        raise Exception('Unexpected error')    


def get_link(chat_id):
    api_response = query_api('getChat', chat_id)

    return api_response['result']['invite_link']


def update_link(chat_id):
    query_api('exportChatInviteLink', chat_id)


# It also runs standalone
if (__name__) == '__main__':
    app.run()
