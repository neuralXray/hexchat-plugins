from os import getenv
from random import randint, choice


# Pending: rename colors file to update HexChat theme accordingly to system theme


user_name = getenv('USER')
directory = '/home/' + user_name + '/.config/hexchat/'
servlist_file = directory + 'servlist.conf'
hexchat_file = directory + 'hexchat.conf'

file = open(directory + '/addons/update.conf')
lines = file.readlines()
file.close()
networks = lines[0].split(',')

mode = 'C=mode'
irc_nick1 = 'irc_nick1 = '
irc_nick2 = 'irc_nick2 = '
irc_nick3 = 'irc_nick3 = '
irc_user_name = 'irc_user_name = '
irc_real_name = 'irc_real_name = '
n_length = 4
ident_length = 9
digits = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']
characters = digits + ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm',
                       'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z',
                       'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M',
                       'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z']


with open(servlist_file) as file:
    lines = file.readlines()

modify = 0
modify_mod = False
chat = 'None'
first = False
with open(servlist_file, 'w') as file:
    for line in lines:
        if first:
            if line[0] == 'I':
                nick = 'Guest'
                for i in range(n_length):
                    nick = nick + choice(digits)
                modified_line = line[:2] + nick + '\n'
                file.write(modified_line)
                #print(chat + ': ' + modified_line)
                modify = modify + 1
                first = False
        elif (modify > 1) & (modify < 5):
            if line[0] == 'i':
                name = 'Guest'
                for i in range(n_length):
                    name = name + choice(digits)
            elif line[0] == 'U':
                name = ''
                for i in range(ident_length):
                    # idents that start with a number are erroneous
                    if name:
                        name = name + choice(characters)
                    else:
                        name = choice(characters[10:])
            else:
                name = nick
            modified_line = line[:2] + name + '\n'
            file.write(modified_line)
            #print(chat + ': ' + modified_line)
            modify = modify + 1
        elif (modify == 5) & ('C=mode' in line) & modify_mod:
            modified_line = mode + ' ' + nick + line[line.rindex(' '):]
            file.write(modified_line)
            #print(chat + ': ' + modified_line)
            modify_mod = False
        else:
            file.write(line)

        if line.startswith('N=') and (line[2:-1] in networks):
            modify_mod = True
            modify = 1
            chat = line[2:-1]
            first = True
        elif line == '\n':
            chat = 'None'
            modify = 0
            first = False


with open(hexchat_file) as file:
    lines = file.readlines()

with open(hexchat_file, 'w') as file:
    for line in lines:
        if line.startswith(irc_nick1):
            nick = 'Guest'
            for i in range(n_length):
                nick = nick + choice(digits)
            modified_line = irc_nick1 + nick + '\n'
            #print(modified_line)
            file.write(modified_line)
        elif line.startswith(irc_nick2):
            name = 'Guest'
            for i in range(n_length):
                name = name + choice(digits)
            modified_line = irc_nick2 + name + '\n'
            #print(modified_line)
            file.write(modified_line)
        elif line.startswith(irc_nick3):
            name = 'Guest'
            for i in range(n_length):
                name = name + choice(digits)
            modified_line = irc_nick3 + name + '\n'
            #print(modified_line)
            file.write(modified_line)
        elif line.startswith(irc_user_name):
            name = ''
            for i in range(ident_length):
                # idents that start with a number are erroneous
                if name:
                    name = name + choice(characters)
                else:
                    name = choice(characters[10:])
            modified_line = irc_user_name + name + '\n'
            #print(modified_line)
            file.write(modified_line)
        elif line.startswith(irc_real_name):
            modified_line = irc_real_name + nick + '\n'
            #print(modified_line)
            file.write(modified_line)
        else:
            file.write(line)

#print('Done!')

