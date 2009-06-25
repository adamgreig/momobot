# -*- coding: utf-8 -*-

from xml.dom import minidom
import urllib2

twitter_feed_url = 'http://twitter.com/statuses/user_timeline/%s.rss'

class Twitter:
    """
    Grab a twitter user's latest update. Also socks (sockington) is hardcoded.
    """
    def __init__(self, bot):
        self.bot = bot
        bot.register_command('socks', self.socks)
        bot.register_command('twitter', self.twitter)
    
    def twitter(self, data):
        username = data['message'].split(' ')[0]
        feed_url = twitter_feed_url % username
        f = urllib2.urlopen(feed_url)
        xmldoc = minidom.parse(f)
        items = xmldoc.getElementsByTagName('item')
        if items:
            item = items[0]
            status = item.getElementsByTagName('description')[0].firstChild
            if status:
                status = status.data
            date = item.getElementsByTagName('pubDate')[0].firstChild
            if date:
                date = date.data
            message = status + ' (' + date + ')'
            self.bot.say(message.encode('utf-8'), data['channel'])
    
    def socks(self, data):
        data['message'] = 'sockington'
        self.twitter(data)
