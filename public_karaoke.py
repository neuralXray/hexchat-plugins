# -*- coding: UTF-8 -*-

__module_name__ = 'Public Karaoke'
__module_version__ = '1.0'
__module_description__ = 'Publicly accessible karaoke.'


import hexchat

import sys
sys.path.insert(0, hexchat.get_info('configdir') + '/addons/utils')
from hexchat_utils import colored_nicks_loaded

from threading import Thread
from random import choice, uniform
from time import sleep
from datetime import datetime
from os import walk, getenv
from re import search


user_name = getenv('USER')
music_directory = '/home/' + user_name + '/Music/'

start_regex = '^\[[0-9]{2}\:[0-9]{2}\.[0-9]{2,3}\]'
lyric_time_format = '%M:%S.%f'

minutes_regex = '^\[[0-9]{2}\:'
seconds_regex = ':[0-9]{2}\.[0-9]{2,3}\]'
start_regex = minutes_regex + seconds_regex[1:]

busy = False

is_colored_nicks_loaded = colored_nicks_loaded()


lyrics_directories = []
for root, dirs, files in walk(music_directory):
    for file in files:
        if file.endswith('.lrc'):
            lyrics_directories.append(root + '/' + file)


def get_lyrics_path(channel, song_search):
    global busy
    busy = True
    results = []

    for lyrics_directory in lyrics_directories:
        if song_search in lyrics_directory.lower():
            results.append(lyrics_directory)

    if len(results) < 6:
        for result in results:
            hexchat.command('msg ' + channel + ' ' + result)
            sleep(2)
    elif len(results) == 0:
        hexchat.command('msg ' + channel + " I don't have this song")
    else:
        hexchat.command('msg ' + channel + \
                        ' to many results, send a more specific search')

    busy = False


def send(channel, song_path):
    global busy
    busy = True
    for lyrics_directory in lyrics_directories:
        if song_path == lyrics_directory:
            lines = open(song_path).readlines()
            lyric_time_start = 0

            hexchat.command('msg ' + channel + ' ' + song_path[song_path.rindex('/') + 1:])
            sleep(2)
            hexchat.command('msg ' + channel + ' ' + '3...')
            sleep(2)
            hexchat.command('msg ' + channel + ' ' + '2...')
            sleep(2)
            hexchat.command('msg ' + channel + ' ' + '1...')
            sleep(2)
            hexchat.command('msg ' + channel + ' ' + 'Play!')

            for line in lines:
                start = search(start_regex, line)
                if start:
                    minutes = search(minutes_regex, line).group()[1:-1]
                    seconds = search(seconds_regex, line).group()[1:-1]

                    lyric_time_end = float(minutes)*60 + float(seconds)

                    lyric_time = lyric_time_end - lyric_time_start
                    lyric_time_start = lyric_time_end

                    lyric = line[start.span()[1]:-1]

                    sleep(lyric_time)
                    if lyric:
                        hexchat.command('msg ' + channel + ' ' + lyric)

            break
    busy = False


def help(channel):
    global busy
    busy = True
    hexchat.command('msg ' + channel + ' ' + 'Display synchronized song lyrics')
    sleep(2)
    hexchat.command('msg ' + channel + ' ' + '.lyrics_path/lp <song to search>')
    sleep(2)
    hexchat.command('msg ' + channel + ' ' + \
                    '.lyrics/l <song path returned by previous command>')
    busy = False


def message(word, word_eol, userdata):
    if not busy:
        message = hexchat.strip(word[1])
        channel = hexchat.get_info('channel')

        if message.startswith('.lyrics_path') or message.startswith('.lp'):
            song_search = message[len('.get_lyrics_path') + 1:]
            Thread(target=get_lyrics_path, args=(channel, song_search,)).start()

        elif message.startswith('.lyrics') or message.startswith('.l'):
            song_path = message[len('.get_lyrics') + 1:]
            Thread(target=send, args=(channel, song_path,)).start()

        elif message.startswith('.help'):
            Thread(target=help, args=(channel,)).start()

    if is_colored_nicks_loaded:
        return hexchat.EAT_HEXCHAT
    else:
        return hexchat.EAT_NONE


hexchat.hook_print('Channel Message', message)
hexchat.hook_print('Channel Msg Hilight', message)
hexchat.hook_print('Channel Action', message)
hexchat.hook_print('Channel Action Hilight', message)


print(__module_name__, 'loaded')

