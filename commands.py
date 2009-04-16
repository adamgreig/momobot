# -*- coding: utf-8 -*-
"""
All the actual bot commands
"""

class Commands:
    def __init__(self, bot):
        self.bot = bot
        bot.register_command('hello', self.hello)
        bot.register_command('momo', self.momo)
        bot.irc.register_callback('channel_join', self.join)
    
    def hello(self, bot, data):
        bot.irc.say('Hello, %s!' % data['username'])
    
    def momo(self, bot, data):
        bot.irc.act('throws Momo on %s!' % data['message'])
    
    def join(self, data):
        if data['username'] != self.bot.nickname:
            self.bot.irc.say(
                'Welcome to %s, %s!' % (data['channel'], data['username']),
                data['channel'])