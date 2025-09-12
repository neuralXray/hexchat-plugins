# -*- coding: UTF-8 -*-

__module_name__        = 'Colored Nicks'
__module_version__     = '1.0'
__module_description__ = 'Colorize nicks in all text events.'


import hexchat

import sys
sys.path.insert(0, hexchat.get_info('configdir') + '/addons/utils')
from hexchat_utils import logging, colored_nick, user_fields_extractor, my_nick_host, \
                          message_word_extractor, channel_word_extractor, \
                          outer_word_extractor, inner_word_extractor, \
                          server_context, channel_context, \
                          get_chanopt, get_complete_chanopt, \
                          color, reset

from re import search, IGNORECASE


sound_file = 'mixkit-message-pop-alert-2354.wav'

highlight_color = '18'
join_color = '23'
part_color = '21'
ban_color = '4'
unban_color = '3'

bold = '\002'
italics = '\035'

hide_joins_parts = 1 << 6
hide_joins_parts_unset = 1 << 7

highlighted_windows = []
focused_tab = (0, '')


# 1. Hook's callbacks
# 1.1. Server
def resolving_user(word, word_eol, userdata):
    # hexchat.prnt('Resolving User')
    # hexchat.prnt(', '.join(word))
    nick = colored_nick(word[0])

    printout = '*\tLooking up IP number for ' + nick + '...'

    hexchat.prnt(printout)
    return hexchat.EAT_HEXCHAT


def sasl_authenticating(word, word_eol, userdata):
    # hexchat.prnt('SASL Authenticating')
    # hexchat.prnt(', '.join(word))
    nick = colored_nick(word[0])
    mechanism = word[1]

    printout = '*\tAuthenticating via SASL as ' + nick + ' (' + mechanism + ')'

    hexchat.prnt(printout)
    return hexchat.EAT_HEXCHAT


def ping_reply(word, word_eol, userdata):
    # /PING [nick]
    # hexchat.prnt('Ping Reply')
    # hexchat.prnt(', '.join(word))
    entity = word[0]
    if '.' not in entity:
        entity = colored_nick(entity)
    seconds = word[1]

    printout = '*\tPing reply from ' + entity + ': ' + seconds + ' seconds'

    context = server_context(hexchat.get_prefs('id'))
    context.prnt(printout)
    context.command('GUI COLOR 2')
    if (hexchat.get_info('away') is None) | (hexchat.get_prefs('away_omit_alerts') == 0):
        hexchat.command('SPLAY ' + sound_file)
    return hexchat.EAT_HEXCHAT


def server_text(word, word_eol, userdata):
    # hexchat.prnt('Server Text')
    # hexchat.prnt(', '.join(word))

    printout = '*\t' + hexchat.strip(word[0])

    context = server_context(hexchat.get_prefs('id'))
    context.prnt(printout)
    return hexchat.EAT_HEXCHAT


# 1.2. Messages
def your_message(word, word_eol, userdata):
    # hexchat.prnt('Your Message / Channel Message')
    # hexchat.prnt(', '.join(word))
    nick, msg = message_word_extractor(word)

    printout = '\t<' + nick + '> ' + msg

    hexchat.prnt(printout)
    return hexchat.EAT_HEXCHAT


def channel_message(word, word_eol, userdata):
    # hexchat.prnt('Your Message / Channel Message')
    # hexchat.prnt(', '.join(word))
    my_nick = hexchat.get_info('nick').replace('\\', '\\\\').replace('[', '\[').replace('|', '\|')

    my_nick_regex = '(?<![a-z])' + my_nick + '(?![a-z])'
    if search(my_nick_regex, word[1], flags=IGNORECASE):
        if len(word) > 2:
            mode = word[2]
        else:
            mode = ''
        hexchat.emit_print('Channel Msg Hilight', word[0], word[1], mode)
    else:
        nick, msg = message_word_extractor(word)
        printout = '\t<' + nick + '> ' + msg
        hexchat.prnt(printout)
        connection_id = hexchat.get_prefs('id')
        channel = hexchat.get_info('channel')
        if (connection_id, channel) not in highlighted_windows:
            hexchat.command('GUI COLOR 2')

    return hexchat.EAT_HEXCHAT


def private_message_to_dialog(word, word_eol, userdata):
    # hexchat.prnt('Private Message to Dialog')
    # hexchat.prnt(', '.join(word))
    nick, msg = message_word_extractor(word)

    printout = '\t<' + nick + '> ' + msg

    hexchat.prnt(printout)
    hexchat.command('GUI COLOR 3')
    if (hexchat.get_info('away') is None) | (hexchat.get_prefs('away_omit_alerts') == 0):
        hexchat.command('SPLAY ' + sound_file)
    return hexchat.EAT_HEXCHAT


def channel_message_highlight(word, word_eol, userdata):
    # hexchat.prnt('Channel Msg Hilight')
    # hexchat.prnt(', '.join(word))
    global highlighted_windows
    nick, msg = message_word_extractor(word)

    msg = bold + color + highlight_color + msg

    printout = '\t<' + nick + '> ' + msg
    hexchat.prnt(printout)
    channel = hexchat.get_info('channel')
    printout = '\t' + channel + ' <' + nick + '> ' + msg
    context = server_context(hexchat.get_prefs('id'))
    context.prnt(printout)

    context.command('GUI COLOR 0')
    hexchat.command('GUI COLOR 3')
    connection_id = hexchat.get_prefs('id')
    channel = hexchat.get_info('channel')
    highlighted_window = (connection_id, channel)
    if (highlighted_window not in highlighted_windows) & (highlighted_window != focused_tab):
        highlighted_windows.append(highlighted_window)

    if (hexchat.get_info('away') is None) | (hexchat.get_prefs('away_omit_alerts') == 0):
        hexchat.command('SPLAY ' + sound_file)

    return hexchat.EAT_HEXCHAT


def message_send(word, word_eol, userdata):
    # /MSG nick msg
    # hexchat.prnt('Message Send')
    # hexchat.prnt(', '.join(word))
    nick, msg = message_word_extractor(word)

    printout = '\tPrivate message sent to ' + nick + ': ' + msg

    context = server_context(hexchat.get_prefs('id'))
    context.prnt(printout)
    return hexchat.EAT_HEXCHAT


def private_message(word, word_eol, userdata):
    # hexchat.prnt('Private Message')
    # hexchat.prnt(', '.join(word))
    nick, msg = message_word_extractor(word)

    printout = '\tPrivate message received: <' + nick + '> ' + msg

    context = server_context(hexchat.get_prefs('id'))
    context.prnt(printout)
    context.command('GUI COLOR 3')
    if (hexchat.get_info('away') is None) | (hexchat.get_prefs('away_omit_alerts') == 0):
        hexchat.command('SPLAY ' + sound_file)
    return hexchat.EAT_HEXCHAT


def receive_wallops(word, word_eol, userdata):
    # hexchat.prnt('Receive Wallops')
    # hexchat.prnt(', '.join(word))
    nick, msg = message_word_extractor(word)

    printout = '*\t-' + nick + '/Wallops- ' + msg

    context = server_context(hexchat.get_prefs('id'))
    context.prnt(printout)
    context.command('GUI COLOR 3')
    if (hexchat.get_info('away') is None) | (hexchat.get_prefs('away_omit_alerts') == 0):
        hexchat.command('SPLAY ' + sound_file)
    return hexchat.EAT_HEXCHAT


# 1.3. Actions
def your_action(word, word_eol, userdata):
    # /ME msg
    # hexchat.prnt('Your Action / Channel Action')
    # hexchat.prnt(', '.join(word))
    nick, msg = message_word_extractor(word)

    nick = italics + nick
    msg = italics + msg
    printout = '\t' + nick + ' ' + msg

    hexchat.prnt(printout)
    return hexchat.EAT_HEXCHAT


def channel_action(word, word_eol, userdata):
    # /ME msg
    # hexchat.prnt('Your Action / Channel Action')
    # hexchat.prnt(', '.join(word))
    my_nick = hexchat.get_info('nick').replace('\\', '\\\\').replace('[', '\[').replace('|', '\|')
    my_nick_regex = '(?<![a-z])' + my_nick + '(?![a-z])'
    if search(my_nick_regex, word[1], flags=IGNORECASE):
        if len(word) > 2:
            mode = word[2]
        else:
            mode = ''
        hexchat.emit_print('Channel Action Hilight', word[0], word[1], word[2])
    else:
        nick, msg = message_word_extractor(word)
        nick = italics + nick
        msg = italics + msg
        printout = '\t' + nick + ' ' + msg
        hexchat.prnt(printout)
        connection_id = hexchat.get_prefs('id')
        channel = hexchat.get_info('channel')
        if (connection_id, channel) not in highlighted_windows:
            hexchat.command('GUI COLOR 2')

    return hexchat.EAT_HEXCHAT


def private_action_to_dialog(word, word_eol, userdata):
    # /ME msg
    # hexchat.prnt('Private Action to Dialog')
    # hexchat.prnt(', '.join(word))
    nick, msg = message_word_extractor(word)

    nick = italics + nick
    msg = italics + msg
    printout = '\t' + nick + ' ' + msg

    hexchat.prnt(printout)
    hexchat.command('GUI COLOR 3')
    if (hexchat.get_info('away') is None) | (hexchat.get_prefs('away_omit_alerts') == 0):
        hexchat.command('SPLAY ' + sound_file)
    return hexchat.EAT_HEXCHAT


def channel_action_highlight(word, word_eol, userdata):
    # hexchat.prnt('Channel Action Hilight')
    # hexchat.prnt(', '.join(word))
    global highlighted_windows
    nick, msg = message_word_extractor(word)

    nick = italics + nick
    msg = italics + bold + color + highlight_color + msg

    printout = '\t' + nick + ' ' + msg
    hexchat.prnt(printout)
    channel = hexchat.get_info('channel')
    printout = '\t' + channel + ' ' + nick + ' ' + msg
    context = server_context(hexchat.get_prefs('id'))
    context.prnt(printout)

    context.command('GUI COLOR 0')
    hexchat.command('GUI COLOR 3')
    connection_id = hexchat.get_prefs('id')
    channel = hexchat.get_info('channel')
    highlighted_window = (connection_id, channel)
    if (highlighted_window not in highlighted_windows) & (highlighted_window != focused_tab):
        highlighted_windows.append(highlighted_window)

    if (hexchat.get_info('away') is None) | (hexchat.get_prefs('away_omit_alerts') == 0):
        hexchat.command('SPLAY ' + sound_file)

    return hexchat.EAT_HEXCHAT


