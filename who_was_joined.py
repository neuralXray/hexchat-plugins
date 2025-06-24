# -*- coding: UTF-8 -*-

__module_name__        = 'WHO was JOINed'
__module_version__     = '1.0'
__module_description__ = 'Log who were joined'


import hexchat

from threading import Thread
from time import sleep

import sys
sys.path.insert(0, hexchat.get_info('configdir'))
from hexchat_utils import colored_nicks_loaded, channel_context, logging


is_colored_nicks_loaded = colored_nicks_loaded()


def you_join_thread(connection_id, chat, channel):
    sleep(10)
    my_nick = hexchat.get_info('nick')
    context = channel_context(connection_id, channel)
    if context:
        for user in context.get_list('users'):
            nick = user.nick
            host = user.host
            if nick != my_nick:
                if host:
                    host = hexchat.strip(host)
                else:
                    host = '*@*'
                printout = '*\t' + nick + '!' + host + ' was joined'
                logging(printout, chat, channel)


def you_join(word, word_eol, userdata):
    # /J #channel
    # hexchat.prnt('You Join')
    # hexchat.prnt(', '.join(word))
    chat = hexchat.get_info('network').lower()
    connection_id = hexchat.get_prefs('id')
    channel = word[1].lower()
    Thread(target=you_join_thread, args=(connection_id, chat, channel,)).start()

    if is_colored_nicks_loaded:
        return hexchat.EAT_HEXCHAT
    else:
        return hexchat.EAT_NONE


hexchat.hook_print('You Join', you_join)


print(__module_name__, 'loaded')

