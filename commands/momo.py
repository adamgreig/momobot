# -*- coding: utf-8 -*-

class Momo:
    def __init__(self, bot):
        self.bot = bot
        bot.register_command('momo', self.momo)
    
    def momo(self, data):
        self.bot.irc.act('throws Momo on %s!' % data['message'])