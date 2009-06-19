# -*- coding: utf-8 -*-

import feedparser

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
        feed = feedparser.parse(feed_url)
        if len(feed.entries) > 0:
            self.bot.say('%s (%s)' % (feed.entries[0]['title'],
                                          feed.entries[0]['updated']),
                             data['channel'])

    def socks(self, data):
        data['message'] = 'sockington'
        self.twitter(data)
