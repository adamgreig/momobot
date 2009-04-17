# -*- coding: utf-8 -*-
# Peter Zatka-Haas - April 2009

import random

class Quotes:
    """
    Users assign quotes, which momo stores.
    Momo can output the quote in channel later.
    
    Momo will respond:
    
    !setquote ..    
        Momo registers the quote .. in a dictionary
        where the KEY is the sender of the command. Any previous quote
        already assigned will be overwritten
    !quote
        Momo says the quote assigned to the sender of this command
        If no quote has been assigned then momo responds accordingly
    !quote <user>
        Momo says the quote assigned to the <user> name given.
        If no quote has been assigned then momo responds accordingly
    !quote NICKNAME
        Momo will return a random quote from the dictionary
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
        requester = data['username']
        quotee = data['message']
        quotee.strip()
        
        if len(quotee) == 0:
            quotee = requester
        
        if quotee == self.bot.nickname:
            quotee = random.choice(self.quotes.keys())
        
        self.bot.irc.say(self.__get_quote(requester, quotee))

    def __get_quote(self, requester, quotee):
        if self.quotes.has_key(quotee):
            return '"%s" - %s' % (self.quotes[quotee], quotee)
        elif quotee == requester:
            return 'Sorry, you never set a quote. Try the setquote command!'
        else:
            return "%s hasn't set a quote yet." % quotee
