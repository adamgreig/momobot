# -*- coding: utf-8 -*-
"""
Handle talking to an IRC server.
"""

import time
import socket
import settings

class IRCError(Exception):
    """
    All IRC errors inherit from this base class
    """
    pass

class ChannelError(IRCError):
    """
    A command was issued for a channel we are not in
    """
    def __init__(self, channel):
        self.channel = channel
    def __str__(self):
        return "A command was issued for a channel we are not in: %s" % \
                self.channel

class CallbackError(IRCError):
    """
    A callback was registed that was not callable
    """
    def __str__(self):
        return "A callback was registered which was not callable."

class IRC:
    """
    Connect to and communicate with an IRC server.
    """
    
    def __init__(self, nickname, version='Momobot'):
        """
        Store our nickname, initialise various class properties
        """
        self.nickname = nickname
        self.version = version
        
        self.callbacks = {}
        self.channels = []
        
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    def connect(self, server, port):
        """
        Actually connect to the server
        """
        nickname = self.nickname
        
        self.socket.connect((server, port))
        
        self.socket.send('NICK %s\r\n' % nickname)
        self.socket.send('USER %s %s %s :%s\r\n' % 
                         (nickname, nickname, nickname, nickname))
        
        self.__callback('connect', {'server': server, 'port': port,
                        'nickname': nickname})
    
    def identify(self, password):
        """
        Identify with NickServ
        password: The NickServ password
        """
        self.socket.send('PRIVMSG nickserv :identify %s\r\n' % password)
        self.__callback('identify', {'nickname': self.nickname})
    
    def join(self, channel):
        """
        Join a channel
        channel: The channel to join, including the #
        """
        self.channels.append(channel)
        self.socket.send('JOIN %s\r\n' % channel)
        self.__callback('join', {'channel': channel})
    
    def part(self, channel=''):
        """
        Leave a specific or all channels
        """
        if channel != '':
            if channel in self.channels:
                self.socket.send('PART %s\r\n' % channel)
                self.__callback('part', {'channel': channel})
                self.channels.remove(channel)
            else:
                raise ChannelError(channel)
        else:
            for channel in self.channels:
                self.socket.send('PART %s\r\n' % channel)
                self.__callback('part', {'channel': channel})
                self.channels.remove(channel)
    
    def quit(self, message='Momobot Disconnected'):
        """
        Quit the server
        message: The quit message to use
        """
        self.socket.send('QUIT :%s\r\n' % message)
        self.socket.close()
        self.channels = []
        self.__callback('quit', {})
    
    def say(self, message, channel=''):
        """
        Say a message to the channel or all channels
        """
        if channel != '':
            if channel in self.channels:
                self.socket.send('PRIVMSG %s :%s\r\n' % 
                                 (channel, message))
            else:
                raise ChannelError(channel)
        else:
            for channel in self.channels:
                self.socket.send('PRIVMSG %s :%s\r\n' %
                                 (channel, message))
    
    def act(self, message, channel=''):
        """
        Send a CTCP action to the channel or all channels
        """
        message = '\001ACTION ' + message + '\001'
        self.say(message, channel)
    
    def privmsg(self, user, message):
        """
        PM someone
        user: The username to PM
        message: The message to send them
        """
        self.socket.send('PRIVMSG %s :%s\r\n' % (user, message))
    
    def notice(self, user, message):
        """
        Send someone a notice
        user: The username to send the notice to
        message: The message to send them
        """
        self.socket.send('NOTICE %s :%s\r\n' % (user, message))
    
    def read(self):
        """
        Read in data from the IRC socket then parse it
        This should be called all the time
        """
        recv_buffer = self.socket.recv(4096)
        self.__parse(recv_buffer)
    
    
    def __parse(self, recv_buffer):
        """
        Parse the current buffer, processing each \r\n-terminated line
        at a time, splitting it into sender/command/text, then parsing
        it if it was successfully split
        """
        messages = recv_buffer.split('\r\n')
        for message in messages:
            message_parts = message.split(' ')
            try:
                sender = message_parts[0]
                command = message_parts[1]
                text = ' '.join(message_parts[2:])
            except IndexError:
                pass
            else:
                self.__process_irc_command(sender, command, text)
    
    def __process_irc_command(self, sender, command, text):
        """
        Process a command from the IRC server
        Commands such as PING, NOTICE and PRIVMSG are processed here.
        
        sender: The full sender string
        command: The command from the IRC server
        text: Everything following the command
        """
        if command == "PING":
            self.socket.send('PONG %s\r\n' % text)
        elif command == "NOTICE" or command == "PRIVMSG":
            self.__process_message(sender, command, text)
        elif command == "JOIN":
            try:
                username = sender.split('!')[0].split(':')[1]
                channel = text.split(':')[1]
            except IndexError:
                return
            if channel in self.channels:
                self.__callback('channel_join', {'username': username})
    
    def __process_message(self, sender, command, text):
        """
        Process a normal message that was received, deciding whether it
        should be handled by the CTCP processor or else whether it is a
        channel or private message or notice.
        """
        try:
            username = sender.split('!')[0].split(':')[1]
            target = text.split(':')[0].strip()
            message = ':'.join(text.split(':')[1:])
        except IndexError:
            return
        
        if message.startswith('\001'):
            self.__process_ctcp(username, target, message)
        else:
            if target in self.channels:
                if command == "PRIVMSG":
                    self.__callback('channel_message', {'channel': target,
                     'username': username, 'message': message})
                elif command == "NOTICE":
                    self.__callback('channel_notice', {'channel': target,
                     'username': username, 'message': message})
            elif target == self.nickname:
                if command == "PRIVMSG":
                    self.__callback('private_message', {'username': username,
                     'message': message})
                elif command == "NOTICE":
                    self.__callback('private_notice', {'username': username,
                     'message': message})
    
    def __process_ctcp(self, username, target, message):
        """
        Process CTCP requests. Not all CTCP messages are supported.
        """
        if message.startswith('\001VERSION\001'):
            self.socket.send('NOTICE %s :\001VERSION %s\001\r\n' % (username,
                             self.version))
        elif message.startswith('\001PING'):
            data = message.split(' ')[1]
            data = data.strip('\001')
            self.socket.send('NOTICE %s :\001PING %s\001\r\n' %
                             (username, data))
        elif message.startswith('\001ACTION'):
            data = message.split(' ')[1:]
            data = ' '.join(data)
            data = data.strip('\001')
            if target in self.channels:
                self.__callback('channel_action', {'channel': target,
                 'username': username, 'message': message})
            elif target == self.nickname:
                self.__callback('private_action', {'username': username,
                 'message': message})
        elif message.startswith('\001TIME\001'):
            self.socket.send('NOTICE %s:\001TIME :%s\001\r\n' % username,
                time.asctime())
    
    
    def __callback(self, callback_type, data):
        """
        Try to call a registered callback with the proper data dictionary
        callback_type: The callback to try calling. E.g., 'channel_message'
        data: The dictionary that should be passed to the callback function
        """
        try:
            callback = self.callbacks[callback_type]
            callback(data)
        except (KeyError, TypeError):
            #print "Invalid or no callback for action %s." % callback_type
            pass
    
    def register_callback(self, callback_type, callback):
        """
        Register a callback function
        callback_type: The type of callback, e.g., 'channel_message'
        callback: The actual function that should be called. It must
        accept a two arguments: a dictionary of the relevent data and
        a reference to the current IRC connection
        """
        if callable(callback):
            self.callbacks[callback_type] = callback
        else:
            raise CommandError