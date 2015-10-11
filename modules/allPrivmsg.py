#!/usr/bin/env python3

def allMsg(bot, raw, spline):
    chan = spline[2]
    if raw.split(' ', 3)[-1].lstrip(':').rstrip('.,?!:- ').lower() in ('hi', 'hello', 'what\'s up'):
        bot.raw('PRIVMSG {} :hi'.format(chan))

allMsg.command='PRIVMSG'
