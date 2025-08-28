# -*- coding: UTF-8 -*-

__module_name__        = 'JOIN'
__module_version__     = '1.0'
__module_description__ = 'JOIN to several channels with one command.'


import hexchat


def join_command(word, word_eol, userdata):
    # /join #channel1 #channel2
    # hexchat.prnt('join channels')
    # hexchat.prnt(', '.join(word))

    if len(word) > 2:
        for channel in word[1:]:
            hexchat.command(f'join {channel}')
        return hexchat.EAT_ALL
    else:
        return hexchat.EAT_NONE


hexchat.hook_command('join', join_command)
hexchat.hook_command('j', join_command)


print(__module_name__, 'loaded')

