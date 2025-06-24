# -*- coding: UTF-8 -*-

__module_name__        = 'CHaN'
__module_version__     = '1.0'
__module_description__ = 'Automated & hidden operator actions'

# Pendiente: pillar exempts a akicks para eliminarlas automaticamente


import hexchat

import sys
configdir = hexchat.get_info('configdir')
sys.path.insert(0, configdir)
from hexchat_utils import colored_nicks_loaded, user_fields_extractor, message_word_extractor
from utils import user_regex

from re import search, IGNORECASE
from time import time, sleep
from threading import Thread


file = open(configdir + '/addons/chan.conf')
lines = file.readlines()
file.close()
channels = {}
for i in range(0, len(lines), 2):
    channels[tuple(lines[i][:-1].split(','))] = lines[i + 1].split(',')

my_idents = {}
my_ips = {}
akick = {}
bans = {}
clock = time()
op_returned = False
op_delay = 2

is_colored_nicks_loaded = colored_nicks_loaded()


def channel_deop_thread(context, channel, nick):
    global clock, op_returned
    my_nick = hexchat.get_info('nick')

    sleep(op_delay)
    if (time() - clock > op_delay) & (not op_returned):
        context.command(f'msg CHaN op {channel} {my_nick}')
        clock = time()
        op_returned = True
        context.command(f'mode -o {nick}')


def chan_command(word, word_eol, userdata):
    # /msg CHaN command channel target
    # hexchat.prnt('CHaN command')
    # hexchat.prnt(', '.join(word))
    channel = hexchat.get_info('channel').lower()
    command = word[0][:-1]
    target = word[1]

    hexchat.command(f'msg CHaN {command} {channel} {target}')

    return hexchat.EAT_ALL


def your_nick_changing(word, word_eol, userdata):
    # /NICK new_nick
    # hexchat.prnt('Your Nick Changing')
    # hexchat.prnt(', '.join(word))
    new_nick = word[1]
    chat = hexchat.get_info('host')
    key = (chat, new_nick.lower())

    if key in channels.keys():
        channel = hexchat.get_info('channel').lower()
        if channel in channels[key]:
            hexchat.command(f'msg CHaN op {channel} {new_nick}')

    if is_colored_nicks_loaded:
        return hexchat.EAT_HEXCHAT
    else:
        return hexchat.EAT_NONE


def ban_command(word, word_eol, userdata):
    # /BAN * regex
    # hexchat.prnt('BAN command')
    # hexchat.prnt(', '.join(word))
    global bans

    if len(word) > 2:
        if word[1] == '*':
            connection_id = hexchat.get_prefs('id')
            channel = hexchat.get_info('channel')
            key = (connection_id, channel)
            regex = word[2]

            if key in bans.keys():
                bans[key] = bans[key] + [regex]
            else:
                bans[key] = [regex]
            print(bans)

            return hexchat.EAT_ALL
    return hexchat.EAT_NONE


def unban_command(word, word_eol, userdata):
    # /BAN * regex
    # hexchat.prnt('BAN command')
    # hexchat.prnt(', '.join(word))
    global bans

    if len(word) > 2:
        if word[1] == '*':
            connection_id = hexchat.get_prefs('id')
            channel = hexchat.get_info('channel')
            key = (connection_id, channel)
            regex = word[2]

            if key in bans.keys():
                if regex in bans[key]:
                    if len(bans[key]) > 1:
                        bans[key].remove(regex)
                    else:
                        del bans[key]
                    print(bans)

            return hexchat.EAT_ALL
    return hexchat.EAT_NONE


def channel_message(word, word_eol, userdata):
    # hexchat.prnt('Your Message / Channel Message')
    # hexchat.prnt(', '.join(word))
    connection_id = hexchat.get_prefs('id')
    channel = hexchat.get_info('channel')
    key = (connection_id, channel)

    if key in bans.keys():
        message = word[1]
        for mask in bans[key]:
            if search(mask, message, flags=IGNORECASE):
                objective = hexchat.strip(word[0])
                hexchat.command(f'kb {objective}')

    if is_colored_nicks_loaded:
        return hexchat.EAT_HEXCHAT
    else:
        return hexchat.EAT_NONE


def exempt_command(word, word_eol, userdata):
    # /EXEMPT objective
    # hexchat.prnt('EXEMPT')
    # hexchat.prnt(', '.join(word))
    if len(word) > 1:
        target = word[1]
        hexchat.command(f'mode e {target}')
    else:
        hexchat.command('mode e')

    return hexchat.EAT_ALL


