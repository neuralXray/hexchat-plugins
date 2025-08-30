# HexChat Python Plugins

A collection of HexChat plugins written in Python.


## Installation commands

```
cd ~/.config/hexchat/addons
git clone https://github.com/neuralXray/hexchat-plugins.git
mv hexchat-plugins/* .
git clone https://github.com/neuralXray/irc-nicks-channels.git
mv irc-nicks-channels/utils.py .
rm -rf hexchat-plugins irc-nicks-channels
mkdir utils
mv update.py hexchat_utils.py utils.py utils
```


## Plugins

### 1. Colored Nicks

Colorize nicks in all text events.


### 2. Anti private messages

Automatically ignore private messages from a user who initiates a private conversation after receiving their first message.

#### Commands

* `antipmex <nick>`: Add nick to the white list.

* `antipmexrm <nick>`: Remove nick from the white list.

#### Configuration file

Edit the `anti_pm.config` file. Each line contains:

1. The message to automatically send to a user that talks to you first in private.

2. The message to automatically send when you stop ignoring a user.

3. A comma-separated list of nicks to not ignore.


### 3. Away

Send a single NOTICE to users who mention you or send you a private message while you are marked as away.


#### Configuration file

Write a comma-separated list of nicks who won't receive an away notice in the first line of the `away.config` file.


### 4. CHaN

Automated and hidden channel operator actions.

#### Commands

* `<command>c <nick>`: equivalent to `msg CHaN <command> <#channel> <nick>` for `voice`, `devoice`, `op`, `deop` commands.

* `exempt`: equivalent to `mode e`, show the ban (mode b) exempt list.

* `exempt <mask>`: equivalent to `mode e <mask>`, set a ban exemption on a mask.

* `unexempt <mask>`: equivalent to `mode -e <mask>`, remove an exemption from mask.

* `exemptme`: set exemptions on me.

* `akick <mask>`: set auto-kick on a mask.

* `rmakick <mask>`: remove auto-kick from a mask.

* `listakick`: list auto-kicks.

#### Configuration file

Edit `chan.config` file following the template.

* Line 1: The server address and the nick with access.

* Line 2: The channels which the nick has access to in the server.

Write on the third line the next server address and nick, and the corresponding channels on the fourth line. Repeat as needed.


### 5. Find clones and channels

Find users with the same IP and common channels after a `WHOIS` command.


### 6. Identify

Automatically identify with password.

#### Configuration file

Edit the `identify.config` file with the server address, nick, and password separated by commas. If needed, configure more nicks, each one on a new line.


### 7. JOIN

JOIN to several channels with one command.

#### Commands

* `join/j <#channel1> <#channel2>`


### 8. Karaoke

Karaoke.

#### Commands

* `lyrics_path/lp <search>`: find lyrics path.

* `lyrics/l <lyrics path>`: send lyrics from a file to the current context.


### 9. Public karaoke

Publicly accessible karaoke. The commands are the same as those for the karaoke plugin, but are received from other users' channel messages when preceded by a dot. To enable the control of the karaoke via channel messages, execute `public_karaoke/pk on`. To disable it, execute `public_karaoke/pk off`. By default, it's disabled.


### 10. Find nicks and channels

Find nicks with the same IP or ident, along with visited channels, and first and last seen datetime.

#### Commands

* `search <nick>!<ident>@<IP> [months=1]`: execute search.


### 11. Raw logger

Log raw server events


### 12. WHO was JOINed

Log who were joined.


### 13. Update

Features:

* Rename the colors file to update the HexChat theme according to the system theme.

* Update nickname, username, and realname with randomized strings only on specified networks and in global configuration. The nickname and username are the same.
    * Nickname and realname format: Guest[0-9]{4}
    * Username format: [a-zA-Z][a-zA-Z0-9]{8}

#### Configuration file

Write a comma-separated list of the network names where the configuration will be updated in the file `update.config`.

 Change the HexChat launcher command to `bash -c 'python3 ~/.config/hexchat/addons/utils/update.py && hexchat --existing %U'` to update the configuration every time you start HexChat.


### Support the developer

* Bitcoin: 1GDDJ7sLcBwFXg978qzCdsxrC8Ci9Dbgfa
* Monero: 4BGpHVqEWBtNwhwE2FECSt6vpuDMbLzrCFSUJHX5sPG44bZQYK1vN8MM97CbyC9ejSHpJANpJSLpxVrLQ2XT6xEXR8pzdCT
* Litecoin: LdaMXYuayfQmEQ4wsgR2Tp6om78caG3TEG
* Ethereum: 0x7862D03Dd9Dd5F1ebc020B2AaBd107d872ebA58E
* PayPal: paypal.me/neuralXray

