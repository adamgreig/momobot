# -*- coding: utf-8 -*
# Peter Zatka-Haas - June 2009

import pickle
import os
import urllib
import random
from xml.dom import minidom

stats_file = "commands/stats.db"

class Fml:
    """
    !fml grabs random post from fml and says in channel
    """
    def __init__(self, bot):
        self.bot = bot
        self.stats = {}
        self.ids = []
        self.choices = ["random", "last", "top", "flop"]
        self.__load_stats()
        bot.register_command("fml", self.fml)
        bot.register_command("fmlstats", self.fml_stats)
        bot.register_command("fmlstatsall", self.fml_stats_all)
        
    def is_number(self, string):
        try:
            float(string)
            return True
        except ValueError:
            return False
        
    def url(self, choice):
        if self.is_number(choice):
            self.go_ahead = 1
            return "http://api.betacie.com/view/" + choice + "/nocomment?language=en&key=readonly"
        elif choice in self.choices:
            self.go_ahead = 1
            return "http://api.betacie.com/view/" + choice + "?language=en&key=readonly"
        else:
            self.bot.say("Error: You must select an option")
            self.go_ahead = 0
            return "ERROR"

    def grab_random(self, choice):
        url = self.url(choice)
        if url == "ERROR":
            return 1
        try:
            file_object = urllib.urlopen(url)
            xmldoc = minidom.parse(file_object)
            items_node = xmldoc.getElementsByTagName("root")[0].getElementsByTagName("items")[0].getElementsByTagName("item")[0]
            date = items_node.getElementsByTagName("date")[0].firstChild.data
            text = items_node.getElementsByTagName("text")[0].firstChild.data
            agree = items_node.getElementsByTagName("agree")[0].firstChild
            if agree is not None:
                agree = agree.data
            deserved = items_node.getElementsByTagName("deserved")[0].firstChild
            if deserved is not None:
                deserved = deserved.data
            id_string = str(items_node.getAttribute('id'))
            fml_set = [text, date, agree, deserved, id_string]
        except Exception as inst:
            self.bot.say("Error parsing FML: %s", inst)
        return fml_set
    
    def fml(self, data):
        if data['message']:
            choice = data['message']
        else:
            choice = "random"
        fml = self.grab_random(choice)
        if self.go_ahead:
            saystr = u"'%s' | Agreed: %s | Deserved: %s | Id: %s" % (fml[0], fml[2], fml[3], fml[4])
            self.bot.say(saystr.encode('utf-8'))
        user = data['username']
        self.counter(user)
        self.__store_stats()

    def counter(self, user):
        if self.stats.has_key(user):
            self.stats[user] += 1
            if self.stats[user] % 1000 == 0:
                self.bot.say('Congratulations, you have read %s FMLs! You must hate yourself.' % str(self.stats[user]))
        else:
            self.stats[user] = 1
            
    def fml_stats(self, data):
        if data['message']:
            target = data['message'].split()[0]
            if self.stats.has_key(target):
                self.bot.say("%s: %s" % (target, self.stats[target]))
            else:
                self.bot.say("No stats for %s" % target)
        else:
            self.bot.say("%s: %s" % (data['username'], self.stats[data['username']]))

    def fml_stats_all(self, data):
        string = ""
        items_list = self.stats.items()
        items_list.sort(lambda x,y: cmp(y[1],x[1]))
        for name, count in items_list:
            string += (" %s: %s ||" % (name, str(count)))
        self.bot.say("||"+string)

    def __store_stats(self):
        f = open(stats_file, "wb")
        pickle.dump(self.stats, f)
        f.close()
            
    def __load_stats(self):
        if os.path.exists(stats_file):
            f = open(stats_file, "rb")
            self.stats = pickle.load(f)
            f.close()
        else:
            self.stats = {}
