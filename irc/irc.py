# -*- coding: utf-8 -*-
"""
Handle talking to an IRC server.
"""

import socket

class IRC:
    """Connect to and communicate with an IRC server."""
    
    def __init__(self, server, port, nickname):
        """
        Connect to the server and set our nickname
        server: The IRC server to connect to
        port: The IRC port to connect to
        nickname: The nickname to use on IRC
        """
        self.nickname = nickname
        self.callbacks = {}
        
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((server, port))
        self.socket.send('NICK %s\r\n' % nickname)
        self.socket.send('USER %s %s %s :%s\r\n' % (nickname, nickname, nickname, nickname))
    
    def identify(self, password):
        """
        Identify with NickServ
        password: The NickServ password
        """
        self.socket.send('PRIVMSG nickserv :identify %s\r\n' % password)
    
    def join(self, channel):
        """
        Join a channel
        channel: The channel to join, including the #
        """
        self.channel = channel
        self.socket.send('JOIN %s\r\n' % channel)
        self.__callback('join', {'channel': channel})
    
    def part(self):
        """
        Leave the current channel
        """
        self.socket.send('PART %s\r\n' % self.channel)
    
    def quit(self, message='Momobot Disconnected'):
        """
        Quit the server
        message: The quit message to use
        """
        self.socket.send('QUIT :%s\r\n' % message)
        self.socket.close()
    
    def say(self, message):
        """
        Say a message to the channel
        message: Message to say
        """
        self.socket.send('PRIVMSG %s :%s\r\n' % (self.channel, message))
    
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
        """
        self.buffer = self.socket.recv(4096)
        self.__parse()
    
    def __parse(self):
        """
        Parse the current buffer, processing each \r\n-terminated line
        at a time, splitting it into sender/command/text, then parsing
        it if it was successfully split
        """
        while self.buffer.find('\r\n') is not -1:
            message = self.buffer.split('\r\n')[0].split(' ')
            try:
                sender = message[0]
                command = message[1]
                text = ' '.join(message[2:])
            except IndexError:
                pass
            else:
                self.__process_irc_command(sender, command, text)
            finally:
                self.buffer = self.buffer[self.buffer.find('\r\n') + 2:]
    
    def __process_irc_command(self, sender, command, text):
        """
        Process a command from the IRC server
        Commands such as PING, NOTICE and PRIVMSG are processed here.
        
        PING: send a PONG reply to the server, letting it know we're alive
        
        NOTICE: pass
        
        PRIVMSG: the main command, split it up and see what it is
        
        sender: The full sender string
        command: The command from the IRC server
        text: Everything following the command
        """
        if command == "PING":
            self.socket.send('PONG %s\r\n' % text)
        elif command == "NOTICE":
            #Right now, we shouldn't get notices. So do nothing.
            pass
        elif command == "PRIVMSG":
            try:
                username = sender.split('!')[0].split(':')[1]
                target = text.split(':')[0].strip()
                message = text.split(':')[1]
            except IndexError:
                return
            
            if target == self.channel:
                self.__callback('channel_message', {'username': username, 'message': message})
            elif message == "\001VERSION\001":
                self.socket.send('NOTICE %s :\001VERSION Momobot v0.1a1\001\r\n' % username)
            elif message.find("\001PING") == 0:
                data = message.split(' ')[1]
                data = data.strip('\001')
                self.socket.send('NOTICE %s :\001PING %s\001\r\n' % (username, data))
        elif command == "JOIN":
            try:
                username = sender.split('!')[0].split(':')[1]
                channel = text.split(':')[1]
            except IndexError:
                return
                
            if channel == self.channel:
                self.__callback('channel_join', {'username': username})
    
    def __callback(self, callback_type, data):
        """
        Try to call a registered callback with the proper data dictionary
        callback_type: The callback to try calling. E.g., 'channel_message'
        data: The dictionary that should be passed to the callback function
        """
        try:
            callback = self.callbacks[callback_type]
            callback(self, data)
        except KeyError, TypeError:
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
        self.callbacks[callback_type] = callback