def private_action(word, word_eol, userdata):
    # hexchat.prnt('Private Action')
    # hexchat.prnt(', '.join(word))
    nick, msg = message_word_extractor(word)

    nick = italics + nick
    msg = italics + msg
    printout = '\tPrivate message received: ' + nick + ' ' + msg

    context = server_context(hexchat.get_prefs('id'))
    context.prnt(printout)
    context.command('GUI COLOR 3')
    if (hexchat.get_info('away') is None) | (hexchat.get_prefs('away_omit_alerts') == 0):
        hexchat.command('SPLAY ' + sound_file)
    return hexchat.EAT_HEXCHAT


# 1.4. Notices
def notice_send(word, word_eol, userdata):
    # /NOTICE recipient msg
    # hexchat.prnt('Notice Send')
    # hexchat.prnt(', '.join(word))
    recipient = word[0]
    msg = hexchat.strip(word[1])
    msg = color + highlight_color + msg
    nick = colored_nick(hexchat.get_info('nick'))

    if recipient[0] == '#':
        printout = '*\t' + nick + ' ' + color + highlight_color + msg
        if hexchat.get_info('channel') != recipient:
            channel_context(hexchat.get_prefs('id'), recipient).prnt(printout)
        else:
            hexchat.prnt(printout)

    else:
        recipient = colored_nick(recipient)

        printout = '*\tNotice sent to ' + recipient + ': ' + color + highlight_color + msg
        server_context(hexchat.get_prefs('id')).prnt(printout)

    return hexchat.EAT_HEXCHAT


def channel_notice(word, word_eol, userdata):
    # hexchat.prnt('Channel Notice')
    # hexchat.prnt(', '.join(word))
    global highlighted_windows
    nick = colored_nick(word[0])
    channel = word[1]
    msg = hexchat.strip(word[2])

    printout = '*\t' + nick + ' ' + color + highlight_color + msg
    hexchat.prnt(printout)

    hexchat.command('GUI COLOR 3')
    connection_id = hexchat.get_prefs('id')
    highlighted_window = (connection_id, channel)
    if (highlighted_window not in highlighted_windows) & (highlighted_window != focused_tab):
        highlighted_windows.append(highlighted_window)

    if (hexchat.get_info('away') is None) | (hexchat.get_prefs('away_omit_alerts') == 0):
        hexchat.command('SPLAY ' + sound_file)

    return hexchat.EAT_HEXCHAT


def notice(word, word_eol, userdata):
    # hexchat.prnt('Notice')
    # hexchat.prnt(', '.join(word))
    nick = colored_nick(word[0])
    msg = hexchat.strip(word[1])

    printout = '*\t' + nick + ' ' + color + highlight_color + msg

    context = server_context(hexchat.get_prefs('id'))
    context.prnt(printout)
    context.command('GUI COLOR 3')
    if (hexchat.get_info('away') is None) | (hexchat.get_prefs('away_omit_alerts') == 0):
        hexchat.command('SPLAY ' + sound_file)
    return hexchat.EAT_HEXCHAT


# 1.5. Nick (Channel) management
def raw_modes(word, word_eol, userdata):
    # /MODE objective [+]/-mode[[+]/-mode]
    # hexchat.prnt('Raw Modes')
    # hexchat.prnt(', '.join(word))
    entity = word[0]
    if '.' not in entity:
        entity = colored_nick(entity)

    modes = word[1]
    s = modes.find(' ')
    channel = modes[0] == '#'

    if channel:
        modes = modes[s + 1:]
        s = modes.find(' ')
        if s == -1:
            if modes[0] == ':':
                modes = modes[1:]
            printout = '*\t' + entity + ' sets mode(s) ' + modes

            hexchat.prnt(printout)

        else:
            objectives = modes[s + 1:]
            objectives = objectives.split(' ')
            colored_objectives = []
            modes = modes[:s]
            modes0 = modes[0]
            modes1 = list(set(modes[1:]))

            if (modes0 == '+') & (len(modes1) == 1) & (modes1[0] == 'b'):
                for objective in objectives:
                    if objective[0] == ':':
                        objective = objective[1:]
                    if ':' not in objective:
                        objective_nick, objective_username, objective_host = user_fields_extractor(objective)
                        if '*' in objective_nick:
                            objective = color + ban_color + objective_nick + \
                                        '!' + objective_username + '@' + objective_host + reset
                        else:
                            objective = objective_nick + color + ban_color + \
                                        '!' + objective_username + '@' + objective_host + reset
                    else:
                        objective = color + ban_color + objective
                    colored_objectives.append(objective)
                colored_objectives = (color + ban_color + ', ' + reset).join(colored_objectives)

                if '.' in entity:
                    printout = '*\t' + color + ban_color + entity + ' sets mode(s) ' + modes + \
                               ' on ' + reset + colored_objectives
                else:
                    printout = '*\t' + entity + color + ban_color + ' sets mode(s) ' + modes + \
                               ' on ' + reset + colored_objectives

            elif (modes0 == '-') & (len(modes1) == 1) & (modes1[0] == 'b'):
                for objective in objectives:
                    if objective[0] == ':':
                        objective = objective[1:]
                    if ':' not in objective:
                        objective_nick, objective_username, objective_host = user_fields_extractor(objective)
                        if '*' in objective_nick:
                            objective = color + unban_color + objective_nick + \
                                        '!' + objective_username + '@' + objective_host + reset
                        else:
                            objective = objective_nick + color + unban_color + \
                                        '!' + objective_username + '@' + objective_host + reset
                    else:
                        objective = color + unban_color + objective
                    colored_objectives.append(objective)
                colored_objectives = (color + unban_color + ', ' + reset).join(colored_objectives)

                if '.' in entity:
                    printout = '*\t' + color + unban_color + entity + ' sets mode(s) ' + modes + \
                               ' on ' + reset + colored_objectives
                else:
                    printout = '*\t' + entity + color + unban_color + ' sets mode(s) ' + modes + \
                               ' on ' + reset + colored_objectives

            else:
                for objective in objectives:
                    if objective[0] == ':':
                        objective = objective[1:]
                    if (':' not in objective) & bool(sum([char not in '0123456789' for char in objective])):
                        objective_nick, objective_username, objective_host = user_fields_extractor(objective)
                        if bool(objective_username) & bool(objective_host):
                            objective = objective_nick + '!' + objective_username + '@' + objective_host
                        else:
                            objective = objective_nick
                        colored_objectives.append(objective)
                    else:
                        modes = modes + ' ' + objective
                colored_objectives = ', '.join(list(set(colored_objectives)))

                printout = '*\t' + entity + ' sets mode(s) ' + modes
                if colored_objectives:
                    printout = printout + ' on ' + colored_objectives

            hexchat.prnt(printout)

    else:
        objective = colored_nick(modes[:s])
        modes = modes[s + 2:]

        printout = '*\t' + entity + ' sets mode(s) ' + modes + ' on ' + objective

        context = server_context(hexchat.get_prefs('id'))
        context.prnt(printout)

    return hexchat.EAT_HEXCHAT


def channel_mode_generic(word, word_eol, userdata):
    # /MODE objective [+]/-mode[[+]/-mode]
    # hexchat.prnt('Channel Mode Generic')
    # hexchat.prnt(', '.join(word))
    global highlighted_windows
    entity = word[0]
    if '.' not in entity:
        entity = colored_nick(entity)
    mode = word[1] + word[2]
    objective = word[3]
    s = objective.find(' ')
    if s != -1:
        objective_ = objective[s + 1:]
        if bool(sum([char not in '0123456789' for char in objective_])):
            objective = objective_
        else:
            mode = mode + ' ' + objective_
            objective = objective[:s]

    printout = '*\t' + entity + ' sets mode ' + mode
    if objective[0] != '#':
        objective = colored_nick(objective)
        printout = printout + ' on ' + objective

    if (s == -1) & (objective[0] != '#'):
        context = server_context(hexchat.get_prefs('id'))
        context.prnt(printout)
        if hexchat.strip(objective) == hexchat.get_info('nick'):
            hexchat.command('GUI COLOR 3')
            connection_id = hexchat.get_prefs('id')
            channel = hexchat.get_info('channel')
            i = channel.find(' ')
            if i != -1:
                channel = channel[:i]
            highlighted_window = (connection_id, channel)
            if (highlighted_window not in highlighted_windows) & (highlighted_window != focused_tab):
                highlighted_windows.append(highlighted_window)
            if (hexchat.get_info('away') is None) | (hexchat.get_prefs('away_omit_alerts') == 0):
                hexchat.command('SPLAY ' + sound_file)
    else:
        hexchat.prnt(printout)

    return hexchat.EAT_HEXCHAT


def your_nick_changing(word, word_eol, userdata):
    # /NICK new_nick
    # hexchat.prnt('Your Nick Changing')
    # hexchat.prnt(', '.join(word))
    nick, msg = message_word_extractor(word)
    new_nick = colored_nick(msg)

    printout = '*\t' + nick + ' is now known as ' + new_nick

    hexchat.prnt(printout)
    return hexchat.EAT_HEXCHAT


def change_nick(word, word_eol, userdata):
    # hexchat.prnt('Change Nick')
    # hexchat.prnt(', '.join(word))
    old_nick = colored_nick(word[0])
    new_nick = colored_nick(word[1])

    printout = '*\t' + old_nick + ' is now known as ' + new_nick

    hexchat.prnt(printout)
    return hexchat.EAT_HEXCHAT


