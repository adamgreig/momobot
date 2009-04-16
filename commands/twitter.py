# -*- coding: utf-8 -*-

import feedparser

twitter_feed_url = 'http://twitter.com/statuses/user_timeline/%s.rss'

class Twitter:
    def __init__(self, bot):
        self.bot = bot
        bot.register_command('socks', self.socks)
        bot.register_command('twitter', self.twitter)
    
    def twitter(self, data):
        username = data['message'].split(' ')[0]
        feed_url = twitter_feed_url % username
        feed = feedparser.parse(feed_url)
        if len(feed.entries) > 0:
            self.bot.irc.say('%s (%s)' % (feed.entries[0]['title'],
                                          feed.entries[0]['updated']))

    def socks(self, data):
        data['message'] = 'socks'
        self.twitter(data)