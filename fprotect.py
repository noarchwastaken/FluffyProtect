#!/usr/bin/python3

"""
FluffyProtect - Telegram group anti-spam for humans.

This program is released under the public domain with WTFPL.
You just DO WHAT THE FUCK YOU WANT TO.
"""

from flask import Flask, redirect, request
from requests import get

# Your Telegram bot API key,
# this is also the URL FluffyProtect listens to Telegram's webhook
API_KEY = ''

app = Flask(__name__)
invite_links = {}


@app.route('/' + API_KEY, methods=['POST'])
def listen_for_updates():
    update = request.get_json()

    if 'new_chat_members' in update['message']:
        # get the chat from Telegram's request
        chat_id = update['message']['chat']['id']

        global invite_links
        invite_links[chat_id] = get_invite_link(API_KEY, chat_id)

    return('ok')


@app.route('/<chat_id>')
def client_request(chat_id):
    # Flask passes chat_id as a string
    chat_id = int(chat_id)

    # If no invite link for chat_id has been generated before, generate one now
    global invite_links
    try:
        invite_links[chat_id]
    except KeyError:
        invite_links[chat_id] = get_invite_link(API_KEY, chat_id)

    return(redirect(invite_links[chat_id], code=302))


def get_invite_link(api_key, chat_id):
    """
    Get invite link for chat_id.

    api_key (str): Your Telegram bot API key
    chat_id (int): Target chat ID
    """

    api_link = ('https://api.telegram.org/bot{}/exportChatInviteLink'
                .format(api_key))
    api_request = get(api_link,
                      params={'chat_id': str(chat_id)})

    api_response = api_request.json()

    # Return and error handling
    if api_response['ok']:
        new_invite_link = api_response['result']
    elif (api_response['error_code']):
        # Raise Exception with error given by Telegram
        raise Exception(api_response['description'])
    else:
        raise Exception('Unexpected error')

    return(new_invite_link)


# It also runs standalone
if (__name__) == '__main__':
    app.run()
