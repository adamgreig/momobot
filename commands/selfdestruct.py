import random
import string
from time import sleep

class Selfdestruct:
        def __init__(self, bot):
            self.bot = bot
            bot.register_command('confirm self destruct code', self.confirm)
            bot.register_command('initiate self destruct sequence', self.init)
            bot.register_command('abort self destruct sequence', self.abort)
            chars = string.letters + string.digits
            self.code = ''.join([random.choice(chars) for i in range(10)])

        def confirm(self, data):
            self.bot.irc.notice(data['username'], 'SELF DESTRUCT CODE %s' % self.code)
        
        def init(self, data):
            if data['message'] == self.code:
                self.bot.say('SELF DESTRUCT SEQUENCE STARTED. DESTRUCTION IN FIVE SECONDS...')
                sleep(1)
                self.bot.say('FOUR...')
                sleep(1)
                self.bot.say('THREE...')
                sleep(1)
                self.bot.say('TWO...')
                sleep(1)
                if "skk" in data['username']:
                    self.bot.say("just kidding :3, feck you %s" % data['username'])
                else:
                    self.bot.say('ONE...')
                    sleep(1)
                    import os
                    os._exit(1)
            else:
                self.bot.say('INCORRECT SELF DESTRUCT SEQUENCE AUTHORISATION CODE.')


        def abort(self, data):
            pass