def nick_clash(word, word_eol, userdata):
    # hexchat.prnt('Nick Clash')
    # hexchat.prnt(', '.join(word))
    nick = word[0]
    new_nick = word[1]

    if ':' not in nick:
        nick = colored_nick(nick)
    i = new_nick.find(':')
    if i != -1:
        new_nick = new_nick[:i]
    else:
        i = new_nick.find('!')
        if i != -1:
            new_nick = new_nick[:i]
    new_nick = colored_nick(new_nick)

    printout = '*\t' + nick + ' is already in use, retrying with ' + new_nick + '...'

    hexchat.prnt(printout)
    return hexchat.EAT_HEXCHAT


def nick_erroneous(word, word_eol, userdata):
    # hexchat.prnt('Nick Erroneous')
    # hexchat.prnt(', '.join(word))
    nick, msg = message_word_extractor(word)
    new_nick = colored_nick(msg)

    printout = '*\t' + nick + ' is erroneous, retrying with ' + new_nick + '...'

    hexchat.prnt(printout)
    return hexchat.EAT_HEXCHAT


def killed(word, word_eol, userdata):
    # result of other /MSG NiCK GHOST nick password
    # hexchat.prnt('Killed')
    # hexchat.prnt(', '.join(word))
    nick = colored_nick(word[0])
    reason = hexchat.strip(word[1])

    printout = '*\t' + color + ban_color + 'You have been killed by ' + reset + nick + color + ban_color + \
               ' (' + reason + ')'

    hexchat.prnt(printout)
    return hexchat.EAT_HEXCHAT


# 1.6. Whois
# /WHOIS nick
def whois_name_line(word, word_eol, userdata):
    # hexchat.prnt('Whois Name Line')
    # hexchat.prnt(', '.join(word))
    nick = colored_nick(word[0])
    user_name = word[1]
    host = word[2]
    real_name = hexchat.strip(word[3])

    printout = '*\t[' + nick + '] (' + user_name + '@' + host + '): ' + real_name

    context = server_context(hexchat.get_prefs('id'))
    context.prnt(printout)

    return hexchat.EAT_HEXCHAT


def whois_real_host(word, word_eol, userdata):
    # hexchat.prnt('Whois Real Host')
    # hexchat.prnt(', '.join(word))
    nick = colored_nick(word[0])
    real_host = word[1]
    ip = word[2]

    printout = '*\t[' + nick + '] Real Host: ' + real_host + ', Real IP: [' + ip + ']'

    context = server_context(hexchat.get_prefs('id'))
    context.prnt(printout)
    return hexchat.EAT_HEXCHAT


def whois(word, word_eol, userdata):
    # hexchat.prnt('Whois Channel/Oper Line / Whois Server Line / Whois Identified / Whois Special')
    # hexchat.prnt(', '.join(word))
    nick = colored_nick(word[0])
    info = hexchat.strip(word[1])

    printout = '*\t[' + nick + '] ' + info

    context = server_context(hexchat.get_prefs('id'))
    context.prnt(printout)
    return hexchat.EAT_HEXCHAT


def whois_authenticated(word, word_eol, userdata):
    # hexchat.prnt('Whois Authenticated')
    # hexchat.prnt(', '.join(word))
    nick = colored_nick(word[0])
    info = word[1]
    nick_authenticated = word[2]

    printout = '*\t[' + nick + '] ' + info + ' ' + nick_authenticated

    context = server_context(hexchat.get_prefs('id'))
    context.prnt(printout)
    return hexchat.EAT_HEXCHAT


def whois_away_line(word, word_eol, userdata):
    # hexchat.prnt('Whois Away Line')
    # hexchat.prnt(', '.join(word))
    nick = colored_nick(word[0])
    info = hexchat.strip(word[1])

    printout = '*\t[' + nick + '] is away (' + info + ')'

    context = server_context(hexchat.get_prefs('id'))
    context.prnt(printout)
    return hexchat.EAT_HEXCHAT


def whois_idle_line(word, word_eol, userdata):
    # hexchat.prnt('Whois Idle Line')
    # hexchat.prnt(', '.join(word))
    nick = colored_nick(word[0])
    idle = word[1]

    printout = '*\t[' + nick + '] idle ' + idle

    context = server_context(hexchat.get_prefs('id'))
    context.prnt(printout)
    return hexchat.EAT_HEXCHAT


def whois_idle_line_with_signed_on(word, word_eol, userdata):
    # hexchat.prnt('Whois Idle Line with Signon')
    # hexchat.prnt(', '.join(word))
    nick = colored_nick(word[0])
    idle = word[1]
    signed_on = word[2]

    printout = '*\t[' + nick + '] idle ' + idle + ', signed on: ' + signed_on

    context = server_context(hexchat.get_prefs('id'))
    context.prnt(printout)
    return hexchat.EAT_HEXCHAT


def whois_end(word, word_eol, userdata):
    # hexchat.prnt('Whois End')
    # hexchat.prnt(', '.join(word))

    printout = '*\t' + word[0] + ' :End of WHOIS'

    context = server_context(hexchat.get_prefs('id'))
    context.prnt(printout)
    return hexchat.EAT_HEXCHAT


# 1.7. Join, part, quit
def you_join(word, word_eol, userdata):
    # /J #channel
    # hexchat.prnt('You Join')
    # hexchat.prnt(', '.join(word))
    channel = word[1]

    connection_id = hexchat.get_prefs('id')
    context = hexchat.get_context()
    if not get_complete_chanopt(context, connection_id, channel, 'irc_conf_mode',
                                hide_joins_parts_unset, hide_joins_parts):
        nick, host = outer_word_extractor(word)

        printout = '*\t' + nick + color + join_color + '!' + host + ' has joined'

        hexchat.prnt(printout)
    else:
        nick = hexchat.strip(word[0])
        host = hexchat.strip(word[2])

        printout = '*\t' + nick + '!' + host + ' has joined'

        network = hexchat.get_info('network').lower()
        logging(printout, network, channel)
    return hexchat.EAT_HEXCHAT


def join(word, word_eol, userdata):
    # hexchat.prnt('Join')
    # hexchat.prnt(', '.join(word))
    channel = word[1]

    connection_id = hexchat.get_prefs('id')
    context = hexchat.get_context()
    if not get_complete_chanopt(context, connection_id, channel, 'irc_conf_mode',
                                hide_joins_parts_unset, hide_joins_parts):
        nick, host = outer_word_extractor(word)

        printout = '*\t' + nick + color + join_color + '!' + host + ' has joined'

        hexchat.prnt(printout)
    else:
        nick = hexchat.strip(word[0])
        host = hexchat.strip(word[2])

        printout = '*\t' + nick + '!' + host + ' has joined'

        network = hexchat.get_info('network').lower()
        logging(printout, network, channel)
    return hexchat.EAT_HEXCHAT


def you_part(word, word_eol, userdata):
    # /PART
    # hexchat.prnt('You Part')
    # hexchat.prnt(', '.join(word))
    channel = word[2]

    connection_id = hexchat.get_prefs('id')
    context = hexchat.get_context()
    if not get_complete_chanopt(context, connection_id, channel, 'irc_conf_mode',
                                hide_joins_parts_unset, hide_joins_parts):
        nick, host = inner_word_extractor(word)

        printout = '*\t' + nick + color + part_color + '!' + host + '' + ' has left'

        hexchat.prnt(printout)
    else:
        nick = hexchat.strip(word[0])
        host = hexchat.strip(word[1])

        printout = '*\t' + nick + '!' + host + ' has left'

        network = hexchat.get_info('network').lower()
        logging(printout, network, channel)
    return hexchat.EAT_HEXCHAT


def you_part_with_reason(word, word_eol, userdata):
    # /PART #channel reason
    # hexchat.prnt('You Part')
    # hexchat.prnt(', '.join(word))
    channel = word[2]
    reason = word[3]

    connection_id = hexchat.get_prefs('id')
    context = hexchat.get_context()
    if not get_complete_chanopt(context, connection_id, channel, 'irc_conf_mode',
                                hide_joins_parts_unset, hide_joins_parts):
        nick, host = inner_word_extractor(word)

        printout = '*\t' + reset + nick + color + part_color + '!' + host + ' has left (' + reason + ')'

        hexchat.prnt(printout)
    else:
        nick = hexchat.strip(word[0])
        host = hexchat.strip(word[1])

        printout = '*\t' + nick + '!' + host + ' has left (' + reason + ')'

        network = hexchat.get_info('network').lower()
        logging(printout, network, channel)
    return hexchat.EAT_HEXCHAT


def part(word, word_eol, userdata):
    # hexchat.prnt('Part')
    # hexchat.prnt(', '.join(word))
    channel = word[2]

    connection_id = hexchat.get_prefs('id')
    context = hexchat.get_context()
    if not get_complete_chanopt(context, connection_id, channel, 'irc_conf_mode',
                                hide_joins_parts_unset, hide_joins_parts):
        nick, host = inner_word_extractor(word)

        printout = '*\t' + nick + color + part_color + '!' + host + ' has left'

        hexchat.prnt(printout)
    else:
        nick = hexchat.strip(word[0])
        host = hexchat.strip(word[1])

        printout = '*\t' + nick + '!' + host + ' has left'

        network = hexchat.get_info('network').lower()
        logging(printout, network, channel)
    return hexchat.EAT_HEXCHAT


def part_with_reason(word, word_eol, userdata):
    # hexchat.prnt('Part with Reason')
    # hexchat.prnt(', '.join(word))
    channel = word[2]
    reason = word[3]

    connection_id = hexchat.get_prefs('id')
    context = hexchat.get_context()
    if not get_complete_chanopt(context, connection_id, channel, 'irc_conf_mode',
                                hide_joins_parts_unset, hide_joins_parts):
        nick, host = inner_word_extractor(word)

        printout = '*\t' + nick + color + part_color + '!' + host + ' has left (' + reason + ')'

        hexchat.prnt(printout)
    else:
        nick = hexchat.strip(word[0])
        host = hexchat.strip(word[1])

        printout = '*\t' + nick + '!' + host + ' has left (' + reason + ')'

        network = hexchat.get_info('network').lower()
        logging(printout, network, channel)
    return hexchat.EAT_HEXCHAT


