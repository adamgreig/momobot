# -*- coding: utf-8 -*-
# Peter Zatka-Haas - April 2009

import os
import pickle
import random
                               
quotes_file = "commands/quotes.db"                      

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
        self.__load_quotes()
        bot.register_command('setquote', self.set_quote)
        bot.register_command('quote', self.get_quote)

    
    def set_quote(self, data):
        self.quotes[data['username']] = data['message']
        self.bot.irc.say("Okay, %s" % data['username'], data['channel'])
        self.__store_quotes()
    
    def get_quote(self, data):
        requester = data['username']
        quotee = data['message']
        quotee = quotee.strip()
        
        if len(quotee) == 0:
            quotee = requester
        
        if quotee == self.bot.nickname and self.quotes:
            quotee = random.choice(self.quotes.keys())
        
        self.bot.irc.say(self.__get_quote(requester, quotee))

    def __get_quote(self, requester, quotee):
        if quotee in self.quotes:
            return '"%s" - %s' % (self.quotes[quotee], quotee)
        elif quotee == requester:
            return 'Sorry, you never set a quote. Try the setquote command!'
        elif quotee == self.bot.nickname:
            return 'Sorry, but there are no quotes. Try setting one!'
        else:
            return "%s hasn't set a quote yet." % quotee
            
    def __store_quotes(self):
        f = open(quotes_file, 'w')
        pickle.dump(self.quotes, f)
        f.close()
    
    def __load_quotes(self):
        if os.path.exists(quotes_file):
            f = open(quotes_file, 'r')
            self.quotes = pickle.load(f)
            f.close()
        else:
            self.quotes = {}
        
        
