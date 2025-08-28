# -*- coding: UTF-8 -*-

__module_name__        = 'Find nicks and channels'
__module_version__     = '1.0'
__module_description__ = 'Find nicks with the same IP or ident, ' \
                         'visited channels, and first and last seen datetime.'


import hexchat

import sys
configdir = hexchat.get_info('configdir')
sys.path.insert(0, configdir)
from hexchat_utils import colored_nick, server_context, colored_nicks_loaded, printout_nick_history
from utils import find_nicks, printout_channel_history, \
                  printout_first_seen, printout_last_seen, printout_first_and_last_seen

from threading import Thread
from os.path import expanduser
from time import sleep


logs_directory = configdir + '/logs/'
additional_logs_directory = expanduser('~/Documents/IRC/logger/logs/')


is_colored_nicks_loaded = colored_nicks_loaded()
searching = False
search_queue = []


def search_thread():
    global search_queue, searching

    while True:
        sleep(2)
        if bool(search_queue) & (not searching):
            searching = True

            for nick, ident, ip, host, logs_dir, months, connection_id in search_queue:
                if ident == '*':
                    ident_search = ''
                else:
                    ident_search = ident
                if ip == '*':
                    ip_search = ''
                else:
                    ip_search = ip
                channel_history, nick_history, ident_history, first_seen, last_seen = \
                find_nicks(nick, ident_search, ip_search, host, logs_dir, months)

                printout_queue = []
                if nick_history:
                    if is_colored_nicks_loaded:
                        if nick != '*':
                            col_nick = colored_nick(nick)
                        else:
                            col_nick = nick
                        nick_history = [colored_nick(n) for n in nick_history]
                    printout = printout_nick_history(nick_history, ident_history, col_nick, ident, ip)
                    printout_queue.append(printout)
                if channel_history:
                    printout = printout_channel_history(channel_history, col_nick)
                    printout_queue.append(printout)
                if first_seen:
                    if first_seen == last_seen:
                        printout = printout_first_and_last_seen(first_seen, col_nick)
                        printout_queue.append(printout)
                    else:
                        printout = printout_first_seen(first_seen, col_nick)
                        printout_queue.append(printout)
                        printout = printout_last_seen(last_seen, col_nick)
                        printout_queue.append(printout)
                else:
                    if is_colored_nicks_loaded:
                        if nick != '*':
                            col_nick = colored_nick(nick)
                        else:
                            col_nick = nick
                    printout = f'*\t[{col_nick}!{ident}@{ip}] Not seen'
                    printout_queue.append(printout)

                if is_colored_nicks_loaded:
                    context = server_context(connection_id)
                for printout in printout_queue:
                    if is_colored_nicks_loaded:
                        context.prnt(printout)
                    else:
                        hexchat.prnt(printout)

                search_queue.remove((nick, ident, ip, host, logs_dir, months, connection_id))

            searching = False


def whois_name_line(word, word_eol, userdata):
    # hexchat.prnt('Whois Name Line')
    # hexchat.prnt(', '.join(word))
    global search_queue
    nick = word[0]
    ident = word[1]
    ip = hexchat.strip(word[2])
    # real_name = hexchat.strip(word[3])
    host = hexchat.get_info('host')
    connection_id = hexchat.get_prefs('id')
    network = hexchat.get_info('network').lower()
    logs_dir = logs_directory + network + '/'

    search_id = (nick, ident, ip, host, logs_dir, 2, connection_id)
    if search_id not in search_queue:
        search_queue.append(search_id)

    if is_colored_nicks_loaded:
        return hexchat.EAT_HEXCHAT
    else:
        return hexchat.EAT_NONE


def search(word, word_eol, userdata):
    global search_queue
    if len(word) == 3:
        try:
            months = int(word[2])
        except ValueError:
            return hexchat.EAT_ALL
    else:
        months = 1

    if (len(word) == 2) or (len(word) == 3):
        user = word[1]
        i = user.find('!')
        j = user.find('@')
        if (i != -1) and (j != -1):
            nick = user[:i]
            ident = user[i + 1:j]
            ip = user[j + 1:]

            host = hexchat.get_info('host')
            connection_id = hexchat.get_prefs('id')
            logs_dir = additional_logs_directory + host + '/'

            search_id = (nick, ident, ip, host, logs_dir, months, connection_id)
            if search_id not in search_queue:
                search_queue.append(search_id)

    return hexchat.EAT_ALL


hexchat.hook_print('Whois Name Line', whois_name_line)

hexchat.hook_command('search', search)


Thread(target=search_thread).start()

print(__module_name__, 'loaded')

