# -*- coding: UTF-8 -*-

import hexchat

from os import listdir
from datetime import datetime


# Pending: strip or not based on config


color = '\003'
reset = '\017'
colors = (19, 20, 22, 24, 25, 26, 27, 28, 29)

configdir = hexchat.get_info('configdir')

date_time_format = '%Y %b %d %H:%M:%S'
folder_date_time_format = '%Y-%m'


def colored_nicks_loaded():
    return bool(sum([addon.endswith('colored_nicks.py') for addon in
           listdir(configdir + '/addons/')]))


# Color nick like HexChat does
def colored_nick(nick, mode=''):
    nick = hexchat.strip(nick)

    total = sum([ord(letter) for letter in nick])
    total = total % len(colors)

    color_code = colors[total]

    nick = color + str(color_code) + mode + nick + reset

    return nick


# User fields extractor: nick!username@host
def user_fields_extractor(user):
    i = user.find('!')
    j = user.find('@')

    if (i == -1) and (j == -1):
        if ('*' not in user) and ('.' not in user):
            nick = colored_nick(user)
        else:
            nick = user
        username = ''
        host = ''
    else:
        nick = user[:i]
        if ('*' not in nick) and ('.' not in nick):
            nick = colored_nick(nick)
        username = user[i + 1:j]
        host = hexchat.strip(user[j + 1:])

    return nick, username, host


# Return my nick and host
def my_nick_host():
    my_nick = hexchat.get_info('nick')

    my_username = ''
    my_host = ''
    for user in hexchat.get_list('users'):
        if user.nick == my_nick:
            my_nick = colored_nick(my_nick)
            my_username_host = user.host

            i = my_username_host.find('@')
            my_username = my_username_host[:i]
            my_host = hexchat.strip(my_username_host[i + 1:])
            break

    return my_nick, my_username, my_host


# Text event information extractors
def message_word_extractor(word):
    nick = word[0]
    if len(word) == 3:
        mode = word[2]
    else:
        mode = ''
    msg = hexchat.strip(word[1])
    #msg = word[1]

    nick = colored_nick(nick, mode)

    return nick, msg


def channel_word_extractor(word):
    nick = word[0]
    objectives = word[1]

    if '.' not in nick:
        nick = colored_nick(nick)

    if '.' not in objectives:
        objectives = objectives.split(' ')
        objectives = [colored_nick(objective) for objective in objectives]
        objectives = ', '.join(objectives)

    return nick, objectives


def outer_word_extractor(word):
    nick = colored_nick(word[0])
    host = hexchat.strip(word[2])

    return nick, host


def inner_word_extractor(word):
    nick = colored_nick(word[0])
    info = hexchat.strip(word[1])

    return nick, info


# Server (current network connection) context
def server_context(connection_id):
    for chan in hexchat.get_list('channels'):
        if (chan.type == 1) & (chan.id == connection_id):
            return chan.context


# Channel (current network connection) context
def channel_context(connection_id, channel):
    for chan in hexchat.get_list('channels'):
        if (chan.id == connection_id) & (chan.channel.lower() == channel.lower()):
            return chan.context


# Channel option
def get_chanopt(context, connection_id, channel, option):
    for chan in context.get_list('channels'):
        if (chan.channel == channel) & (chan.id == connection_id):
            return bool(chan.flags & option)


def get_complete_chanopt(context, connection_id, channel, global_option, option_unset, option):
    if get_chanopt(context, connection_id, channel, option_unset):
        if bool(hexchat.get_prefs(global_option)):
            return True
        else:
            return False
    else:
        if get_chanopt(context, connection_id, channel, option):
            return True
        else:
            return False


def printout_nick_history(nick_history, ident_history, nick='', ident='', ip=''):
    if bool(nick) & bool(ident) & bool(ip):
        printout = f'*\t[{nick}!{ident}@{ip}] '
    else:
        printout = ''

    list_ident_history = sum(ident_history.values(), [])
    if (len(set(list_ident_history)) == 1) and \
       (len(nick_history) == len(list_ident_history)) and \
       (len(nick_history) > 1):
        nick_history[-1] = f'{nick_history[-1]} ! {list_ident_history[0]}'
    else:
        nick_history = [n if (hexchat.strip(n) in ident_history.keys()) and \
                             (len(ident_history[hexchat.strip(n)]) == 1) and \
                             (ident_history[hexchat.strip(n)][0] == '*') else
                        f'{n}!{ident_history[hexchat.strip(n)][0]}'
                        if (hexchat.strip(n) in ident_history.keys()) and \
                           (len(ident_history[hexchat.strip(n)]) == 1) else
                        f'{n}!{",".join([ident for ident in ident_history[hexchat.strip(n)] if ident != "*"])}'
                        if hexchat.strip(n) in ident_history.keys() else
                        n for n in nick_history]

    printout = printout + 'Nick(s): ' + ', '.join(nick_history)

    return printout


def logging(log, network, channel):
    date_time = datetime.now()
    folder_date_time = date_time.strftime(folder_date_time_format)
    log_date_time = date_time.strftime(date_time_format)
    logs_dir = configdir + '/logs/' + network + '/' + folder_date_time + '/' + channel + '.log'
    file = open(logs_dir, 'a')
    file.write(log_date_time + ' ' + log + '\n')
    file.close()

