# -*- coding: utf-8 -*-
"""
Handle actually being a useful bot
"""

import time
import irc
import commands

class BotError(Exception):
    pass

class CommandError(BotError):
    def __str__(self):
        return "The command being registered was not callable."

class Bot:
    def __init__(self, settings):
        self.settings = settings
        self.irc = irc.IRC(settings.NICKNAME, settings.CTCP_VERSION)
        self.commands = {}
        commands.Commands(self)
        self.irc.register_callback('channel_message', self.process_message)
        self.irc.connect(settings.SERVER, settings.PORT)
        self.irc.join('#momobot')
    
    def process(self):
        self.irc.read()
    
    def process_message(self, data):
        for command_indicator in self.settings.COMMAND_INDICATOR:
            if data['message'].startswith(command_indicator):
                message = data['message'].replace(command_indicator, '')
                for command in self.commands:
                    if message.startswith(command):
                        message = message.replace(command, '')
                        message = message.lstrip()
                        command = self.commands[command]
                        time.sleep(self.settings.COMMAND_DELAY)
                        command(self, message)
                        return
    
    def register_command(self, command_name, command):
        if callable(command):
            self.commands[command_name] = command
        else:
            raise CommandError