def unexempt_command(word, word_eol, userdata):
    # /UNEXEMPT objective
    # hexchat.prnt('EXEMPT')
    # hexchat.prnt(', '.join(word))
    target = word[1]

    hexchat.command(f'mode -e {target}')

    return hexchat.EAT_ALL


def exemptme_command(word, word_eol, userdata):
    # /EXEMPTME
    # hexchat.prnt('EXEMPTME')
    # hexchat.prnt(', '.join(word))
    my_nick = hexchat.get_info('nick')

    hexchat.command(f'mode e {my_nick}')

    return hexchat.EAT_ALL


def banned(word, word_eol, userdata):
    # hexchat.prnt('User Limit')
    # hexchat.prnt(', '.join(word))
    channel = word[0]
    chat = hexchat.get_info('host')
    my_nick = hexchat.get_info('nick')
    key = (chat, my_nick.lower())

    if key in channels.keys():
        if channel in channels[key]:
            hexchat.command(f'msg CHaN unban {channel}')

    if is_colored_nicks_loaded:
        return hexchat.EAT_HEXCHAT
    else:
        return hexchat.EAT_NONE


def channel_deop(word, word_eol, userdata):
    # /DEOP objective
    # hexchat.prnt('Channel DeOp')
    # hexchat.prnt(', '.join(word))
    global clock, op_returned
    chat = hexchat.get_info('host')
    my_nick = hexchat.get_info('nick')
    key = (chat, my_nick.lower())

    if key in channels.keys():
        channel = hexchat.get_info('channel').lower()
        if channel in channels[key]:
            nick = word[0]
            objectives = word[1].split(' ')
            for objective in objectives:
                if objective == my_nick:
                    if time() - clock > op_delay:
                        hexchat.command(f'msg CHaN op {channel} {my_nick}')
                        clock = time()
                        hexchat.command(f'mode -o {nick}')
                    else:
                        op_returned = False
                        Thread(target=channel_deop_thread, args=(hexchat.get_context(), channel, nick,)).start()
                    break

    if is_colored_nicks_loaded:
        return hexchat.EAT_HEXCHAT
    else:
        return hexchat.EAT_NONE


def channel_op(word, word_eol, userdata):
    # /DEOP objective
    # hexchat.prnt('Channel DeOp')
    # hexchat.prnt(', '.join(word))
    global op_returned
    nick = word[0]
    objectives = word[1].split(' ')

    for objective in objectives:
        if objective == my_nick:
            op_returned = True
            break

    if is_colored_nicks_loaded:
        return hexchat.EAT_HEXCHAT
    else:
        return hexchat.EAT_NONE


def channel_ban(word, word_eol, userdata):
    # /BAN objective
    # hexchat.prnt('Channel Ban')
    # hexchat.prnt(', '.join(word))
    objective = word[1]
    if (':' not in objective) and ('(' not in objective) and (')' not in objective) and ('+' not in objective):
        entity = word[0]
        my_nick = hexchat.get_info('nick')
        for user in hexchat.get_list('users'):
            if user.nick == my_nick:
                if user.prefix == '@':
                    connection_id = hexchat.get_prefs('id')
                    if connection_id in my_idents:
                        my_ident = my_idents[connection_id]
                    else:
                        my_ident = '*'
                    if connection_id in my_ips:
                        my_ip = my_ips[connection_id]
                    else:
                        my_ip = '*'
                    my_user = my_nick + '!' + my_ident + '@' + my_ip
                    objective_regex = objective.replace('\\', '\\\\').replace('.', '\.').replace('?', '.')\
                                               .replace('*', '.*').replace('[', '\[').replace('|', '\|')

                    if search(objective_regex, my_user):
                        if '.' in entity:
                            hexchat.command(f'mode -b+e {objective} {objective}')
                        else:
                            hexchat.command(f'mode -b+e-o+b {objective} {objective} {entity} {entity}')
                break

    if is_colored_nicks_loaded:
        return hexchat.EAT_HEXCHAT
    else:
        return hexchat.EAT_NONE


def you_kicked(word, word_eol, userdata):
    # /KICK objective
    # hexchat.prnt('Kick')
    # hexchat.prnt(', '.join(word))
    chat = hexchat.get_info('host')
    my_nick = hexchat.get_info('nick').lower()
    key = (chat, my_nick)

    if key in channels.keys():
        channel = hexchat.get_info('channel').lower()
        if channel in channels[key]:
            nick = word[2]
            hexchat.command(f'msg CHaN deop {channel} {nick}')

    if is_colored_nicks_loaded:
        return hexchat.EAT_HEXCHAT
    else:
        return hexchat.EAT_NONE


