#!/usr/bin/env python3
"""Minty Bot

This module allows the user to connect a bot to an irc network with ssl.
"""
from imp import load_source
from inspect import isfunction
from os import listdir, walk
from os.path import join as osjoin
from re import compile as recompile, match as rematch, split as resplit
from socket import AF_INET as inet, gaierror, socket, SOCK_STREAM as stream
from ssl import wrap_socket
from time import sleep, time

import eventhandler

def main():
    bot = MintyBot(chans=['##und3rw0rld'],
            onJoin = {'##und3rw0rld' : 'hey there!'})
    connected = bot.connect()
    bot.addModules()
    if connected:
        print('\x1b[32;1mConnected\x1b[0m')
    else:
        print("\x1b[31;1mCould not establish a connection to {} on port\
 {}\x1b[0m".format(bot.host, bot.port))
        return
    print('hostname: {}'.format(bot.hostname))
    bot.mainLoop()


class MintyBot():
    """Bot that handles connecting to an irc server, staying on and calling
    functions based on matched seearch terms in the split raw lines"""
    def connect(self):
        """connect to host, wait for response, identify bot with NICK and USER
            NOTE: this method is mandatory before the mainLoop
            RETURN: <bool>"""
        self.statusOn('not connected')
        try:
            self.s.connect((self.host, self.port))
        except gaierror:
            return False

        rb = '' # read buffer
        b = False # break condition
        while not b:
            rb = rb + self.s.recv(1024).decode('utf-8')
            tmp = rb.split('\n')
            rb = tmp.pop()

            for line in tmp:
                line = line.rstrip()
                spline = line.split()
                print(line)

                if self.hostname is None:
                    self.hostname = spline[0].lstrip(':')

                if ' '.join(spline[-3:]).lower() == 'found your hostname':
                    print('\x1b[32;1mFound hostname\x1b[0m')
                    b = True
                elif spline[0] == 'ERROR':
                    return False
            ## END> for line in tmp
        ## END> while not b

        self.s.send('NICK {}\r\n'.format(self.nick).encode('utf-8'))
        self.s.send('USER {} 0 * :{}\r\n'\
                    .format(self.nick, self.realname).encode('utf-8'))

        rb = ''
        b = False
        while not b:
            rb = rb + self.s.recv(1024).decode('utf-8')
            tmp = rb.split('\n')
            rb = tmp.pop()

            for line in tmp:
                line = line.rstrip()
                spline = line.split()
                print(line)

                if ' '.join(spline[1:3]) == 'MODE {}'.format(self.nick):
                    b = True
                elif spline[0] == 'ERROR':
                    return False
            ## END> for line in tmp
        ##END> while not b

        if self.password is not None:
            self.s.send('PRIVMSG NickServ :identify {}'\
                        .format(self.password).encode('utf-8'))

            rb = ''
            b = False
            while not b:
                rb = rb + self.s.recv(1024).decode('utf-8')
                tmp = rb.split('\n')
                rb = tmp.pop()

                for line in tmp:
                    line = line.rstrip()
                    spline = line.split()
                    print(line)

                    if False:
                        b = True
                    elif spline[0] == 'ERROR':
                        return False
                ## END> for line in tmp
            ## END> while not b
        ## END> if self.password is not None

        for chan in self.chans:
            sleep(.5)
            print('\x1b[34;1mJoining\x1b[21m {}\x1b[0m'.format(chan))
            self.s.send('JOIN {}\r\n'.format(chan).encode('utf-8'))
            if chan in self.onJoin.keys():
                self.s.send('PRIVMSG {} :{}\r\n'\
                            .format(chan, self.onJoin[chan]).encode('utf-8'))
        ## END> for chan in self.chans

        self.statusOff('not connected')
        self.statusOn('connected')
        return True
    ## END> def connect(self)

    def addModules(self):
        """auto-add or re-auto-add modules in self.moduleDirs
            NOTE: this function should be called if the bot is to have any
                  modules imported. This is not automatically called simply
                  for flexibility to the programmer."""
        for mdir in self.moduleDirs:
            for dirpath, subdirs, files in walk(mdir):
                for f in files:
                    if not f.endswith('.py'):
                        continue
                    try:
                        module = load_source(f[:-3], osjoin(dirpath, f))
                        for attr in dir(module):
                            if isfunction(getattr(module, attr)):
                                print('trying to load module: {}'.format(attr))
                                eventHandler = getattr(module, attr)
                                KWARGS = {}
                                if hasattr(eventHandler, 'nick'):
                                    KWARGS['nick'] = eventHandler.nick
                                if hasattr(eventHandler, 'ident'):
                                    KWARGS['ident'] = eventHandler.ident
                                if hasattr(eventHandler, 'hostname'):
                                    KWARGS['hostname'] = self.hostname
                                if hasattr(eventHandler, 'command'):
                                    KWARGS['command'] = eventHandler.command
                                if hasattr(eventHandler, 'argument'):
                                    KWARGS['argument'] = eventHandler.argument
                                if hasattr(eventHandler, 'message'):
                                    KWARGS['message'] = eventHandler.message
                                self.eventHandlers.append(
                                    eventhandler.EventHandler(eventHandler,
                                        **KWARGS));
                                self.importedModules[eventHandler] =\
                                    self.eventHandlers[-1]
                                print('\x1b[32;1mmodule loaded: {}\x1b[0m'.\
                                    format(module))
                        ## END> for attr in dir(module)
                    except Exception as e:
                        print('\x1b[31;1mError loading file {}: {}\x1b[0m'.\
                            format(f, e))
                ## END> for f in files
            ## END> for dirpath, subdirs, files in listdir('.')
        ## END> for mdir in self.moduleDirs
    ## END> def addModules(self)

    def mainLoop(self):
        """main loop where the bot calls onNewline() for updates"""
        rb = '' # read buffer
        while -1 not in self.status.keys():
            rb = rb + self.s.recv(1024).decode('utf-8')
            newlines = rb.split('\n')
            rb = newlines.pop()

            for newline in newlines:
                self.onNewline(newline.rstrip())
        ## END> while -1 not in self.status.keys()
    ## END> def mainLoop(self)

    def onNewline(self, line):
        """on newline this method should be overridden, as this is just a
           stub that responds to pings
            PARAM: <str>(line - the raw line received)
            RETURN: <bool>
            NOTE: use `Bot().onNewline = function`, etc to override this in
                  bot's extended class"""
        print(line)

        spline = line.split()

        if spline[0] == 'PING':
            nick = None
            ident = None
            hostname = None
            command = 'PING'
            argument = None
            message = line.split(' ', 1)[-1]
        elif spline[0].upper() == 'ERROR':
            print('\x1b[31;1mError: {}\x1b[0m'.format(' '.join(spline[1:])))
            return False
        elif spline[0].lstrip(':') == self.hostname:
            nick = None
            ident = spline[2]
            hostname = self.hostname
            command = spline[1]
            argument = spline[3]
            message = line.split(' ', 4)
        elif spline[2].upper() == 'PRIVMSG':
            nick = spline[0].split('!')[0]
            ident = spline[0].split('!', 1)[1].split('@')[0].lstrip('~')
            hostname = spline[0].split('@', 1)[1]
            command = spline[1]
            argument = spline[2]
            message = line.split(' ', 3)[-1]
        else:
            nick = None
            ident = None
            hostname = None
            command = None
            argument = None
            message = None

        for eh in self.eventHandlers:
            if eh.matches(nick, ident, hostname, command, argument, message):
                try:
                    eh.call(self, line, spline)
                except Exception as e:
                    print('\x1b[33;1mException:\x1b[0m {}'.format(e))
    ## END> def onNewline(self, line)

    def raw(self, line):
        self.s.send('{}\r\n'.format(line).encode('utf-8'))

    def statusOn(self, newStatus):
        """adds or updates self.status to True
            PARAM: <str>(newStatus - name of the status to set True)"""
        self.status[newStatus] = True
    ## END> statusOn(self, newStatus)

    def statusOff(self, oldStatus):
        """sets self.status[oldStatus] to false
            PARAM: <str>(oldStatus - name of the status to set False)"""
        self.status[oldStatus] = False
    ## END> statusOff(self, oldStatus)

    def getStatus(self, statusName):
        """gets the status based on statusName
            PARAM: <str>(statusName - name of the status to check for)
            RETURN: None OR <bool>"""
        return None if statusName not in self.status.keys()\
                    else self.status[statusName]
    ## END> getStatus(self, statusName)

    def __init__(self, **kwargs):
        """INIT for MintyBot
            PARAM: **kwargs"""

        """owner of the bot
            DEFAULT: None
            FORMAT: <str>"""
        self.owner = kwargs.get('owner', None)

        """visible nick of the bot
            DEFAULT: 'mintybot'
            FORMAT: <str>"""
        self.nick = kwargs.get('nick', 'mintybot_')

        """password used to identify with nickserv
            DEFAULT: None
            FORMAT: <str>
            NOTE: when self.password is None, bot doesn't try to identify"""
        self.password = kwargs.get('password', None)

        """realname that gets displayed in WHOIS, etc
            DEFAULT: '\x0303Minty\x03 Bot'
            FORMAT: <str>"""
        self.realname = kwargs.get('realname', '\x0303Minty\x03 Bot')

        """the ident of the bot
            DEFAULT: self.nick
            FORMAT: <str>"""
        self.ident = kwargs.get('ident', self.nick)

        """host to connect to
            DEFAULT: 'irc.freenode.net'
            FORMAT: <str>"""
        self.host = kwargs.get('host', 'irc.freenode.net')

        """port to connect to host with
            DFAULT: 6697
            FORMAT: <int>"""
        self.port = kwargs.get('port', 6697)

        """channels the bot is joined (initially it is what channels to join)
            DEFAULT: None
            FORMAT: <str> OR [<str>, ...]
            NOTE: when self.chans is None, the bot will simply quit"""
        self.chans = kwargs.get('chans', None)

        """message when bot joins each channel
            DEFAULT: None
            FORMAT: <str> OR None
            NOTE: when self.onJoin is None, the bot won't say anything after
                  joining"""
        self.onJoin = kwargs.get('onJoin', {})

        """directories that have modules for the bot
            DEFAULT: 'modules'
            FORMAT: <str> OR [<str>, ...]"""
        self.moduleDirs = kwargs.get('moduleDirs', ['modules'])

        """modules imported
            FORMAT: {<str> : <import_module>, ...}"""
        self.importedModules = {}

        """handlers for events
            FORMAT: [<module:EventHandler>, ...]
            NOTE: These may be added, but will be auto-added based on
                  self.moduleDirs"""
        self.eventHandlers = []

        """commands that require arguments
            FORMAT: <str>
            PRIVATE: Do not change"""
        self._requireArgs = ['PRIVMSG']

        """name of the host you connect to
            FORMAT: <str> OR None
            EXAMPLE: server.freenode.net"""
        self.hostname = None

        """indicates if the status is active
            FORMAT: {<str> : <bool>}
            NOTE: DO NOT ADD/REMOVE THESE YOURSELF
                  USE self.statusOn(<str>) and self.statusOff(<str>)"""
        self.status = {}

        """ssl socket used to speak to the host
            USES: socket.AF_INET, socket.SOCK_STREAM
            FORMAT: <module:wrap_socket>"""
        self.s = wrap_socket(socket(inet, stream)) # create ssl socket

        # reformat self.moduleDirs as a list if necessary
        if not isinstance(self.moduleDirs, list):
            self.moduleDirs = [self.moduleDirs]
        if 'modules' not in self.moduleDirs:
            self.moduleDirs.append('modules')

        # make sure self.chans is a list
        if self.chans is None:
            self.chans = []
        elif not isinstance(self.chans, list):
            self.chans = [self.chans]
    ## END> def __init__(self, **kwargs)
## END> class Bot()

if __name__ == '__main__':
    main()

