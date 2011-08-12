import feedparser

class Woot:
    """
    Returns the current item on sale at Woot.com, according to the woot rss.
    """
    def __init__(self, bot):
        self.bot = bot
        bot.register_command('woot', self.woot)
        print "hello woot world"
        self.bot.say('I exist')
	
    def woot(self, data):
        print "Wooting! {}".format(self.get_woot())
        self.bot.say('The current sale at www.woot.com is ' + self.get_woot(), data['channel'])
		
    def get_woot(self):
        woot = feedparser.parse("http://www.woot.com/blog/rss.aspx") 
        sale = "No woots? How is this possible!?"
        for item in woot['entries']:
            if item.category == 'Woot':
                sale = item.title
                break
        return sale
