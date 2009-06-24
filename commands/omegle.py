# -*- coding: utf-8 -*-

import threading
import urllib
import simplejson
import datetime
import time

base_url = "http://omegle.com/"
start_url = base_url + "start"
check_url = base_url + "events"
send_url = base_url + "send"
dc_url = base_url + "disconnect"

started = False

class client(threading.Thread):
    thread_id = 1
    closed_chats = []
    
    def __init__(self, irc, id_check, id_speak):
        self.irc = irc
        threading.Thread.__init__(self)
        if client.thread_id == 1:
            self.myid = 1
            client.thread_id = 2
        else:
            self.myid = 2
            client.thread_id = 1
        self.id_check = id_check
        self.id_speak = id_speak
        self.id_check_p = urllib.urlencode({'id':id_check})
        self.id_speak_p = urllib.urlencode({'id':id_speak})
    
    def run(self):
        global started
        while True:
            time.sleep(1)
            e = urllib.urlopen(check_url, self.id_check_p)
            events = simplejson.loads(e.read())
            if events:
                for event in events:
                    if event[0] == 'gotMessage':
                        msg = event[1]
                        msg = msg.encode('utf-8')
                        self.say("<%s> %s" % (self.myid, msg))
                        params = urllib.urlencode({'id':self.id_speak,
                                                   'msg':msg})
                        urllib.urlopen(send_url, params)
                        time.sleep(1)
                    elif event[0] == 'connected':
                        self.say("%s * CONNECTED" % self.myid)
                    elif event[0] == 'strangerDisconnected':
                        self.say("%s * DISCONNECTED" % self.myid)
                        urllib.urlopen(dc_url, self.id_speak_p)
                        client.closed_chats.append(self.id_speak)
                        started = False
                        return
            for chat in client.closed_chats:
                if chat == self.id_check:
                    client.closed_chats.remove(chat)
                    started = False
                    self.say("%s * CLOSED" % self.myid)
                    return

class Omegle:
    def __init__(self, bot):
        self.bot = bot
        bot.register_command('omeglestart', self.start)
        bot.register_command('omeglestop', self.stop)
        bot.register_command('omegle1', self.send1)
        bot.register_command('omegle2', self.send2)
        bot.register_command('omegles1', self.split1)
        bot.register_command('omegles2', self.split2)
    
    def start(self, data):
        global started
        if started:
            self.bot.say('A chat is already in progress, not starting.')
            return
        
        started = True
        
        f = urllib.urlopen(start_url, '')
        chat_id_1 = f.read()
        chat_id_1 = chat_id_1[1:-1]
        
        f = urllib.urlopen(start_url, '')
        chat_id_2 = f.read()
        chat_id_2 = chat_id_2[1:-1]
        
        self.bot.say('Got chat IDs, starting...')
        
        self.starttime = datetime.datetime.today()
        self.c1 = client(self.bot, chat_id_1, chat_id_2)
        self.c2 = client(self.bot, chat_id_2, chat_id_1)
        
        self.c1.start()
        self.c2.start()
    
    def stop(self, data):
        global started
        if started:
            client.closed_chats.append(self.c1.id_check)
            client.closed_chats.append(self.c2.id_check)
            self.bot.say("%s * DISCONNECTED" % self.c1.myid)
            urllib.urlopen(dc_url, self.c1.id_speak_p)
            self.bot.say("%s * DISCONNECTED" % self.c2.myid)
            urllib.urlopen(dc_url, self.c2.id_speak_p)
            started = False
    
    def split1(self, data):
        urllib.urlopen(dc_url, self.c1.id_check_p)
        self.bot.say("*1 Split")
    
    def split2(self, data):
        urllib.urlopen(dc_url, self.c2.id_check_p)
        self.bot.say("*2 Split")
    
    def send1(self, data):
        global started
        if started:
            if 'message' in data:
                msg = data['message']
                msg = msg.encode('utf-8')
                params = urllib.urlencode({'id':self.c1.id_speak, 'msg':msg})
                urllib.urlopen(send_url, params)
    def send2(self, data):
        global started
        if started:
            if 'message' in data:
                msg = data['message']
                msg = msg.encode('utf-8')
                params = urllib.urlencode({'id':self.c2.id_speak, 'msg':msg})
                urllib.urlopen(send_url, params)
