# -*- coding: utf-8 -*-
"""
All the actual bot commands
"""

class Commands:
    def __init__(self, bot):
        self.bot = bot
        bot.register_command('hello', self.hello)
        bot.register_command('momo', self.momo)
    
    def hello(self, bot, message):
        bot.irc.say('Hello, World!')
    
    def momo(self, bot, message):
        bot.irc.act('throws Momo on %s!' % message)