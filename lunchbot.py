from collections import defaultdict
from datetime import (
    datetime,
    timedelta,
)

import yaml

from util import parse_time, format_timedelta

from random import choice

import time

from ircbot import (
    IRCBot,
    response,
    command,
)

class LunchBot(IRCBot):
    def __init__(self, *args, **kwargs):
        super(LunchBot, self).__init__(*args, **kwargs)
        self.timers = defaultdict(dict)

    @response(trigger='botsnack')
    def botsnack(self, channel, user, message):
        return choice([":)", ":3", "thanks!", "tasty!"])

    @response(trigger='botsmack')
    def botsmack(self, channel, user, message):
        return choice(["mm", "channel for that :)"])

    @response(trigger='<3')
    def heart(self, channel, user, message):
        return '<3'

    @command(trigger='source')
    def source(self, channel, user, message):
        return "I live at https://github.com/rpearl/lunchbot"

    @command(trigger='time')
    def add_timer(self, channel, user, message):
        """ Add a timer"""
        when, sep, msg = message.partition(' ')
        delta = parse_time(when)
        if delta is None:
            return "'%s' does not parse as a time" % (when,)

        if msg in self.timers[user]:
            return "there is already a timer for %s" % (msg,)

        end = "timer for " + choice(["%s is done", "%s is ready", "%s is finished"]) % msg
        try:
            end_time = datetime.now()+delta
        except:
            return "Invalid date. Stop that."
        end_ts = time.mktime(end_time.timetuple())

        def response():
            self.reply(channel, user, end)
            del self.timers[user][msg]

        cb = self.io_loop.add_timeout(end_ts, response)
        self.timers[user][msg] = (cb, end_ts)
        return "okay! starting %s timer for %s." % (format_timedelta(delta), msg)

    @command(trigger='list')
    def list_timers(self, channel, user, message):
        """List all your timers"""
        s = []
        for msg, (cb, end_time) in self.timers[user].iteritems():
            done = timedelta(seconds=int(end_time - time.time()))
            out = "%s in %s" % (msg, format_timedelta(done))
            s.append((done, out))
        if s:
            out = [e[1] for e in sorted(s, key=lambda e:e[0])]
            return 'you have the following timers: %s' % (', '.join(out),)
        else:
            return 'you have no timers running.'

    @command(trigger='cancel')
    def cancel_timer(self, channel, user, message):
        """Cancels a timer"""
        if message not in self.timers[user]:
            return "you don't have a timer for %s!" % (message,)
        cb, _ = self.timers[user][message]
        self.io_loop.remove_timeout(cb)
        del self.timers[user][message]
        return "Okay, removing timer for %s." % (message,)


if __name__ == '__main__':
    with open('bot.yaml') as f:
        config = yaml.load(f)
    c = LunchBot(config['name'], owner=config['owner'])
    server = config['server']
    c.start(server['host'], server['port'], channels=server['channels'])