def private_message(word, word_eol, userdata):
    # hexchat.prnt('Private Message')
    # hexchat.prnt(', '.join(word))
    nick = word[0]
    msg = hexchat.strip(word[1])

    if nick == 'CHaN':
        my_nick = hexchat.get_info('nick')
        if search(f'Se eliminaron [0-9]+ bans que afectaban al usuario {my_nick} en #', msg):
            channel = msg[msg.find('#'):]
            hexchat.command(f'join {channel}')

    if is_colored_nicks_loaded:
        return hexchat.EAT_HEXCHAT
    else:
        return hexchat.EAT_NONE


def akick_command(word, word_eol, userdata):
    # /AKICK objective
    # hexchat.prnt('AKICK')
    # hexchat.prnt(', '.join(word))
    global akick
    targets = word_eol[1].split(' ')
    channel = hexchat.get_info('channel').lower()
    connection_id = hexchat.get_prefs('id')
    key = (connection_id, channel)

    if targets[-1] == '':
        targets = targets[:-1]
    targets = list(set(targets))
    for i, target in enumerate(targets):
        j = target.find('!')
        k = target.find('@')
        if (j == -1) & (k == -1):
            targets[i] = target + '!*@*'
        if ('(' in target) or (')' in target) or ('+' in target):
            del targets[i]
            hexchat.prnt('Invalid mask')

    if key in akick.keys():
        akick[key] = list(set(akick[key] + targets))
    else:
        akick[key] = targets

    for target in targets:
        target_nick = target[:target.find('!')]
        hexchat.command(f'mode -e+b {target} {target}')
        if target_nick != '*':
            hexchat.command(f'kick {target_nick}')

    return hexchat.EAT_ALL


def rmakick_command(word, word_eol, userdata):
    # /RMAKICK objective
    # hexchat.prnt('AKICK')
    # hexchat.prnt(', '.join(word))
    global akick
    targets = word_eol[1].split(' ')
    channel = hexchat.get_info('channel').lower()
    connection_id = hexchat.get_prefs('id')
    key = (connection_id, channel)

    if targets[-1] == '':
        targets = targets[:-1]
    for i, target in enumerate(targets):
        j = target.find('!')
        k = target.find('@')
        if (j == -1) & (k == -1):
            targets[i] = target + '!*@*'

    if key in akick.keys():
        akicks = list(set(akick[key]) - set(targets))
        if akicks:
            akick[key] = akicks
        else:
            del akick[key]

    return hexchat.EAT_ALL


def listakick_command(word, word_eol, userdata):
    # /LISTAKICK objective
    # hexchat.prnt('LISTAKICK')
    # hexchat.prnt(', '.join(word))
    channel = hexchat.get_info('channel').lower()
    connection_id = hexchat.get_prefs('id')
    key = (connection_id, channel)

    if key in akick.keys():
        hexchat.prnt(', '.join(akick[key]))

    return hexchat.EAT_ALL


def join(word, word_eol, userdata):
    # hexchat.prnt('Join')
    # hexchat.prnt(', '.join(word))
    channel = word[1]
    nick = word[0]
    host = nick + '!' + hexchat.strip(word[2])
    connection_id = hexchat.get_prefs('id')
    key = (connection_id, channel)

    if key in akick.keys():
        for value in akick[key]:
            value_regex = value.replace('\\', '\\\\').replace('.', '\.').replace('?', '.')\
                               .replace('*', '.*').replace('[', '\[').replace('|', '\|')
            if search(value_regex, host):
                hexchat.command(f'kick {nick}')

    if is_colored_nicks_loaded:
        return hexchat.EAT_HEXCHAT
    else:
        return hexchat.EAT_NONE


def channel_unban(word, word_eol, userdata):
    # /UNBAN objective
    # hexchat.prnt('Channel UnBan')
    # hexchat.prnt(', '.join(word))
    entity = word[0]
    my_nick = hexchat.get_info('nick')

    if entity != my_nick:
        connection_id = hexchat.get_prefs('id')
        channel = hexchat.get_info('channel').lower()
        key = (connection_id, channel)

        if key in akick.keys():
            objective = word[1]

            if objective in akick[key]:
                hexchat.command(f'mode b {objective}')

    if is_colored_nicks_loaded:
        return hexchat.EAT_HEXCHAT
    else:
        return hexchat.EAT_NONE


