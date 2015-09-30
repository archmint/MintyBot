#!/usr/bin/env python3

""" Minty Bot

This module allows the user to connect a bot to an irc network with ssl.
"""
from socket import socket, AF_INET as inet, SOCK_STREAM as stream
from ssl import wrap_socket
from time import sleep

class Bot():
    def __init__(self, **kwargs):
        self.nick = kwargs.get('nick', 'mintybot_')
        """ visible nick of the bot
            DEFAULT: 'mintybot'"""

        self.password = kwargs.get('password', None)
        """ password used to identify with nickserv
            DEFAULT: None
            when self.password is None, bot doesn't try to identify"""

        self.realname = kwargs.get('realname', '\x0303Minty\x03 Bot')
        """ realname that gets displayed in WHOIS, etc"""

        self.ident = kwargs.get('ident', self.nick)
        """ the ident of the bot
            DEFAULT: self.nick"""

        self.host = kwargs.get('host', 'irc.freenode.net')
        """ host to connect to
            DEFAULT: 'irc.freenode.net'"""

        self.port = kwargs.get('port', 6697)
        """ port to connect to host with
            DFAULT: 6697"""

        self.chans = kwargs.get('chans', None)
        """ channels the bot is joined (initially it is what channels to join)
            DEFAULT: None
            when self.chans is None, the bot will simply quit"""

        self.s = wrap_socket(socket(inet, stream)) # create ssl socket
        """ ssl socket used to speak to the host"""

        self.hostname = None
        """ name of the host you connect to
            EXAMPLE: sendak.freenode.net NOTICE"""

        if self.chans is None:
            self.chans = []
        elif not isinstance(self.chans, list):
            self.chans = [self.chans]


    def _connect(self):
        """ private method _connect(self):

                connect to the host, wait for response
                identify bot with NICK and USER
        """
        self.s.connect((self.host, self.port))

        rb = "" # read buffer
        b = False # break condition
        while not b:
            rb = rb + self.s.recv(1024).decode('utf-8')
            tmp = rb.split("\n")
            rb = tmp.pop()

            for line in tmp:
                line = line.rstrip()
                spline = line.split()
                print(line)

                if self.hostname is None:
                    self.hostname = spline[1]

                if ' '.join(spline[-3:]).lower() == 'found your hostname':
                    print("\x1b[32;1mFound hostname\x1b[0m")
                    b = True
                elif spline[0] == 'ERROR':
                    return False

        self.s.send('NICK {}\r\n'.format(self.nick).encode('utf-8'))
        self.s.send('USER {} 0 * :{}\r\n'.format(self.nick, self.realname).encode('utf-8'))

        rb = ""
        b = False
        while not b:
            rb = rb + self.s.recv(1024).decode('utf-8')
            tmp = rb.split("\n")
            rb = tmp.pop()

            for line in tmp:
                line = line.rstrip()
                spline = line.split()
                print(line)

                if ' '.join(spline[1:3]) == 'MODE {}'.format(self.nick):
                    b = True
                elif spline[0] == 'ERROR':
                    return False

        if self.password is not None:
            self.s.send('PRIVMSG NickServ :identify {}'.format(self.password).encode('utf-8'))

        sleep(2) # TODO:

        for chan in self.chans:
            sleep(.5)
            print('\x1b[34;1mJoining\x1b[21m {}'.format(chan))
            self.s.send('JOIN {}\r\n'.format(chan).encode('utf-8'))

        return True

    def mainLoop(self):
        rb = ""
        while True:
            rb = rb + self.s.recv(1024).decode('utf-8')
            tmp = rb.split("\n")
            rb = tmp.pop()

            for line in tmp:
                line = line.rstrip()
                spline = line.split()
                print(line)

                if spline[0] == 'PING':
                    self.s.send('PONG {}\r\n'.format(spline[1]).encode('utf-8'))
                elif spline[0] == 'ERROR':
                    return False
        return True


if __name__ == "__main__":
    bot = Bot(chans=["##und3rw0rld"])
    connected = bot._connect()
    if connected:
        print("\x1b[32;1mConnected\x1b[0m")
    else:
        print("\x1b[31;1mNot Connected\x1b[0m")
    bot.mainLoop()