def hexchat_quit(word, word_eol, userdata):
    # hexchat.prnt('Quit')
    # hexchat.prnt(', '.join(word))
    reason = word[1]

    channel = hexchat.get_info('channel')
    connection_id = hexchat.get_prefs('id')
    context = hexchat.get_context()
    if (not get_complete_chanopt(context, connection_id, channel, 'irc_conf_mode',
                                 hide_joins_parts_unset, hide_joins_parts)) | \
       reason.startswith('G-lined'):
        nick, host = outer_word_extractor(word)

        printout = '*\t' + nick + color + part_color + '!' + host + ' has quit (' + reason + ')'

        hexchat.prnt(printout)
    else:
        nick = hexchat.strip(word[0])
        host = hexchat.strip(word[2])

        printout = '*\t' + nick + '!' + host + ' has quit (' + reason + ')'

        network = hexchat.get_info('network').lower()
        logging(printout, network, channel)
    return hexchat.EAT_HEXCHAT


# 1.8. Channels
def topic_creation(word, word_eol, userdata):
    # /TOPIC
    # hexchat.prnt('Topic Creation')
    # hexchat.prnt(', '.join(word))
    nick, username, host = user_fields_extractor(word[1])
    if bool(username) & bool(host):
        user = nick + '!' + username + '@' + host
    else:
        user = nick
    datetime = word[2]

    printout = '*\tTopic set by ' + user + ' (' + datetime + ')'

    hexchat.prnt(printout)
    return hexchat.EAT_HEXCHAT


def topic_change(word, word_eol, userdata):
    # /TOPIC topic
    # hexchat.prnt('Topic Change')
    # hexchat.prnt(', '.join(word))
    nick = colored_nick(word[0])
    topic = hexchat.strip(word[1])

    printout = '*\t' + nick + ' has changed the topic to: ' + topic

    hexchat.prnt(printout)
    return hexchat.EAT_HEXCHAT


def channel_voice(word, word_eol, userdata):
    # /VOICE objective
    # hexchat.prnt('Channel Voice')
    # hexchat.prnt(', '.join(word))
    global highlighted_windows
    nick, objective = channel_word_extractor(word)

    printout = '*\t' + nick + ' gives voice to ' + objective

    hexchat.prnt(printout)
    if hexchat.strip(objective) == hexchat.get_info('nick'):
        hexchat.command('GUI COLOR 3')
        connection_id = hexchat.get_prefs('id')
        channel = hexchat.get_info('channel')
        highlighted_window = (connection_id, channel)
        if (highlighted_window not in highlighted_windows) & (highlighted_window != focused_tab):
            highlighted_windows.append(highlighted_window)
        if (hexchat.get_info('away') is None) | (hexchat.get_prefs('away_omit_alerts') == 0):
            hexchat.command('SPLAY ' + sound_file)
    return hexchat.EAT_HEXCHAT


def channel_de_voice(word, word_eol, userdata):
    # /DEVOICE objective
    # hexchat.prnt('Channel DeVoice')
    # hexchat.prnt(', '.join(word))
    global highlighted_windows
    nick, objective = channel_word_extractor(word)

    printout = '*\t' + nick + ' removes voice from ' + objective

    hexchat.prnt(printout)
    if hexchat.strip(objective) == hexchat.get_info('nick'):
        hexchat.command('GUI COLOR 3')
        connection_id = hexchat.get_prefs('id')
        channel = hexchat.get_info('channel')
        highlighted_window = (connection_id, channel)
        if (highlighted_window not in highlighted_windows) & (highlighted_window != focused_tab):
            highlighted_windows.append(highlighted_window)
        if (hexchat.get_info('away') is None) | (hexchat.get_prefs('away_omit_alerts') == 0):
            hexchat.command('SPLAY ' + sound_file)
    return hexchat.EAT_HEXCHAT


def channel_operator(word, word_eol, userdata):
    # /OP objective
    # hexchat.prnt('Channel Operator')
    # hexchat.prnt(', '.join(word))
    global highlighted_windows
    nick, objective = channel_word_extractor(word)

    printout = '*\t' + nick + ' gives channel operator status to ' + objective

    hexchat.prnt(printout)
    if hexchat.strip(objective) == hexchat.get_info('nick'):
        hexchat.command('GUI COLOR 3')
        connection_id = hexchat.get_prefs('id')
        channel = hexchat.get_info('channel')
        highlighted_window = (connection_id, channel)
        if (highlighted_window not in highlighted_windows) & (highlighted_window != focused_tab):
            highlighted_windows.append(highlighted_window)
        if (hexchat.get_info('away') is None) | (hexchat.get_prefs('away_omit_alerts') == 0):
            hexchat.command('SPLAY ' + sound_file)
    return hexchat.EAT_HEXCHAT


def channel_de_op(word, word_eol, userdata):
    # /DEOP objective
    # hexchat.prnt('Channel DeOp')
    # hexchat.prnt(', '.join(word))
    global highlighted_windows
    nick, objective = channel_word_extractor(word)

    printout = '*\t' + nick + ' removes channel operator status from ' + objective

    hexchat.prnt(printout)
    if hexchat.strip(objective) == hexchat.get_info('nick'):
        hexchat.command('GUI COLOR 3')
        connection_id = hexchat.get_prefs('id')
        channel = hexchat.get_info('channel')
        highlighted_window = (connection_id, channel)
        if (highlighted_window not in highlighted_windows) & (highlighted_window != focused_tab):
            highlighted_windows.append(highlighted_window)
        if (hexchat.get_info('away') is None) | (hexchat.get_prefs('away_omit_alerts') == 0):
            hexchat.command('SPLAY ' + sound_file)
    return hexchat.EAT_HEXCHAT


def channel_half_operator(word, word_eol, userdata):
    # /HOP objective
    # hexchat.prnt('Channel Half-Operator')
    # hexchat.prnt(', '.join(word))
    global highlighted_windows
    nick, objective = channel_word_extractor(word)

    printout = '*\t' + nick + ' gives channel half-operator status to ' + objective

    hexchat.prnt(printout)
    if hexchat.strip(objective) == hexchat.get_info('nick'):
        hexchat.command('GUI COLOR 3')
        connection_id = hexchat.get_prefs('id')
        channel = hexchat.get_info('channel')
        highlighted_window = (connection_id, channel)
        if (highlighted_window not in highlighted_windows) & (highlighted_window != focused_tab):
            highlighted_windows.append(highlighted_window)
        if (hexchat.get_info('away') is None) | (hexchat.get_prefs('away_omit_alerts') == 0):
            hexchat.command('SPLAY ' + sound_file)
    return hexchat.EAT_HEXCHAT


def channel_de_half_op(word, word_eol, userdata):
    # /DEHOP objective
    # hexchat.prnt('Channel DeHalfOp')
    # hexchat.prnt(', '.join(word))
    global highlighted_windows
    nick, objective = channel_word_extractor(word)

    printout = '*\t' + nick + ' removes channel half-operator status from ' + objective

    hexchat.prnt(printout)
    if hexchat.strip(objective) == hexchat.get_info('nick'):
        hexchat.command('GUI COLOR 3')
        connection_id = hexchat.get_prefs('id')
        channel = hexchat.get_info('channel')
        highlighted_window = (connection_id, channel)
        if (highlighted_window not in highlighted_windows) & (highlighted_window != focused_tab):
            highlighted_windows.append(highlighted_window)
        if (hexchat.get_info('away') is None) | (hexchat.get_prefs('away_omit_alerts') == 0):
            hexchat.command('SPLAY ' + sound_file)
    return hexchat.EAT_HEXCHAT


def your_invitation(word, word_eol, userdata):
    # /INVITE nick
    # hexchat.prnt('Your Invitation')
    # hexchat.prnt(', '.join(word))
    nick = colored_nick(word[0])
    channel = word[1]
    # server = word[2]

    printout = '*\tYou have invited ' + nick
    if hexchat.get_info('channel') != channel:
        connection_id = hexchat.get_prefs('id')
        channel_context(connection_id, channel).prnt(printout)
        printout = printout + ' to ' + channel
    hexchat.prnt(printout)

    return hexchat.EAT_HEXCHAT


def invited(word, word_eol, userdata):
    # hexchat.prnt('Invited')
    # hexchat.prnt(', '.join(word))
    nick = colored_nick(word[1])
    channel = word[0]

    printout = '*\tYou have been invited to ' + channel + ' by ' + nick

    context = server_context(hexchat.get_prefs('id'))
    context.prnt(printout)
    context.command('GUI COLOR 3')
    if (hexchat.get_info('away') is None) | (hexchat.get_prefs('away_omit_alerts') == 0):
        hexchat.command('SPLAY ' + sound_file)
    return hexchat.EAT_HEXCHAT


def invited_other(word, word_eol, userdata):
    # hexchat.prnt('Invited Other')
    # hexchat.prnt(', '.join(word))
    nick = colored_nick(word[1])
    recipient = colored_nick(word[2])

    printout = '*\t' + recipient + ' has been invited by ' + nick

    hexchat.prnt(printout)
    return hexchat.EAT_HEXCHAT


def channel_invite(word, word_eol, userdata):
    # /MODE #channel I recipient
    # hexchat.prnt('Channel INVITE')
    # hexchat.prnt(', '.join(word))
    global highlighted_windows
    nick = colored_nick(word[0])
    recipient = word[1]
    recipient_nick, recipient_username, recipient_host = user_fields_extractor(recipient)

    printout = '*\t' + nick + ' sets invite exempt on ' + \
               recipient_nick + '!' + recipient_username + '@' + recipient_host

    hexchat.prnt(printout)
    my_nick, my_username, my_host = my_nick_host()
    my_user = f'{my_nick}!{my_username}@{my_host}'
    if search(recipient.replace('\\', '\\\\').replace('.', '\.').replace('?', '.').replace('*', '.*').replace('[', '\[').replace('|', '\|'), my_user):
        hexchat.command('GUI COLOR 3')
        connection_id = hexchat.get_prefs('id')
        channel = hexchat.get_info('channel')
        highlighted_window = (connection_id, channel)
        if (highlighted_window not in highlighted_windows) & (highlighted_window != focused_tab):
            highlighted_windows.append(highlighted_window)
        if (hexchat.get_info('away') is None) | (hexchat.get_prefs('away_omit_alerts') == 0):
            hexchat.command('SPLAY ' + sound_file)
    return hexchat.EAT_HEXCHAT


