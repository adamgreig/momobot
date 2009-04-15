# -*- coding: utf-8 -*-
"""
Handle talking to an IRC server.
"""

import socket

class IRC:
    """Connect to and communicate with an IRC server."""
    
    def __init__(self, server, port, nickname):
        """Connect to the server and set our nickname"""
        self.nickname = nickname
        self.callbacks = {}
        
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((server, port))
        self.socket.send('NICK %s\r\n' % nickname)
        self.socket.send('USER %s %s %s :%s\r\n' % (nickname, nickname, nickname, nickname))
    
    def identify(self, password):
        """Identify with NickServ"""
        self.socket.send('PRIVMSG nickserv :identify %s\r\n' % password)
    
    def join(self, channel):
        """Join a channel"""
        self.channel = channel
        self.socket.send('JOIN %s\r\n' % channel)
    
    def part(self):
        """Leave the current channel"""
        self.socket.send('PART %s\r\n' % self.channel)
    
    def quit(self, message='Momobot Disconnected'):
        """Quit the server"""
        self.socket.send('QUIT :%s\r\n' % message)
        self.socket.close()
    
    def say(self, message):
        """Say a message to the channel"""
        self.socket.send('PRIVMSG %s :%s\r\n' % (self.channel, message))
    
    def privmsg(self, user, message):
        """PM someone"""
        self.socket.send('PRIVMSG %s :%s\r\n' % (user, message))
    
    def notice(self, user, message):
        """Send someone a notice"""
        self.socket.send('NOTICE %s :%s\r\n' % (user, message))
    
    def read(self):
        """Read in data from IRC"""
        self.buffer = self.socket.recv(4096)
        self.parse()
    
    def parse(self):
        """Parse the current buffer, doing all sorts of exciting things
        with it"""
        while self.buffer.find('\r\n') is not -1:
            message = self.buffer.split('\r\n')[0].split(' ')
            try:
                sender = message[0]
                command = message[1]
                text = ' '.join(message[2:])
            except IndexError:
                pass
            else:
                self.process_irc_command(sender, command, text)
            finally:
                self.buffer = self.buffer[self.buffer.find('\r\n') + 2:]
    
    def process_irc_command(self, sender, command, text):
        """Process a given command"""
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
                self.callback('channel_message', {'username': username, 'message': message})
            elif message == "\001VERSION\001":
                self.socket.send('NOTICE %s :\001VERSION Momobot v0.1a1\001\r\n' % username)
            elif message.find("\001PING") == 0:
                data = message.split(' ')[1]
                data = data.strip('\001')
                self.socket.send('NOTICE %s :\001PING %s\001\r\n' % (username, data))
    
    def callback(self, callback_type, data):
        """Call a registered callback with the proper data dictionary"""
        try:
            callback = self.callbacks[callback_type]
            callback(data)
        except KeyError, TypeError:
            print "Invalid or no callback for action %s." % callback_type
    
    def register_callback(self, callback_type, callback):
        self.callbacks[callback_type] = callback