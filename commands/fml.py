# -*- coding: utf-8 -*
# Peter Zatka-Haas - June 2009

import pickle
import os
import urllib
import random
from xml.dom import minidom

fml_feed_url = "http://api.betacie.com/view/random?language=en&key=readonly"
stats_file = "commands/stats.db"

class Fml:
    """
    !fml grabs random post from fml and says in channel
    """
    def __init__(self, bot):
        self.bot = bot
        self.stats = {}
        self.ids = []
        self.__load_stats()
        bot.register_command("fml", self.fml)
        bot.register_command("fmlstats", self.fml_stats)
        bot.register_command("fmlstatsall", self.fml_stats_all)

    def grab_random(self):
        file_object = urllib.urlopen(fml_feed_url)
        xmldoc = minidom.parse(file_object)
        items_node = xmldoc.firstChild.childNodes[1].firstChild
        fml_id = items_node.getAttribute('id')
        while fml_id in self.ids:
            file_object = urllib.urlopen(fml_feed_url)
            xmldoc = minidom.parse(file_object)
            items_node = xmldoc.firstChild.childNodes[1].firstChild
            fml_id = items_node.getAttribute('id')
        self.ids.append(fml_id)
        date = items_node.childNodes[2].firstChild.data
        text = items_node.childNodes[6].firstChild.data
        agree = items_node.childNodes[3].firstChild.data
        deserved = items_node.childNodes[4].firstChild.data
        fml_set = [text, date, agree, deserved]
        return fml_set
    
    def fml(self, data):
        random_number = random.randrange(0,499)
        if random_number == 123 and data['username'] != "redd":
            self.bot.say('f YOUR life')
            os._exit(1)
        fml = self.grab_random()
        if data['message'] == "p":
            self.bot.notice(data['username'], "'%s' | Agreed: %s | Deserved: %s" % (fml[0], fml[2], fml[3]))
        else:
            self.bot.say("'%s' | Agreed: %s | Deserved: %s" % (fml[0], fml[2], fml[3]))
        if "Xait" in data['username']:
            user = "XaiterPhone"
        else:
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
