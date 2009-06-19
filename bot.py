# -*- coding: utf-8 -*-
"""
Handle actually being a useful bot
"""

import socket
import time
import irc
import command_loader

class BotError(Exception):
    pass

class CommandError(BotError):
    def __str__(self):
        return "The command being registered was not callable."

class Bot:
    def __init__(self, settings):
        self.settings = settings
        self.nickname = settings.NICKNAME
        self.irc = irc.IRC(settings.NICKNAME, settings.CTCP_VERSION)
        self.commands = {}
        self.channels = []
        command_loader.CommandLoader(self)
        self.irc.register_callback('channel_message', self.process_message)
        self.irc.connect(settings.SERVER, settings.PORT)
        if settings.PASSWORD:
            self.irc.identify(settings.PASSWORD)
        self.irc.join(settings.CHANNEL)
        self.say_q = []

  #  def say(self, message, channel=""):
   #     """
    #    Adds say message to speak queue for spam control. This then passes
     #   to the speak method which does the actual say in channel, or channels
      #  """
       # message = message.encode("utf-8")
        #self.say_q.append(message)




        #self.speak(message, channel)

    def say(self, message, channel=""):
        if channel:
            for channel in self.channels:
                self.socket.send("PRIVMSG %s :%s\r\n" % (channel,
                                                     message))
        else:
            if channel in self.channels:
                self.socket.send("PRIVMSG %s :%s\r\n" % (channel,
                                                    message))

    def process(self):
        self.irc.read()
    
    def process_message(self, data):
        for command_indicator in self.settings.COMMAND_INDICATORS:
            if data['message'].startswith(command_indicator):
                data['message'] = data['message'].replace(command_indicator,
                                                          '', 1)
                for command in self.commands:
                    if data['message'].startswith(command):
                        data['message'] = data['message'].replace(command,
                                                                  '', 1)
                        data['message'] = data['message'].lstrip()
                        command = self.commands[command]
                        time.sleep(self.settings.COMMAND_DELAY)
                        command(data)
                        return
            else:
                #irc.say(data['message'], data['channel'])
                pass
    
    def register_command(self, command_name, command):
        if callable(command):
            self.commands[command_name] = command
        else:
            raise CommandError