def channel_remove_invite(word, word_eol, userdata):
    # /MODE #channel -I recipient
    # hexchat.prnt('Channel Remove Invite')
    # hexchat.prnt(', '.join(word))
    global highlighted_windows
    nick = colored_nick(word[0])
    recipient = word[1]
    recipient_nick, recipient_username, recipient_host = user_fields_extractor(recipient)

    printout = '*\t' + nick + ' removes invite exempt on ' + \
               recipient_nick + '!' + recipient_username + '@' + recipient_host

    hexchat.prnt(printout)
    my_nick, my_username, my_host = my_nick_host()
    my_user = f'{my_nick}!{my_username}@{my_host}'
    if search(recipient.replace('\\', '\\\\').replace('.', '\.').replace('?', '.').replace('*', '.*').replace('[', '\[').replace('|', '\|'), my_user):
        hexchat.command('GUI COLOR 3')
        connection_id = hexchat.get_prefs('id')
        channel = hexchat.get_info('channel')
        highlighted_window = (connection_id, channel)
        if (highlighted_window not in highlighted_windows) & (highlighted_window != focused_tab):
            highlighted_windows.append(highlighted_window)
        if (hexchat.get_info('away') is None) | (hexchat.get_prefs('away_omit_alerts') == 0):
            hexchat.command('SPLAY ' + sound_file)
    return hexchat.EAT_HEXCHAT


def channel_set_key(word, word_eol, userdata):
    # /MODE k password
    # hexchat.prnt('Channel Set Key')
    # hexchat.prnt(', '.join(word))
    nick = colored_nick(word[0])
    password = word[1]

    printout = '*\t' + nick + ' sets channel keyword to ' + password

    hexchat.prnt(printout)
    return hexchat.EAT_HEXCHAT


def channel_remove_keyword(word, word_eol, userdata):
    # /MODE -k password
    # hexchat.prnt('Channel Remove Keyword')
    # hexchat.prnt(', '.join(word))
    nick = colored_nick(word[0])

    printout = '*\t' + nick + ' removes channel keyword'

    hexchat.prnt(printout)
    return hexchat.EAT_HEXCHAT


def channel_set_limit(word, word_eol, userdata):
    # /MODE l max_n_users
    # hexchat.prnt('Channel Set Limit')
    # hexchat.prnt(', '.join(word))
    nick = colored_nick(word[0])
    max_n_users = word[1]

    printout = '*\t' + nick + ' sets channel limit to ' + max_n_users

    hexchat.prnt(printout)
    return hexchat.EAT_HEXCHAT


def channel_remove_limit(word, word_eol, userdata):
    # /MODE -l
    # hexchat.prnt('Channel Remove Limit')
    # hexchat.prnt(', '.join(word))
    nick = colored_nick(word[0])

    printout = '*\t' + nick + ' removes user limit'

    hexchat.prnt(printout)
    return hexchat.EAT_HEXCHAT


def channel_quiet(word, word_eol, userdata):
    # /QUIET user
    # hexchat.prnt('Channel Quiet')
    # hexchat.prnt(', '.join(word))
    global highlighted_windows
    nick = colored_nick(word[0])
    objective = word[1]
    objective_nick, objective_username, objective_host = user_fields_extractor(objective)

    if objective_nick == '*':
        printout = '*\t' + nick + color + ban_color + ' sets quiet on ' + \
                   objective_nick + '!' + objective_username + '@' + objective_host
    else:
        printout = '*\t' + nick + color + ban_color + ' sets quiet on ' + reset + \
                   objective_nick + color + ban_color + '!' + objective_username + '@' + objective_host

    hexchat.prnt(printout)
    my_nick, my_username, my_host = my_nick_host()
    my_user = f'{my_nick}!{my_username}@{my_host}'
    if search(objective.replace('\\', '\\\\').replace('.', '\.').replace('?', '.').replace('*', '.*').replace('[', '\[').replace('|', '\|'), my_user):
        hexchat.command('GUI COLOR 3')
        connection_id = hexchat.get_prefs('id')
        channel = hexchat.get_info('channel')
        highlighted_window = (connection_id, channel)
        if (highlighted_window not in highlighted_windows) & (highlighted_window != focused_tab):
            highlighted_windows.append(highlighted_window)
        if (hexchat.get_info('away') is None) | (hexchat.get_prefs('away_omit_alerts') == 0):
            hexchat.command('SPLAY ' + sound_file)
    return hexchat.EAT_HEXCHAT


def channel_unquiet(word, word_eol, userdata):
    # /QUIET user
    # hexchat.prnt('Channel UnQuiet')
    # hexchat.prnt(', '.join(word))
    global highlighted_windows
    nick = colored_nick(word[0])
    objective = word[1]
    objective_nick, objective_username, objective_host = user_fields_extractor(objective)

    if objective_nick == '*':
        printout = '*\t' + nick + color + unban_color + ' removes quiet on ' + \
                   objective_nick + '!' + objective_username + '@' + objective_host
    else:
        printout = '*\t' + nick + color + unban_color + ' removes quiet on ' + reset + \
                   objective_nick + color + unban_color + '!' + objective_username + '@' + objective_host

    hexchat.prnt(printout)
    my_nick, my_username, my_host = my_nick_host()
    my_user = f'{my_nick}!{my_username}@{my_host}'
    if search(objective.replace('\\', '\\\\').replace('.', '\.').replace('?', '.').replace('*', '.*').replace('[', '\[').replace('|', '\|'), my_user):
        hexchat.command('GUI COLOR 3')
        connection_id = hexchat.get_prefs('id')
        channel = hexchat.get_info('channel')
        highlighted_window = (connection_id, channel)
        if (highlighted_window not in highlighted_windows) & (highlighted_window != focused_tab):
            highlighted_windows.append(highlighted_window)
        if (hexchat.get_info('away') is None) | (hexchat.get_prefs('away_omit_alerts') == 0):
            hexchat.command('SPLAY ' + sound_file)
    return hexchat.EAT_HEXCHAT


def channel_ban(word, word_eol, userdata):
    # /BAN objective
    # hexchat.prnt('Channel Ban')
    # hexchat.prnt(', '.join(word))
    global highlighted_windows
    entity = word[0]
    objective = word[1]

    if objective.startswith('m:'):
        mode = 'mute'
        objective = objective[objective.find('m:') + 2:]
    else:
        mode = 'ban'

    if ':' not in objective:
        objective_nick, objective_username, objective_host = user_fields_extractor(objective)
        if bool(objective_username) and bool(objective_host):
            if '*' in objective_nick:
                objective = objective_nick + '!' + objective_username + '@' + objective_host
            else:
                objective = reset + objective_nick + color + ban_color + '!' + objective_username + \
                            '@' + objective_host
        else:
            objective = objective_nick
        

    if '.' in entity:
        printout = '*\t' + color + ban_color + entity + f' sets {mode} on ' + objective
    else:
        entity = colored_nick(entity)
        printout = '*\t' + entity + color + ban_color + f' sets {mode} on ' + objective

    hexchat.prnt(printout)
    if ':' not in objective:
        my_nick, my_username, my_host = my_nick_host()
        my_user = f'{my_nick}!{my_username}@{my_host}'
        if search(objective.replace('\\', '\\\\').replace('.', '\.').replace('?', '.')\
                  .replace('*', '.*').replace('[', '\[').replace('|', '\|'), my_user):
            hexchat.command('GUI COLOR 3')
            connection_id = hexchat.get_prefs('id')
            channel = hexchat.get_info('channel')
            highlighted_window = (connection_id, channel)
            if (highlighted_window not in highlighted_windows) & (highlighted_window != focused_tab):
                highlighted_windows.append(highlighted_window)
            if (hexchat.get_info('away') is None) | (hexchat.get_prefs('away_omit_alerts') == 0):
                hexchat.command('SPLAY ' + sound_file)
    return hexchat.EAT_HEXCHAT


def channel_unban(word, word_eol, userdata):
    # /UNBAN objective
    # hexchat.prnt('Channel UnBan')
    # hexchat.prnt(', '.join(word))
    global highlighted_windows
    entity = word[0]
    objective = word[1]

    if objective.startswith('m:'):
        mode = 'mute'
        objective = objective[objective.find('m:') + 2:]
    else:
        mode = 'ban'

    if ':' not in objective:
        objective_nick, objective_username, objective_host = user_fields_extractor(objective)
        if bool(objective_username) and bool(objective_host):
            if '*' in objective_nick:
                colored_objective = objective_nick + '!' + objective_username + '@' + objective_host
            else:
                colored_objective = reset + objective_nick + color + unban_color + '!' + \
                                    objective_username + '@' + objective_host
        else:
            colored_objective = objective_nick
    else:
        colored_objective = objective

    if '.' in entity:
        printout = '*\t' + color + unban_color + entity + f' removes {mode} on ' + colored_objective
    else:
        entity = colored_nick(entity)
        printout = '*\t' + entity + color + unban_color + f' removes {mode} on ' + colored_objective

    hexchat.prnt(printout)
    if ':' not in objective:
        my_nick, my_username, my_host = my_nick_host()
        my_user = f'{my_nick}!{my_username}@{my_host}'
        if search(objective.replace('\\', '\\\\').replace('.', '\.').replace('?', '.')\
                  .replace('*', '.*').replace('[', '\[').replace('|', '\|'), my_user):
            hexchat.command('GUI COLOR 3')
            connection_id = hexchat.get_prefs('id')
            channel = hexchat.get_info('channel')
            highlighted_window = (connection_id, channel)
            if (highlighted_window not in highlighted_windows) & (highlighted_window != focused_tab):
                highlighted_windows.append(highlighted_window)
            if (hexchat.get_info('away') is None) | (hexchat.get_prefs('away_omit_alerts') == 0):
                hexchat.command('SPLAY ' + sound_file)
    return hexchat.EAT_HEXCHAT


