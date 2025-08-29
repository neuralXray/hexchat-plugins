# -*- coding: UTF-8 -*-

__module_name__        = 'Raw logger'
__module_version__     = '1.0'
__module_description__ = 'Log raw server events.'


import hexchat

from os.path import exists


log_dir = hexchat.get_info('configdir') + '/logs/raw.log'

if not exists(log_dir):
    file = open(log_dir, 'w')
    file.close()


def raw_line(word, word_eol, userdata):
    # hexchat.prnt(', '.join(word))

    file = open(log_dir, 'a')
    file.write(' '.join(word) + '\n')
    file.close()

    return hexchat.EAT_NONE


hexchat.hook_server('RAW LINE', raw_line)


print(__module_name__, 'loaded')

