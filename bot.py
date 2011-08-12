# -*- coding: utf-8 -*-
"""
Handle actually being a useful bot
"""

import socket
import time
import irc
import command_loader
import sys

import message_queue

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
        self.__queue = message_queue.MessageQueue(self.irc, 2)
        command_loader.CommandLoader(self)
        self.irc.register_callback('channel_message', self.process_message)
        self.irc.connect(settings.SERVER, settings.PORT)
        if settings.PASSWORD:
            self.irc.identify(settings.PASSWORD)
        self.irc.join(settings.CHANNEL)

    def process(self):
        while True:
            try:
                self.irc.read()
                self.__queue.process_message_queue()
            except Exception, e:
                self.irc.say('Exception occured: %s' % e)
    
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
                pass
    
    def register_command(self, command_name, command):
        if hasattr(command, '__call__'):
            self.commands[command_name] = command
        else:
            raise CommandError

    def say(self, message, channel=''):
        self.__queue.addSayMessage(message, channel)
    
    def act(self, message, channel=''):
        self.__queue.addActMessage(message, channel)
    
    def privmsg(self, user, message):
        self.__queue.addPrivateMessage(user, message)
    
    def notice(self, user, message):
        self.__queue.addNoticeMessage(user, message)
        
