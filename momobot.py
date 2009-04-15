# -*- coding: utf-8 -*-
"""
The main bot file
"""

import settings
import irc

myirc = irc.IRC(settings.SERVER, settings.PORT, settings.USERNAME)
myirc.join(settings.CHANNEL)

def public_message(data):
    print "Got a public message: ",
    print data

myirc.register_callback('channel_message', public_message)

while True:
    myirc.read()