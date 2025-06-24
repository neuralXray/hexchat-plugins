# -*- coding: UTF-8 -*-

__module_name__ = 'Karaoke'
__module_version__ = '1.0'
__module_description__ = 'Karaoke'


import hexchat
from threading import Thread
from random import choice, uniform
from time import sleep
from datetime import datetime
from os import walk, getenv
from re import search


user_name = getenv('USER')
music_directory = '/home/' + user_name + '/Music/'

start_regex = '^\[[0-9]{2}\:[0-9]{2}\.[0-9]{2}\]'
lyric_time_format = '%M:%S.%f'

minutes_regex = '^\[[0-9]{2}\:'
seconds_regex = ':[0-9]{2}\.[0-9]{2}\]'
start_regex = minutes_regex + seconds_regex[1:]


lyrics_directories = []
for root, dirs, files in walk(music_directory):
    for file in files:
        if file.endswith('.lrc'):
            lyrics_directories.append(root + '/' + file)


def get_lyrics_path(word, word_eol, userdata):
    if len(word_eol) > 1:
        song_search = word_eol[1].lower()
        for lyrics_directory in lyrics_directories:
            if song_search in lyrics_directory.lower():
                hexchat.prnt(lyrics_directory)
        return hexchat.EAT_ALL
    else:
        hexchat.prnt('/get_lyrics_path song to search')

def get_lyrics(word, word_eol, userdata):
    channel = word[1]
    song_path = word_eol[2]
    Thread(target=send, args=(channel, song_path,)).start()

    return hexchat.EAT_ALL


def send(channel, song_path):
    for lyrics_directory in lyrics_directories:
        if song_path == lyrics_directory:
            lyric_time_start = 0

            # hexchat.command('msg ' + channel + ' ' + song_path[song_path.rindex('/') + 1:])
            # sleep(2)
            # hexchat.command('msg ' + channel + ' ' + '3...')
            # sleep(2)
            # hexchat.command('msg ' + channel + ' ' + '2...')
            # sleep(2)
            # hexchat.command('msg ' + channel + ' ' + '1...')
            # sleep(2)
            # hexchat.command('msg ' + channel + ' ' + 'Play!')

            for line in open(song_path):
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


hexchat.hook_command('lyrics_path', get_lyrics_path)
hexchat.hook_command('lyrics', get_lyrics)


print(__module_name__, 'loaded')

