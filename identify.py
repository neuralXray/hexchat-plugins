# -*- coding: UTF-8 -*-

__module_name__        = 'Identify'
__module_version__     = '1.0'
__module_description__ = 'Automatically identify with password.'


import hexchat


file = open(hexchat.get_info('configdir') + '/addons/identify.conf')
passwords = {}
for line in file:
    line = line.split(',')
    passwords[(line[0], line[1])] = line[2]
file.close()


def nick_command(word, word_eol, userdata):
    chat = hexchat.get_info('host').lower()
    nick = word[1]

    key = (chat, nick.lower())
    if key in passwords.keys():
        password = passwords[key]
        hexchat.command(f'nick {nick}!{password}')
        return hexchat.EAT_ALL
    else:
        return hexchat.EAT_NONE


hexchat.hook_command('nick', nick_command)


print(__module_name__, 'loaded')

