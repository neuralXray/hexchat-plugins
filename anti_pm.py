# -*- coding: UTF-8 -*-

__module_name__        = 'Anti private messages'
__module_version__     = '1.0'
__module_description__ = 'Ignore private messages from a nick after he sends you one.'


import hexchat

import sys
configdir = hexchat.get_info('configdir')
sys.path.insert(0, configdir)
from hexchat_utils import colored_nicks_loaded


file = open(configdir + '/addons/anti_pm.conf')
lines = file.readlines()
file.close()

text = lines[0][:-1]
textex = lines[1][:-1]

is_colored_nicks_loaded = colored_nicks_loaded()
exceptions = lines[2][:-1]
if exceptions:
    exceptions = [exception.lower() for exception in exceptions.split(',')]
else:
    exceptions = []
ignores = []


def private_message(word, word_eol, userdata):
    # hexchat.prnt('Private Message')
    # hexchat.prnt(', '.join(word))
    global ignores
    nick = word[0]
    nick_lower = nick.lower()

    if nick_lower not in exceptions:
        ignores.append(nick_lower)
        hexchat.command('ignore ' + nick + '!*@* PRIV NOSAVE')
        hexchat.command('msg ' + nick + ' ' + text)

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


def antipmex(word, word_eol, userdata):
    global exceptions, ignores
    nick = word[1]

    if nick.lower() not in exceptions:
        exceptions.append(nick.lower())

    if nick.lower() in ignores:
        ignores.remove(nick.lower())
        hexchat.command('unignore ' + nick + '!*@*')
        hexchat.command('msg ' + nick + ' ' + textex)

    return hexchat.EAT_ALL


def antipmexrm(word, word_eol, userdata):
    global exceptions
    nick = word[1].lower()

    if nick in exceptions:
        exceptions.remove(nick)

    return hexchat.EAT_ALL


hexchat.hook_print('Private Message to Dialog', private_message)
hexchat.hook_print('Private Message', private_message)
hexchat.hook_print('Private Action to Dialog', private_message)
hexchat.hook_print('Private Action', private_message)

hexchat.hook_print('Your Message', your_message)
hexchat.hook_print('Message Send', message_send)

hexchat.hook_command('antipmex', antipmex)
hexchat.hook_command('antipmexrm', antipmexrm)


print(__module_name__, 'loaded')

