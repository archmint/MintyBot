#!/usr/bin/env python3

"""EventHandler to match nick, ident, hostname, command, argument and message
    for any parsed irc message"""

from re import compile as recompile, match as rematch

class EventHandler():
    """ Used to match search terms in order (using regex) and call a function handler"""
    def matches(self, nick, ident, hostname, command, argument, message):
        if nick is not None:
            if not rematch(self.nick, nick):
                return False
        if ident is not None:
            if not rematch(self.ident, ident):
                return False
        if hostname is not None:
            if not rematch(self.hostname, hostname):
                return False
        if command is not None:
            if not rematch(self.command, command):
                return False
        if argument is not None:
            if not rematch(self.argument, argument):
                return False
        if message is not None:
            if not rematch(self.message, message):
                return False
        return True

    def __init__(self, call, **kwargs):
        """EventHandler initialization

            PARAM: <func> function call for handling line when matched"""

        if not callable(call):
            raise RuntimeError

        self.nick = recompile(kwargs.get('nick', '.*'))
        """nick to match
            FORMAT: <module:regex>"""

        self.ident = recompile(kwargs.get('ident', '.*'))
        """ident to match
            FORMAT: <module:regex>"""

        self.hostname = recompile(kwargs.get('hostname', '.*'))
        """hostname to match
            FORMAT: <module:regex>"""

        self.command = recompile(kwargs.get('command', '.*'))
        """command to match
            FORMAT: <module:regex>"""

        self.argument = recompile(kwargs.get('argument', '.*'))
        """argument to match
            FORMAT: <module:regex>"""

        self.message = recompile(kwargs.get('message', '.*'))
        """message to match (this is the final part of the message)
            FORMAT: <module:regex>"""

        self.call = call
        """the function to call if there is a match
            FORMAT: <func>"""

def a(): print("A")

if __name__ == '__main__':
    ev = EventHandler(a, message='message')
    if ev.matches('archmint', 'ssdf', 'asff', 'PING', 'saffasdf', 'message'):
        a()
    print(__doc__)

