#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
The main bot file
"""

import settings
import bot

momobot = bot.Bot(settings)

while True:
    try:
        momobot.process()
    except:
        momobot.irc.say('Exception occured.')
