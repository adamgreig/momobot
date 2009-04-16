# -*- coding: utf-8 -*-
"""
All the actual bot commands
"""

import os
import commands

class CommandLoader:
    def __init__(self, bot):
        self.bot = bot
        for filename in os.listdir('commands'):
            if filename.endswith('.py') and filename != "__init__.py":
                modulename = filename[0:-3]
                classname = modulename.capitalize()
                try:
                    __import__('commands.%s' % modulename)
                    eval('commands.%s.%s(bot)' % (modulename, classname))
                except SyntaxError, error:
                    print "A syntax error occured loading the command '",
                    print filename,
                    print "':"
                    print error
                except (NameError, TypeError):
                    pass
