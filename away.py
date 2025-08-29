# -*- coding: UTF-8 -*-

__module_name__        = 'Away'
__module_version__     = '1.0'
__module_description__ = 'Notice nick mentions and private messages if marked as away.'


import hexchat

import sys
addonsdir = hexchat.get_info('configdir') + '/addons'
sys.path.insert(0, addonsdir + '/utils')
from hexchat_utils import colored_nicks_loaded

from re import search, IGNORECASE


file = open(addonsdir + '/away.conf')
lines = file.readlines()
file.close()

is_colored_nicks_loaded = colored_nicks_loaded()
exceptions = lines[0][:-1]
if exceptions:
    exceptions = [exception.lower() for exception in exceptions.split(',')]
else:
    exceptions = []

noticed_nicks = []


def away_hook(word, word_eol, userdata):
    global noticed_nicks
    nick = hexchat.strip(word[0])
    connection_id = hexchat.get_prefs('id')
    noticed_nick_id = (connection_id, nick)
    away = hexchat.get_info('away')

    if (away is not None) and (noticed_nick_id not in noticed_nicks) and \
       (nick.lower() not in exceptions):
        noticed_nicks.append(noticed_nick_id)
        hexchat.command(f"notice {nick} I'm away ({away})")

    if is_colored_nicks_loaded:
        return hexchat.EAT_HEXCHAT
    else:
        return hexchat.EAT_NONE


def message_send(word, word_eol, userdata):
    # hexchat.prnt('Message Send')
    # hexchat.prnt(', '.join(word))
    global exceptions
    nick = word[0].lower()

    if nick not in exceptions:
        exceptions.append(nick)

    if is_colored_nicks_loaded:
        return hexchat.EAT_HEXCHAT
    else:
        return hexchat.EAT_NONE


def your_message(word, word_eol, userdata):
    # hexchat.prnt('Your Message')
    # hexchat.prnt(', '.join(word))
    global exceptions
    context = hexchat.get_info('channel').lower()

    if (context[0] != '#') and (context not in exceptions):
        exceptions.append(context)

    if is_colored_nicks_loaded:
        return hexchat.EAT_HEXCHAT
    else:
        return hexchat.EAT_NONE


def back_hook(word, word_eol, userdata):
    global noticed_nicks

    noticed_nicks = []

    return hexchat.EAT_NONE


def away_back_hook(word, word_eol, userdata):
    if (hexchat.get_info('away') is not None):
        hexchat.command('back')

        return hexchat.EAT_ALL
    else:
        return hexchat.EAT_NONE


hexchat.hook_print('Channel Msg Hilight', away_hook)
hexchat.hook_print('Channel Action Hilight', away_hook)

hexchat.hook_print('Private Message to Dialog', away_hook)
hexchat.hook_print('Private Message', away_hook)
hexchat.hook_print('Private Action to Dialog', away_hook)
hexchat.hook_print('Private Action', away_hook)
hexchat.hook_print('Notice', away_hook)

hexchat.hook_print('Your Message', your_message)
hexchat.hook_print('Message Send', message_send)

hexchat.hook_command('back', back_hook)
hexchat.hook_command('away', away_back_hook)


print(__module_name__, 'loaded')

