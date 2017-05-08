#!/usr/bin/env python2

from __future__ import with_statement
import os

history = u'/.pinebot_history'

#Retrieve API token from 'token' file
with open(u'token', u'r') as f:
    token = f.read().strip()

#List of available commands and description
available_commands = (
    u'/start\t:\tWelcome message to Pinebot',
    u'/help\t:\tShows this help message. Use /help modules for a list of available modules',
    u'/login\t:\tLogins chat to access privileged functions'
)

#List of available modules
available_modules = os.listdir('pineapple/modules')

shadow_file = '/etc/shadow'