def ban_list(word, word_eol, userdata):
    # /BAN
    # hexchat.prnt('Ban List')
    # hexchat.prnt(', '.join(word))
    channel = word[0]
    objective = word[1]
    nick = word[2]
    datetime = word[3]

    if ':' not in objective:
        objective_nick, objective_username, objective_host = user_fields_extractor(objective)
        if '*' in objective_nick:
            colored_objective = objective_nick + '!' + objective_username + '@' + objective_host
        else:
            colored_objective = reset + objective_nick + color + ban_color + '!' + \
                                objective_username + '@' + objective_host
    else:
        colored_objective = objective

    printout = '*\t' + color + ban_color + channel + ': ' + colored_objective + \
               ' on ' + datetime + ' by '
    if '.' not in nick:
        nick = colored_nick(nick)
        printout = printout + reset + nick
    else:
        printout = printout + nick

    hexchat.prnt(printout)
    return hexchat.EAT_HEXCHAT


def you_kicked(word, word_eol, userdata):
    # hexchat.prnt('You Kicked')
    # hexchat.prnt(', '.join(word))
    global highlighted_windows
    nick = colored_nick(word[0])
    kicker = word[2]
    if '.' in kicker:
        kicker = color + ban_color + kicker + reset
    else:
        kicker = colored_nick(kicker)
    if len(word) > 3:
        reason = hexchat.strip(word[3])
    else:
        reason = word[2]

    if word[2] == reason:
        printout = '*\t' + kicker + color + ban_color + ' has kicked ' + reset + nick
    else:
        printout = '*\t' + kicker + color + ban_color + ' has kicked ' + reset + nick + \
                   color + ban_color + ' (' + reason + ')'

    hexchat.prnt(printout)
    hexchat.command('GUI COLOR 3')
    connection_id = hexchat.get_prefs('id')
    channel = hexchat.get_info('channel')
    highlighted_window = (connection_id, channel)
    if (highlighted_window not in highlighted_windows) & (highlighted_window != focused_tab):
        highlighted_windows.append(highlighted_window)
    if (hexchat.get_info('away') is None) | (hexchat.get_prefs('away_omit_alerts') == 0):
        hexchat.command('SPLAY ' + sound_file)
    return hexchat.EAT_HEXCHAT


def kick(word, word_eol, userdata):
    # /KICK objective
    # hexchat.prnt('Kick')
    # hexchat.prnt(', '.join(word))
    entity = word[0]
    objective = colored_nick(word[1])
    if len(word) == 4:
        reason = hexchat.strip(word[3])
    else:
        reason = entity

    if reason == entity:
        printout = ''
    else:
        printout = color + ban_color + ' (' + reason + ')'
    if '.' in entity:
        entity = color + ban_color + entity + reset
    else:
        entity = colored_nick(entity)
    printout = '*\t' + entity + color + ban_color + ' has kicked ' + reset + objective + printout

    hexchat.prnt(printout)
    return hexchat.EAT_HEXCHAT


def channel_exempt(word, word_eol, userdata):
    # /MODE #channel e objective
    # hexchat.prnt('Channel Exempt')
    # hexchat.prnt(', '.join(word))
    global highlighted_windows
    nick = colored_nick(word[0])
    objective = word[1]
    objective_nick, objective_username, objective_host = user_fields_extractor(objective)

    printout = '*\t' + nick + ' sets exempt on ' + \
               objective_nick + '!' + objective_username + '@' + objective_host

    hexchat.prnt(printout)
    my_nick, my_username, my_host = my_nick_host()
    my_user = f'{my_nick}!{my_username}@{my_host}'
    if search(objective.replace('\\', '\\\\').replace('.', '\.').replace('?', '.').replace('*', '.*').replace('[', '\[').replace('|', '\|'), my_user):
        hexchat.command('GUI COLOR 3')
        connection_id = hexchat.get_prefs('id')
        channel = hexchat.get_info('channel')
        highlighted_window = (connection_id, channel)
        if (highlighted_window not in highlighted_windows) & (highlighted_window != focused_tab):
            highlighted_windows.append(highlighted_window)
        if (hexchat.get_info('away') is None) | (hexchat.get_prefs('away_omit_alerts') == 0):
            hexchat.command('SPLAY ' + sound_file)
    return hexchat.EAT_HEXCHAT


def channel_remove_exempt(word, word_eol, userdata):
    # /MODE #channel -e objective
    # hexchat.prnt('Channel Remove Exempt')
    # hexchat.prnt(', '.join(word))
    global highlighted_windows
    nick = colored_nick(word[0])
    objective = word[1]
    objective_nick, objective_username, objective_host = user_fields_extractor(objective)

    printout = '*\t' + nick + ' removes exempt on ' + \
               objective_nick + '!' + objective_username + '@' + objective_host

    hexchat.prnt(printout)
    my_nick, my_username, my_host = my_nick_host()
    my_user = f'{my_nick}!{my_username}@{my_host}'
    if search(objective.replace('\\', '\\\\').replace('.', '\.').replace('?', '.').replace('*', '.*').replace('[', '\[').replace('|', '\|'), my_user):
        hexchat.command('GUI COLOR 3')
        connection_id = hexchat.get_prefs('id')
        channel = hexchat.get_info('channel')
        highlighted_window = (connection_id, channel)
        if (highlighted_window not in highlighted_windows) & (highlighted_window != focused_tab):
            highlighted_windows.append(highlighted_window)
        if (hexchat.get_info('away') is None) | (hexchat.get_prefs('away_omit_alerts') == 0):
            hexchat.command('SPLAY ' + sound_file)
    return hexchat.EAT_HEXCHAT


# 1.9. Notify
def add_notify(word, word_eol, userdata):
    # hexchat.prnt('Add Notify')
    # hexchat.prnt(', '.join(word))
    nick = colored_nick(word[0])

    printout = '*\t' + nick + ' added to notify list'

    context = server_context(hexchat.get_prefs('id'))
    context.prnt(printout)
    return hexchat.EAT_HEXCHAT


def delete_notify(word, word_eol, userdata):
    # hexchat.prnt('Delete Notify')
    # hexchat.prnt(', '.join(word))
    nick = colored_nick(word[0])

    printout = '*\t' + nick + ' deleted from notify list'

    context = server_context(hexchat.get_prefs('id'))
    context.prnt(printout)
    return hexchat.EAT_HEXCHAT


def notify_online(word, word_eol, userdata):
    # hexchat.prnt('Notify Online')
    # hexchat.prnt(', '.join(word))
    nick = colored_nick(word[0])

    printout = '*\tNotify: ' + nick + ' is online'

    context = server_context(hexchat.get_prefs('id'))
    context.prnt(printout)
    context.command('GUI COLOR 3')
    if (hexchat.get_info('away') is None) | (hexchat.get_prefs('away_omit_alerts') == 0):
        hexchat.command('SPLAY ' + sound_file)
    return hexchat.EAT_HEXCHAT


def notify_offline(word, word_eol, userdata):
    # hexchat.prnt('Notify Offline')
    # hexchat.prnt(', '.join(word))
    nick = colored_nick(word[0])

    printout = '*\tNotify: ' + nick + ' is offline'

    context = server_context(hexchat.get_prefs('id'))
    context.prnt(printout)
    context.command('GUI COLOR 2')
    if (hexchat.get_info('away') is None) | (hexchat.get_prefs('away_omit_alerts') == 0):
        hexchat.command('SPLAY ' + sound_file)
    return hexchat.EAT_HEXCHAT


def notify_away(word, word_eol, userdata):
    # hexchat.prnt('Notify Away')
    # hexchat.prnt(', '.join(word))
    nick = colored_nick(word[0])
    reason = hexchat.strip(word[1])

    printout = '*\tNotify: ' + nick + ' is away (' + reason + ')'

    context = server_context(hexchat.get_prefs('id'))
    context.prnt(printout)
    context.command('GUI COLOR 2')
    if (hexchat.get_info('away') is None) | (hexchat.get_prefs('away_omit_alerts') == 0):
        hexchat.command('SPLAY ' + sound_file)
    return hexchat.EAT_HEXCHAT


def notify_back(word, word_eol, userdata):
    # hexchat.prnt('Notify Back')
    # hexchat.prnt(', '.join(word))
    nick = colored_nick(word[0])

    printout = '*\tNotify: ' + nick + ' is back'

    context = server_context(hexchat.get_prefs('id'))
    context.prnt(printout)
    context.command('GUI COLOR 3')
    if (hexchat.get_info('away') is None) | (hexchat.get_prefs('away_omit_alerts') == 0):
        hexchat.command('SPLAY ' + sound_file)
    return hexchat.EAT_HEXCHAT


# 1.10 Ignore
def ignore_add(word, word_eol, userdata):
    # hexchat.prnt('Ignore Add')
    # hexchat.prnt(', '.join(word))
    nick, username, host = user_fields_extractor(word[0])
    if bool(username) & bool(host):
        user = nick + '!' + username + '@' + host
    else:
        user = nick

    printout = '*\t' + user + ' added to ignore list'

    context = server_context(hexchat.get_prefs('id'))
    context.prnt(printout)
    return hexchat.EAT_HEXCHAT


def ignore_changed(word, word_eol, userdata):
    # hexchat.prnt('Ignore Changed')
    # hexchat.prnt(', '.join(word))
    nick, username, host = user_fields_extractor(word[0])
    if bool(username) & bool(host):
        user = nick + '!' + username + '@' + host
    else:
        user = nick

    printout = '*\tignore on ' + user + ' changed'

    context = server_context(hexchat.get_prefs('id'))
    context.prnt(printout)
    return hexchat.EAT_HEXCHAT


