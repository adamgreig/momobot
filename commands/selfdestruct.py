# -*- coding: utf-8 -*-
import random
import string
from time import sleep

class Selfdestruct:
        def __init__(self, bot):
            self.bot = bot
            bot.register_command('confirm self destruct code', self.confirm)
            bot.register_command('initiate self destruct sequence', self.init)
            chars = string.letters + string.digits
            self.code = ''.join([random.choice(chars) for i in range(10)])

        def confirm(self, data):
            if data['username'] in self.bot.settings.SELFDESTRUCT_USERS:
                self.bot.notice(data['username'], 'SELF DESTRUCT CODE %s' % self.code)
            else:
                self.bot.say('You are not authorised for the self destruct code!')
        
        def init(self, data):
            if data['message'] == self.code:
                import os
                os._exit(1)
            else:
                self.bot.say('INCORRECT SELF DESTRUCT SEQUENCE AUTHORISATION CODE.')
