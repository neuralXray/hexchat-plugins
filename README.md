# HexChat Python plugins

Collection of HexChat python plugins.


## Installation

```
mkdir hexchat-plugins
cd hexchat-plugins
git clone git clone https://github.com/neuralXray/hexchat-plugins.git
```


## Plugins

### anti_pm

Ignore private messages from every nick that send you a private message.

#### Commands

* `antipmex nick`: Add nick to the white list, nicks to not ignore.

* `antipmexrm nick`: Remove nick from the white list.

anti_pm.config

* line 1: text automatically sent to the nick that first sends you a private message and that you instantly ignore.

* line 2: text to automatically send, when you stop ignoring a nick, to him.

* line 3: list of comma separated nicks to not ignore.


### away

Notice nick mentions if away.


### chan

Automated & hidden operator actions.

#### Commands

* `commandc nick`: equivalent as `msg CHaN command channel nick` for commandc = `voicec`, `devoice`, `opc`, `deopc`.

* `exempt`: equivalent as `mode e`, show (ban, mode b) exempt list.

* `exempt mask`: equivalent as `mode e mask`, set (ban) exemption on mask.

* `unexempt mask`: equivalent as `mode -e mask`, remove exemption from mask.

* `exemptme`: set exemptions on me.

* `akick mask`: set akick to mask.

* `rmakick mask`: remove akick to mask.

* `listakick`: list akisks.


### clones_channels




### colored_nicks




### identify




### join




### karaoke




### karaoke_publicly_accesible




### nicks_channels




### raw_log




### update




### who_was_joined




### Support the developer

* Bitcoin: 1GDDJ7sLcBwFXg978qzCdsxrC8Ci9Dbgfa
* Monero: 4BGpHVqEWBtNwhwE2FECSt6vpuDMbLzrCFSUJHX5sPG44bZQYK1vN8MM97CbyC9ejSHpJANpJSLpxVrLQ2XT6xEXR8pzdCT
* Litecoin: LdaMXYuayfQmEQ4wsgR2Tp6om78caG3TEG
* Ethereum: 0x7862D03Dd9Dd5F1ebc020B2AaBd107d872ebA58E
* PayPal: paypal.me/neuralXray