def ignore_remove(word, word_eol, userdata):
    # hexchat.prnt('Ignore Remove')
    # hexchat.prnt(', '.join(word))
    nick, username, host = user_fields_extractor(word[0])
    if bool(username) & bool(host):
        user = nick + '!' + username + '@' + host
    else:
        user = nick

    printout = '*\t' + user + ' removed from ignore list'

    context = server_context(hexchat.get_prefs('id'))
    context.prnt(printout)
    return hexchat.EAT_HEXCHAT


# 1.11. CTCP
def ctcp_send(word, word_eol, userdata):
    # Send a CTCP SOUND (the sound must be located in recipient sound directory /home/user/.config/hexchat/sounds/):
    # /CTCP recipient SOUND sound_file
    # hexchat.prnt('CTCP Send')
    # hexchat.prnt(', '.join(word))
    recipient = word[0]
    if recipient[0] != '#':
        recipient = colored_nick(recipient)
    ctcp = hexchat.strip(word[1])

    printout = '*\tCTCP sent to ' + recipient + ': ' + ctcp

    context = server_context(hexchat.get_prefs('id'))
    context.prnt(printout)
    return hexchat.EAT_HEXCHAT


def ctcp_generic(word, word_eol, userdata):
    # hexchat.prnt('CTCP Generic')
    # hexchat.prnt(', '.join(word))
    nick = colored_nick(word[1])
    ctcp = hexchat.strip(word[0])

    printout = '*\tReceived a CTCP from ' + nick + ': ' + ctcp

    context = server_context(hexchat.get_prefs('id'))
    context.prnt(printout)
    context.command('GUI COLOR 2')
    if (hexchat.get_info('away') is None) | (hexchat.get_prefs('away_omit_alerts') == 0):
        hexchat.command('SPLAY ' + sound_file)
    return hexchat.EAT_HEXCHAT


def ctcp_generic_to_channel(word, word_eol, userdata):
    # hexchat.prnt('CTCP Generic to Channel')
    # hexchat.prnt(', '.join(word))
    nick = colored_nick(word[1])
    ctcp = hexchat.strip(word[0])

    printout = '*\tReceived a CTCP from ' + nick + ': ' + ctcp

    hexchat.prnt(printout)
    hexchat.command('GUI COLOR 2')
    return hexchat.EAT_HEXCHAT


def ctcp_sound(word, word_eol, userdata):
    # hexchat.prnt('CTCP Sound')
    # hexchat.prnt(', '.join(word))
    nick = colored_nick(word[1])
    ctcp = word[0]

    printout = '*\tReceived a CTCP SOUND from ' + nick + ': ' + ctcp

    context = server_context(hexchat.get_prefs('id'))
    context.prnt(printout)
    context.command('GUI COLOR 2')
    return hexchat.EAT_ALL


def ctcp_sound_to_channel(word, word_eol, userdata):
    # hexchat.prnt('CTCP Sound to Channel')
    # hexchat.prnt(', '.join(word))
    nick = colored_nick(word[1])
    channel = word[2]
    ctcp = word[0]

    printout = '*\tReceived a CTCP SOUND from ' + nick + ': ' + ctcp

    hexchat.prnt(printout)
    hexchat.command('GUI COLOR 2')
    return hexchat.EAT_ALL


# 1.12. DCC
def dcc_send_connect(word, word_eol, userdata):
    # /DCC SEND nick file
    # hexchat.prnt('DCC SEND Connect')
    # hexchat.prnt(', '.join(word))
    nick = colored_nick(word[0])
    ip = word[1]

    printout = '*\tDCC SEND connection established to ' + nick + ' [' + ip + ']'

    hexchat.prnt(printout)
    return hexchat.EAT_HEXCHAT


def dcc_chat_connect(word, word_eol, userdata):
    # hexchat.prnt('DCC CHAT Connect')
    # hexchat.prnt(', '.join(word))
    nick = colored_nick(word[0])
    ip = word[1]

    printout = '*\tDCC CHAT connection established to ' + nick + ' [' + ip + ']'

    hexchat.prnt(printout)
    return hexchat.EAT_HEXCHAT


def dcc_recv_connect(word, word_eol, userdata):
    # hexchat.prnt('DCC RECV Connect')
    # hexchat.prnt(', '.join(word))
    nick = colored_nick(word[0])
    ip = word[1]

    printout = '*\tDCC RECV connection established to ' + nick + ' [' + ip + ']'

    hexchat.prnt(printout)
    return hexchat.EAT_HEXCHAT


def dcc_connection_failed(word, word_eol, userdata):
    # hexchat.prnt('DCC Conection Failed')
    # hexchat.prnt(', '.join(word))
    dcc = word[0]
    nick = colored_nick(word[1])
    error = word[2]

    printout = '*\tDCC ' + dcc + ' connect attempt to ' + nick + ' failed (' + error + ')'

    hexchat.prnt(printout)
    return hexchat.EAT_HEXCHAT


def dcc_send_offer(word, word_eol, userdata):
    # hexchat.prnt('DCC SEND Offer')
    # hexchat.prnt(', '.join(word))
    nick = colored_nick(word[0])
    dcc = word[1]
    dcc_bytes = word[2]
    ip = word[3]

    printout = '*\t' + nick + ' has offered "' + dcc + '" (' + dcc_bytes + ' bytes)' + ' [' + ip + ']'

    hexchat.prnt(printout)
    return hexchat.EAT_HEXCHAT


def dcc_offer(word, word_eol, userdata):
    # /DCC SEND nick file
    # hexchat.prnt('DCC Offer')
    # hexchat.prnt(', '.join(word))
    nick = colored_nick(word[1])
    dcc = word[0]

    printout = '*\tOffering to ' + nick + ': "' + dcc + '"'

    hexchat.prnt(printout)
    return hexchat.EAT_HEXCHAT


def dcc_chat_offer(word, word_eol, userdata):
    # /DCC CHAT nick
    # hexchat.prnt('DCC CHAT Offer')
    # hexchat.prnt(', '.join(word))
    nick = colored_nick(word[0])

    printout = '*\tReceived a DCC CHAT offer from ' + nick

    hexchat.prnt(printout)
    return hexchat.EAT_HEXCHAT


def dcc_generic_offer(word, word_eol, userdata):
    # hexchat.prnt('DCC Generic Offer')
    # hexchat.prnt(', '.join(word))
    nick = colored_nick(word[1])
    dcc = word[0]

    printout = '*\tReceived from ' + nick + ': "' + dcc + '"'

    hexchat.prnt(printout)
    return hexchat.EAT_HEXCHAT


def dcc_chat_offering(word, word_eol, userdata):
    # /DCC CHAT nick
    # hexchat.prnt('DCC CHAT Offering')
    # hexchat.prnt(', '.join(word))
    nick = colored_nick(word[0])

    printout = '*\tOffering DCC CHAT to ' + nick

    hexchat.prnt(printout)
    return hexchat.EAT_HEXCHAT


def dcc_chat_re_offer(word, word_eol, userdata):
    # /DCC CHAT nick (two or more times)
    # hexchat.prnt('DCC CHAT Reoffer')
    # hexchat.prnt(', '.join(word))
    nick = colored_nick(word[0])

    printout = '*\tAlready offering DCC CHAT to ' + nick

    hexchat.prnt(printout)
    return hexchat.EAT_HEXCHAT


def dcc_resume_request(word, word_eol, userdata):
    # hexchat.prnt('DCC RESUME Request')
    # hexchat.prnt(', '.join(word))
    nick = colored_nick(word[0])
    dcc = word[1]
    position = word[2]

    printout = '*\t' + nick + ' has requested to resume "' + dcc + '" from ' + position

    hexchat.prnt(printout)
    return hexchat.EAT_HEXCHAT


def dcc_send_complete(word, word_eol, userdata):
    # hexchat.prnt('DCC SEND Complete')
    # hexchat.prnt(', '.join(word))
    nick = colored_nick(word[1])
    dcc = word[0]
    cps = word[2]

    printout = '*\tDCC SEND to ' + nick + ' completed: "' + dcc + '" (' + cps + ' cps)'

    hexchat.prnt(printout)
    return hexchat.EAT_HEXCHAT


def dcc_recv_complete(word, word_eol, userdata):
    # hexchat.prnt('DCC RECV Complete')
    # hexchat.prnt(', '.join(word))
    nick = colored_nick(word[2])
    dcc = word[0]
    cps = word[3]

    printout = '*\tDCC RECV from ' + nick + ' completed: "' + dcc + '" (' + cps + ' cps)'

    hexchat.prnt(printout)
    return hexchat.EAT_HEXCHAT


def dcc_send_abort(word, word_eol, userdata):
    # hexchat.prnt('DCC SEND Abort')
    # hexchat.prnt(', '.join(word))
    nick = colored_nick(word[0])
    dcc = word[1]

    printout = '*\tDCC SEND to ' + nick + ' ("' + dcc + '") aborted'

    hexchat.prnt(printout)
    return hexchat.EAT_HEXCHAT


def dcc_chat_abort(word, word_eol, userdata):
    # /DCC CLOSE CHAT nick
    # hexchat.prnt('DCC CHAT Abort')
    # hexchat.prnt(', '.join(word))
    nick = colored_nick(word[0])

    printout = '*\tDCC CHAT to ' + nick + ' aborted'

    hexchat.prnt(printout)
    return hexchat.EAT_HEXCHAT


def dcc_recv_abort(word, word_eol, userdata):
    # hexchat.prnt('DCC RECV Abort')
    # hexchat.prnt(', '.join(word))
    nick = colored_nick(word[0])
    dcc = word[1]

    printout = '*\tDCC RECV to ' + nick + ' ("' + dcc + '") aborted'

    hexchat.prnt(printout)
    return hexchat.EAT_HEXCHAT


