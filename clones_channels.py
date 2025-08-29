# -*- coding: UTF-8 -*-

__module_name__        = 'Find clones and channels'
__module_version__     = '1.0'
__module_description__ = 'Find users with the same IP and common channels after a WHOIS.'


import hexchat

import sys
sys.path.insert(0, hexchat.get_info('configdir') + '/addons/utils')
from hexchat_utils import colored_nick, server_context, colored_nicks_loaded


is_colored_nicks_loaded = colored_nicks_loaded()
printout_queue = []


def whois_name_line(word, word_eol, userdata):
    # hexchat.prnt('Whois Name Line')
    # hexchat.prnt(', '.join(word))
    nick = word[0]
    ident = word[1]
    ip = word[2]
    # real_name = hexchat.strip(word[3])
    chat = hexchat.get_info('host')
    connection_id = hexchat.get_prefs('id')

    channel_history = []
    clones_nicks = []
    clones = []
    if is_colored_nicks_loaded:
        col_nick = colored_nick(nick)
    else:
        col_nick = nick

    if ip.endswith('.79j.0Ar7OI.virtual') and (chat == 'irc.chathispano.com'):
        printout = '*\t[' + col_nick + '] Unable to find clone(s) (IRCCloud)'
    else:
        for chan in hexchat.get_list('channels'):
            if (chan.id == connection_id) and (chan.type == 2):
                user_list = chan.context.get_list('users')
                for user in user_list:
                    nick_check = user.nick
                    nick_host = user.host

                    if nick_check == nick:
                        channel = user.prefix + chan.channel
                        channel_history.append(channel)

                    if nick_host:
                        nick_ident = nick_host[:nick_host.find('@')]
                        nick_ip = nick_host[nick_host.find('@') + 1:]
                        if (nick_ip == ip) and (nick_check != nick) and (nick_check not in clones_nicks):
                            clones_nicks.append(nick_check)
                            if is_colored_nicks_loaded:
                                nick_check = colored_nick(nick_check)
                            clones.append(nick_check + '!' + nick_ident)
        printout = '*\t[' + col_nick + '] ' + str(len(clones)) + ' clone(s)'
        if clones:
            printout = printout + ': ' + ', '.join(clones)
    if is_colored_nicks_loaded:
        context = server_context(connection_id)
        context.prnt(printout)
    else:
        hexchat.prnt(printout)

    my_nick = hexchat.get_info('nick')
    if nick != my_nick:
        if channel_history:
            printout = 'Common channel(s): ' + ', '.join(channel_history)
        else:
            printout = 'No common channel(s)'
        printout = '*\t[' + col_nick + '] ' + printout
        if is_colored_nicks_loaded:
            context = server_context(connection_id)
            context.prnt(printout)
        else:
            hexchat.prnt(printout)

    if is_colored_nicks_loaded:
        return hexchat.EAT_HEXCHAT
    else:
        return hexchat.EAT_NONE


hexchat.hook_print('Whois Name Line', whois_name_line)

print(__module_name__, 'loaded')

