# -*- coding: utf-8 -*-

import Queue
import datetime

class Message:
    def __init__(self, type, message, target):
        self.type = type
        self.message = message
        self.target = target           
    
class MessageQueue:
    
    def __init__(self, irc, messagesPerSecond):
        # Message Types
        self.__sayMsg = 'say'
        self.__actMsg = 'act'
        self.__privMsg = 'priv'
        self.__noticeMsg = 'notice'
        
        self.__irc = irc
        self.__timeMessageLastSent = None
        self.__messageWaitMilliseconds = None
        
        if messagesPerSecond <= 0:
            raise Exception, "messagesPerSecond must be greater than 0."
        
        self.__messageWaitMilliseconds = datetime.timedelta(milliseconds=(1000 // messagesPerSecond))
        self.__queue = Queue.Queue()
    
    def addSayMessage(self, message, channel=''):
        self.__queue.put(Message(self.__sayMsg, message, channel))
    
    def addActMessage(self, message, channel=''):
        self.__queue.put(Message(self.__actMsg, message, channel))
    
    def addPrivateMessage(self, user, message):
        self.__queue.put(Message(self.__privMsg, message, user))
    
    def addNoticeMessage(self, user, message):
        self.__queue.put(Message(self.__noticeMsg, message, user))
        
    def process_message_queue(self):
        if self.__queue.empty():
            return
        
        if self.__timeMessageLastSent != None and (datetime.datetime.now() - self.__timeMessageLastSent) <= self.__messageWaitMilliseconds:
            return
        
        currentMessage = self.__queue.get()
        
        if currentMessage.type == self.__sayMsg:
            self.__irc.say(currentMessage.message, currentMessage.target)
        elif currentMessage.type == self.__actMsg:
            self.__irc.act(currentMessage.message, currentMessage.target)
        elif currentMessage.type == self.__privMsg:
            self.__irc.privmsg(currentMessage.target, currentMessage.message)
        elif currentMessage.type == self.__noticeMsg:
            self.__irc.notice(currentMessage.target, currentMessage.message)
            
        self.__timeMessageLastSent = datetime.datetime.now()
