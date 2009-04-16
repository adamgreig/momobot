# -*- coding: utf-8 -*-
# Peter Zatka-Haas - April 2009

import random

class Quotes:
    """
    Users assign quotes, which momo stores. Momo can output the quote in channel later
    
    Momo will respond:
    
    !setquote ..    Momo registers the quote .. in a dictionary quotes={..}
                    where the KEY is the sender of the command. Any previous quote
                    already assigned will be overwritten
    !quote          Momo says the quote assigned to the sender of this command
                    If no quote has been assigned then momo responds accordingly
    !quote <user>   Momo says the quote assigned to the <user> name given.
                    If no quote has been assigned then momo responds accordingly
    !quote momobot  Momo will return a random quote from the dictionary quotes={..}
    """
    
    def __init__(self, bot):
        self.bot = bot
        self.quotes = {}
        bot.register_command('setquote', self.set_quote)
        bot.register_command('quote', self.get_quote)
        
    def set_quote(self, data):
        self.quotes[data['username']] = data['message']
        self.bot.irc.say("Okay, %s" % data['username'], data['channel'])
            
    def get_quote(self, data):
        target_exists = len(data['message'].split())
        if target_exists:
            target = data['message'].split()[0]
            if target == "momobot":
                random_quoter = random.choice(self.quotes.keys())
                self.bot.irc.say('"%s" - %s' % (self.quotes[random_quoter], random_quoter))
            else:
                if self.quotes.has_key(target):
                    self.bot.irc.say('"%s" - %s' % (self.quotes[target], target))
                else:
                    self.bot.irc.say("%s hasn't set a quote yet!" % target)
        else:
            if self.quotes.has_key(data['username']):
                self.bot.irc.say('"%s" - %s' % (self.quotes[data['username']], data['username']))
            else:
                self.bot.irc.say("You never set me a quote dammit >:3 rawr!")
 
