#!/usr/bin/env python3

def ping(bot, raw, spline):
    bot.raw('PONG :{}'.format(raw.split(' ', 1)[-1]))

ping.command='PING'
