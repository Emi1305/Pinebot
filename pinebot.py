#!/usr/bin/env python2

from __future__ import with_statement
from __future__ import absolute_import
from subprocess import Popen, PIPE
from io import open
from itertools import imap

import crypt
import telebot
import logging
import signal
import config


#Start the bot
bot = telebot.AsyncTeleBot(config.token)

#Create log files
logging.basicConfig(filename=u'pinebot.log', format=u'%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG)

#List of authorized chats
authorized = set()

#Insensitive case function name comparer
def check_function_name(name):
    def compare(message):
        return u'/' + name == message.text.split(u' ')[0].lower()
    return compare

#Asynchronous reply with wait
def reply(message, text):
    reply = bot.reply_to(message, text)
    reply.wait()

#Check authorization decorator
def check_authorization(func):
    def checker(message):
        logging.debug(u'Checking authorization of chat_id:' + unicode(message.chat.id))
        logging.debug(u'Current authorized chats:' + u'\n'.join(imap(unicode, authorized)))
        if message.chat.id not in authorized:
            #Here we don't use the custom `reply` method to actually log the warning in case of failure
            reply = bot.reply_to(message, u'You\'re not authorized, please /login')
            logging.warning(u'Chat id: ' + unicode(message.chat.id) + u' attempted to use functionality: ' + unicode(message.text) + u' without being authorized')
            reply.wait()
        else:
            logging.debug(u'Chat authorized')
            func(message)
    return checker

#Check user and password against shadow
def check_passwd(user, password):
    def get_salt(hash):
        hash = hash.split(u'$')
        return u'$' + u'$'.join(hash[1:3] if len(hash) == 3 else hash[1:4]) + u'$'
    with open(config.shadow_file, 'r') as shadow:
        for line in shadow:
            if line.startswith(user):
                hashed = line.split(u':')[1]
                salt = get_salt(hashed)
                h = crypt.crypt(password, salt)
                equal = True
                for i, j in zip(h, hashed):
                    equal &= i==j
                return equal

def download_document(message):
    return bot.download_file(bot.get_file(message.document.file_id).file_path)

@bot.message_handler(commands=[u'start'])
def send_welcome(message):
    logging.debug(u'Receiver start message')
    reply(message, u'Welcome to the pineapple telegram bot, enter /help for a list of useful commands. Remember to use a private chat')
    
@bot.message_handler(commands=[u'help'])
def send_help(message):
    logging.debug(u'Received help message')
    try:
        if message.text.split(u' ')[1] == 'modules':
            reply(message, u'\n'.join(config.available_modules))
    except:
        reply(message, u'\n'.join(config.available_commands))

@bot.message_handler(commands=[u'download_history'])
@check_authorization
def send_file(message):
    logging.debug(u'Received download_history message')
    with open(history) as f:
        bot.send_document(message.chat.id, f)
    logging.info(u'History sent')

@bot.message_handler(content_types=[u'document'])
@check_authorization
def receive_config(message):
    logging.debug(u'Receiving config file')
    #nombre = message.text.split(' ')[1]
    with open(u'.config', u'wb') as config:
        config.write(download_document(message))
    logging.info(u'Config received')
    reply(message, u'Config received')

@bot.message_handler(commands=[u'login'])
def login(message):
    logging.debug(u'Login user')
    if message.chat.type != 'private':
        reply(message, u'Login is only available in private chats')
        return
    try: 
        user, key = message.text.split(u' ')[1], message.text.split(u' ')[2]
    except:
        logging.debug(u'Login attempt without user or key')
        reply(message, u'User and Key are needed. Ex: /login user key')
        return
    if check_passwd(user, key): #TODO: Implement proper password check
        logging.info(u'Authorized chat id:' + unicode(message.chat.id))
        authorized.add(message.chat.id)
        reply(message, u'Login succesful. For security we recommend to delete your login message.')
    else:
        logging.info(u'Authorization failure: user')
        reply(message, u'Login failure')

@bot.message_handler(func=check_function_name(u'pineap'))
@check_authorization
def pine_ap(message):
    logging.debug(u'Running PineAP')
    cmd = [u'python', u'pineapple/modules/PineAP/executable/executable']
    cmd.extend(message.text.split(u' ')[1:])
    logging.info(u'Running PineAP with the following parameters: ' + u' '.join(cmd))
    pineap = Popen(cmd, stdout=PIPE, stderr=PIPE)
    logging.debug(u'Starting PineAP thread')
    (out, err) = pineap.communicate()
    pineap.wait()
    logging.debug(u'PineAP output: ' + out.decode() + u'\nPineAP err: ' + err.decode())
    reply(message, out.decode() if not err else err.decode())

def main():
    assert(config.token)
    try:
        bot.polling(none_stop=False, interval=0)
    except Exception, e:
        logging.critical(e)
        exit(-1)

if __name__ == u'__main__':
    signal.signal(signal.SIGINT, exit) #Workaround to deal with bot.polling being a blocking call
    main()
