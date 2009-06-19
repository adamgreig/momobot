# -*- coding: utf-8 -*-
"""
Handle actually being a useful bot
"""

import socket
import time
import irc
import command_loader
import datetime
import Queue

class BotError(Exception):
    pass

class CommandError(BotError):
    def __str__(self):
        return "The command being registered was not callable."
    
class Message:
    def __init__(self, type, message, target):
        self.type = type
        self.message = message
        self.target = target            
    
class MessageQueue:
    # Message Types
    __sayMsg = 'say'
    __actMsg = 'act'
    __privMsg = 'priv'
    __noticeMsg = 'notice'
    
    __irc = None
    __timeMessageLastSent = None
    __messageWaitMilliseconds = None
    
    
    def __init__(self, irc, messagesPerSecond):
        if messagesPerSecond <= 0:
            raise Exception, "messagesPerSecond must be greater than 0."
    
        self.__messageWaitMilliseconds = datetime.timedelta(milliseconds=(1000 / messagesPerSecond))
        self.__queue = Queue.LifoQueue()
    
    def addSayMessage(self, message, channel=''):
        self.__queue.put(message(__sayMsg, message, channel))
    
    def addActMessage(self, message, channel=''):
        self.__queue.put(message(__actMsg, message, channel))
    
    def addPrivateMessage(self, user, message):
        self.__queue.put(message(__privMsg, message, user))
    
    def addNoticeMessage(self, user, message):
        self.__queue.put(message(__noticeMsg, message, user))
        
    def process_message_queue(self):
        if self.__timeMessageLastSent != None and (self.__timeMessageLastSent - datetime.now) <= self.__messageWaitMilliseconds:
            return
    
        currentMessage = self.__queue.get()
        
        if currentMessage.type == __sayMsg:
            self.__irc.say(currentMessage.message, currentMessage.target)
        elif currentMessage.type == __actMsg:
            self.__irc.act(currentMessage.message, currentMessage.target)
        elif currentMessage.type == __privMsg:
            self.__irc.privmsg(currentMessage.target, currentMessage.message)
        elif currentMessage.type == __noticeMsg:
            self.__irc.notice(currentMessage.target, currentMessage.message)
            
        self.__timeMessageLastSent = datetime.now    


class Bot:
    __messageQueue = MessageQueue(irc, 2)

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

    def process(self):
    
        while True:
#            try:
            self.irc.read()
            self.__messageQueue.process_message_queue()
#            except:
#                self.say('Exception occured.')
            
    
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

    def say(self, message, channel=''):
        self.irc.say(message, channel)
    
    def act(self, message, channel=''):
        self.irc.act(message, channel)
    
    def privmsg(self, user, message):
        self.irc.privmsg(user, message)
    
    def notice(self, user, message):
        self.irc.notice(user, message)
        