def channel_remove_exempt(word, word_eol, userdata):
    # /MODE #channel -e objective
    # hexchat.prnt('Channel Remove Exempt')
    # hexchat.prnt(', '.join(word))
    objective = word[1]
    if ('(' not in objective) and (')' not in objective) and ('+' not in objective):
        my_nick = hexchat.get_info('nick')
        connection_id = hexchat.get_prefs('id')

        if connection_id in my_idents:
            my_ident = my_idents[connection_id]
        else:
            my_ident = '*'
        if connection_id in my_ips:
            my_ip = my_ips[connection_id]
        else:
            my_ip = '*'
        my_user = my_nick + '!' + my_ident + '@' + my_ip
        objective_regex = objective.replace('\\', '\\\\').replace('.', '\.').replace('?', '.')\
                                   .replace('*', '.*').replace('[', '\[').replace('|', '\|')

        if search(objective_regex, my_user):
            for user in hexchat.get_list('users'):
                if user.nick == my_nick:
                    if user.prefix == '@':
                        hexchat.command(f'mode e {objective}')
                    break

    if is_colored_nicks_loaded:
        return hexchat.EAT_HEXCHAT
    else:
        return hexchat.EAT_NONE


def server_text(word, word_eol, userdata):
    # hexchat.prnt('Server Text')
    # hexchat.prnt(', '.join(word))
    global my_ips, my_idents
    text = hexchat.strip(word[0])
    connection_id = hexchat.get_prefs('id')

    if text.endswith(':is now your displayed host'):
        my_ips[connection_id] = text[:text.find(' ')]
    elif search(f'^Welcome to the .+ IRC Network {user_regex}$', text):
        user = search(user_regex, text).group()
        i = user.find('!')
        j = user.find('@')
        my_idents[connection_id] = user[i + 1:j]

    return hexchat.EAT_NONE


def invite(word, word_eol, userdata):
    # hexchat.prnt('Invite')
    # hexchat.prnt(', '.join(word))
    chat = hexchat.get_info('host')
    my_nick = hexchat.get_info('nick').lower()
    key = (chat, my_nick)

    if key in channels.keys():
        channel = word[0]
        if channel in channels[key]:
            hexchat.command(f'msg CHaN invite {channel}')

    if is_colored_nicks_loaded:
        return hexchat.EAT_HEXCHAT
    else:
        return hexchat.EAT_NONE


def invited(word, word_eol, userdata):
    # hexchat.prnt('Invited')
    # hexchat.prnt(', '.join(word))
    chat = hexchat.get_info('host')
    my_nick = hexchat.get_info('nick').lower()
    key = (chat, my_nick)

    if key in channels.keys():
        channel = word[0]
        if channel in channels[key]:
            hexchat.command(f'join {channel}')

    return hexchat.EAT_HEXCHAT


hexchat.hook_command('voicec', chan_command)
hexchat.hook_command('devoicec', chan_command)
hexchat.hook_command('opc', chan_command)
hexchat.hook_command('deopc', chan_command)
hexchat.hook_print('Your Nick Changing', your_nick_changing)

hexchat.hook_command('ban', ban_command)
hexchat.hook_command('unban', unban_command)
hexchat.hook_print('Channel Message', channel_message)
hexchat.hook_print('Channel Msg Hilight', channel_message)
hexchat.hook_print('Channel Action', channel_message)
hexchat.hook_print('Channel Action Hilight', channel_message)

hexchat.hook_command('exempt', exempt_command)
hexchat.hook_command('unexempt', unexempt_command)
hexchat.hook_command('exemptme', exemptme_command)

hexchat.hook_print('Banned', banned)
hexchat.hook_print('Channel DeOp', channel_deop)
hexchat.hook_print('Channel Op', channel_op)
hexchat.hook_print('Channel Ban', channel_ban)
hexchat.hook_print('You Kicked', you_kicked)
hexchat.hook_print('Private Message to Dialog', private_message)
hexchat.hook_print('Private Message', private_message)

hexchat.hook_command('akick', akick_command)
hexchat.hook_command('rmakick', rmakick_command)
hexchat.hook_command('listakick', listakick_command)
hexchat.hook_print('Join', join)
hexchat.hook_print('Channel UnBan', channel_unban)
hexchat.hook_print('Channel Remove Exempt', channel_remove_exempt)

hexchat.hook_print('Invite', invite)
hexchat.hook_print('Invited', invited)

hexchat.hook_print('Server Text', server_text)


print(__module_name__, 'loaded')

