# -*- coding: utf-8 -*-
# Peter Zatka-Haas - June 2009

import urllib
from xml.dom import minidom

fml_feed_url = "http://api.betacie.com/view/random?language=en&key=readonly"

class Fml:
    """
    !fml grabs random post from fml and says in channel
    """
    def __init__(self, bot):
        self.bot = bot
        self.posts = []
        bot.register_command("fml", self.fml)
        
    def grab_random(self):
        file_object = urllib.urlopen(fml_feed_url)
        xmldoc = minidom.parse(file_object)
        items_node = xmldoc.firstChild.childNodes[1].firstChild
        date = items_node.childNodes[2].firstChild.data
        text = items_node.childNodes[6].firstChild.data
        agree = items_node.childNodes[3].firstChild.data
        deserved = items_node.childNodes[4].firstChild.data
        fml_set = [text, date, agree, deserved]
        return fml_set
    
    def fml(self, data):
        fml = self.grab_random()
        self.bot.irc.say("'%s' | Agreed: %s | Deserved: %s" % (fml[0], fml[2], fml[3]))