def dcc_send_failed(word, word_eol, userdata):
    # hexchat.prnt('DCC SEND Failed')
    # hexchat.prnt(', '.join(word))
    nick = colored_nick(word[1])
    dcc = word[0]
    error = word[2]

    printout = '*\tDCC SEND to ' + nick + ' ("' + dcc + '") failed (' + error + ')'

    hexchat.prnt(printout)
    return hexchat.EAT_HEXCHAT


def dcc_chat_failed(word, word_eol, userdata):
    # hexchat.prnt('DCC CHAT Failed')
    # hexchat.prnt(', '.join(word))
    nick = colored_nick(word[0])
    ip = word[1]
    error = word[3]

    printout = '*\tDCC CHAT to ' + nick + ' [' + ip + '] lost (' + error + ')'

    hexchat.prnt(printout)
    return hexchat.EAT_HEXCHAT


def dcc_recv_failed(word, word_eol, userdata):
    # hexchat.prnt('DCC RECV Failed')
    # hexchat.prnt(', '.join(word))
    nick = colored_nick(word[2])
    dcc = word[0]
    error = word[3]

    printout = '*\tDCC RECV from ' + nick + ' ("' + dcc + '") failed (' + error + ')'

    hexchat.prnt(printout)
    return hexchat.EAT_HEXCHAT


def dcc_malformed(word, word_eol, userdata):
    # hexchat.prnt('DCC Malformed')
    # hexchat.prnt(', '.join(word))
    nick = colored_nick(word[0])
    dcc = word[1]

    printout = '*\tReceived a malformed DCC request from ' + nick + '$a010* Contents of packet: ' + dcc

    hexchat.prnt(printout)
    return hexchat.EAT_HEXCHAT


def dcc_stall(word, word_eol, userdata):
    # hexchat.prnt('DCC Stall')
    # hexchat.prnt(', '.join(word))
    nick = colored_nick(word[2])
    dcc_type = word[0]
    dcc = word[1]

    printout = '*\tDCC ' + dcc_type + ' to ' + nick + ' ("' + dcc + '") stalled, aborting'

    hexchat.prnt(printout)
    return hexchat.EAT_HEXCHAT


def dcc_timeout(word, word_eol, userdata):
    # hexchat.prnt('DCC Timeout')
    # hexchat.prnt(', '.join(word))
    nick = colored_nick(word[2])
    dcc_type = word[0]
    dcc = word[1]

    printout = '*\tDCC ' + dcc_type + ' to ' + nick + ' ("' + dcc + '") timed out, aborting'

    hexchat.prnt(printout)
    return hexchat.EAT_HEXCHAT


def focus_tab(word, word_eol, userdata):
    global highlighted_windows, focused_tab
    connection_id = hexchat.get_prefs('id')
    channel = hexchat.get_info('channel')
    focused_tab = (connection_id, channel)

    if focused_tab in highlighted_windows:
        highlighted_windows.remove(focused_tab)

    return hexchat.EAT_NONE


# 2. Hook creation for every text event
# 2.1. Server
hexchat.hook_print('Resolving User', resolving_user)
hexchat.hook_print('SASL Authenticating', sasl_authenticating)
hexchat.hook_print('Ping Reply', ping_reply)
hexchat.hook_print('Server Text', server_text)

# 2.2. Messages
hexchat.hook_print('Your Message', your_message)
hexchat.hook_print('Channel Message', channel_message)
hexchat.hook_print('Channel Msg Hilight', channel_message_highlight)
hexchat.hook_print('Message Send', message_send)
hexchat.hook_print('Private Message to Dialog', private_message_to_dialog)
hexchat.hook_print('Private Message', private_message)
hexchat.hook_print('Receive Wallops', receive_wallops)

# 2.3. Actions
hexchat.hook_print('Your Action', your_action)
hexchat.hook_print('Channel Action', channel_action)
hexchat.hook_print('Channel Action Hilight', channel_action_highlight)
hexchat.hook_print('Private Action to Dialog', private_action_to_dialog)
hexchat.hook_print('Private Action', private_action)

# 2.4. Notices
hexchat.hook_print('Notice Send', notice_send)
hexchat.hook_print('Channel Notice', channel_notice)
hexchat.hook_print('Notice', notice)

# 2.5. Nick
hexchat.hook_print('Channel Mode Generic', channel_mode_generic)
hexchat.hook_print('Raw Modes', raw_modes)
hexchat.hook_print('Your Nick Changing', your_nick_changing)
hexchat.hook_print('Change Nick', change_nick)
hexchat.hook_print('Nick Clash', nick_clash)
hexchat.hook_print('Nick Erroneous', nick_erroneous)
hexchat.hook_print('Killed', killed)

# 2.6. Whois
hexchat.hook_print('Whois Name Line', whois_name_line)
hexchat.hook_print('Whois Real Host', whois_real_host)
hexchat.hook_print('Whois Channel/Oper Line', whois)
hexchat.hook_print('Whois Server Line', whois)
hexchat.hook_print('Whois Authenticated', whois_authenticated)
hexchat.hook_print('Whois Identified', whois)
hexchat.hook_print('Whois Special', whois)
hexchat.hook_print('Whois Away Line', whois_away_line)
hexchat.hook_print('Whois Idle Line', whois_idle_line)
hexchat.hook_print('Whois Idle Line with Signon', whois_idle_line_with_signed_on)
hexchat.hook_print('Whois End', whois_end)

# 2.7. Join, part, quit
hexchat.hook_print('You Join', you_join)
hexchat.hook_print('Join', join)
hexchat.hook_print('You Part', you_part)
hexchat.hook_print('You Part with Reason', you_part_with_reason)
hexchat.hook_print('Part', part)
hexchat.hook_print('Part with Reason', part_with_reason)
hexchat.hook_print('Quit', hexchat_quit)

# 2.8. Channels
hexchat.hook_print('Topic Creation', topic_creation)
hexchat.hook_print('Topic Change', topic_change)
hexchat.hook_print('Channel Voice', channel_voice)
hexchat.hook_print('Channel DeVoice', channel_de_voice)
hexchat.hook_print('Channel Operator', channel_operator)
hexchat.hook_print('Channel DeOp', channel_de_op)
hexchat.hook_print('Channel Half-Operator', channel_half_operator)
hexchat.hook_print('Channel DeHalfOp', channel_de_half_op)
hexchat.hook_print('Your Invitation', your_invitation)
hexchat.hook_print('Invited', invited)
hexchat.hook_print('Invited Other', invited_other)
hexchat.hook_print('Channel INVITE', channel_invite)
hexchat.hook_print('Channel Remove Invite', channel_remove_invite)
hexchat.hook_print('Channel Set Key', channel_set_key)
hexchat.hook_print('Channel Remove Keyword', channel_remove_keyword)
hexchat.hook_print('Channel Set Limit', channel_set_limit)
hexchat.hook_print('Channel Remove Limit', channel_remove_limit)
hexchat.hook_print('Channel Quiet', channel_quiet)
hexchat.hook_print('Channel UnQuiet', channel_unquiet)
hexchat.hook_print('Channel Ban', channel_ban)
hexchat.hook_print('Channel UnBan', channel_unban)
hexchat.hook_print('Ban List', ban_list)
hexchat.hook_print('You Kicked', you_kicked)
hexchat.hook_print('Kick', kick)
hexchat.hook_print('Channel Exempt', channel_exempt)
hexchat.hook_print('Channel Remove Exempt', channel_remove_exempt)

# 2.9. Notify
hexchat.hook_print('Add Notify', add_notify)
hexchat.hook_print('Delete Notify', delete_notify)
hexchat.hook_print('Notify Online', notify_online)
hexchat.hook_print('Notify Offline', notify_offline)
hexchat.hook_print('Notify Away', notify_away)
hexchat.hook_print('Notify Back', notify_back)

# 2.10. Ignore
hexchat.hook_print('Ignore Add', ignore_add)
hexchat.hook_print('Ignore Changed', ignore_changed)
hexchat.hook_print('Ignore Remove', ignore_remove)

# 2.11. CTCP
hexchat.hook_print('CTCP Send', ctcp_send)
hexchat.hook_print('CTCP Generic', ctcp_generic)
hexchat.hook_print('CTCP Generic to Channel', ctcp_generic_to_channel)
hexchat.hook_print('CTCP Sound', ctcp_sound)
hexchat.hook_print('CTCP Sound to Channel', ctcp_sound_to_channel)

# 2.12. DCC
hexchat.hook_print('DCC SEND Connect', dcc_send_connect)
hexchat.hook_print('DCC CHAT Connect', dcc_chat_connect)
hexchat.hook_print('DCC RECV Connect', dcc_recv_connect)
hexchat.hook_print('DCC Conection Failed', dcc_connection_failed)
hexchat.hook_print('DCC SEND Offer', dcc_send_offer)
hexchat.hook_print('DCC Offer', dcc_offer)
hexchat.hook_print('DCC CHAT Offer', dcc_chat_offer)
hexchat.hook_print('DCC Generic Offer', dcc_generic_offer)
hexchat.hook_print('DCC CHAT Offering', dcc_chat_offering)
hexchat.hook_print('DCC CHAT Reoffer', dcc_chat_re_offer)
hexchat.hook_print('DCC RESUME Request', dcc_resume_request)
hexchat.hook_print('DCC SEND Complete', dcc_send_complete)
hexchat.hook_print('DCC RECV Complete', dcc_recv_complete)
hexchat.hook_print('DCC SEND Abort', dcc_send_abort)
hexchat.hook_print('DCC CHAT Abort', dcc_chat_abort)
hexchat.hook_print('DCC RECV Abort', dcc_recv_abort)
hexchat.hook_print('DCC SEND Failed', dcc_send_failed)
hexchat.hook_print('DCC CHAT Failed', dcc_chat_failed)
hexchat.hook_print('DCC RECV Failed', dcc_recv_failed)
hexchat.hook_print('DCC Malformed', dcc_malformed)
hexchat.hook_print('DCC Stall', dcc_stall)
hexchat.hook_print('DCC Timeout', dcc_timeout)

# Focus window
hexchat.hook_print('Focus Tab', focus_tab)


print(__module_name__, 'loaded')

