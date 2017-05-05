#!/usr/bin/env python3

import telebot
import logging
import signal
from subprocess import Popen, PIPE

history = '/.pinebot_history'

#Retrieve API token from 'token' file
with open('token', 'r') as f:
    token = f.read().strip()
assert(token)

#Start the bot
bot = telebot.AsyncTeleBot(token)

#Create log files
logging.basicConfig(filename='pinebot.log', format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG)

#List of authorized chats
authorized = set()

#List of available commands and description
available_commands = (
    '/start\t:\tStarts the bot',
    '/help\t:\tShows this help message',
    '/download_history\t:\tDownloads message history'
)

#Insensitive case function name comparer
def check_function_name(name):
    def compare(message):
        return '/' + name == message.text.split(' ')[0].lower()
    return compare

#Asynchronous reply with wait
def reply(message, text):
    reply = bot.reply_to(message, text)
    reply.wait()

#Check authorization decorator
def check_authorization(func):
    def checker(message):
        logging.debug('Checking authorization of chat_id:' + str(message.chat.id))
        logging.debug('Current authorized chats:' + '\n'.join(map(str, authorized)))
        if message.chat.id not in authorized:
            #Here we don't use the custom `reply` method to actually log the warning in case of failure
            reply = bot.reply_to(message, 'You\'re not authorized, please /login')
            logging.warning('Chat id: ' + str(message.chat.id) + ' attempted to use functionality: ' + str(message.text) + ' without being authorized')
            reply.wait()
        else:
            logging.debug('Chat authorized')
            func(message)
    return checker

def download_document(message):
    return bot.download_file(bot.get_file(message.document.file_id).file_path)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    logging.debug('Receiver start message')
    reply(message, 'Welcome to the pineapple telegram bot')
    
    
@bot.message_handler(commands=['help'])
def send_help(message):
    logging.debug('Received help message')
    reply(message, '\n'.join(available_commands))

@bot.message_handler(commands=['download_history'])
@check_authorization
def send_file(message):
    logging.debug('Received download_history message')
    with open(history) as f:
        bot.send_document(message.chat.id, f)
    logging.info('History sent')

@bot.message_handler(content_types=['document'])
@check_authorization
def receive_config(message):
    logging.debug('Receiving config file')
    #nombre = message.text.split(' ')[1]
    with open('.config', 'wb') as config:
        config.write(download_document(message))
    logging.info('Config received')
    reply(message, 'Config received')

@bot.message_handler(commands=['login'])
def login(message):
    logging.debug('Login user')
    try: 
        key = message.text.split(' ')[1]
    except:
        logging.debug('Login attempt without key')
        reply(message, 'Key is needed. Ex: /login key')
        return
    if key == 'password': #TODO: Implement proper password check
        logging.info('Authorized chat id:' + str(message.chat.id))
        authorized.add(message.chat.id)
        reply(message, 'Login succesful')
    else:
        logging.info('Authorization failure')
        reply(message, 'Login failure')

@bot.message_handler(func=check_function_name('pineap'))
@check_authorization
def pine_ap(message):
    logging.debug('Running PineAP')
    cmd = ['python', 'pineapple/modules/PineAP/executable/executable']
    cmd.extend(message.text.split(' ')[1:])
    logging.info('Running PineAP with the following parameters: ' + ' '.join(cmd))
    with Popen(cmd, stdout=PIPE, stderr=PIPE) as pineap:
        logging.debug('Starting PineAP thread')
        (out, err) = pineap.communicate()
        pineap.wait()
        logging.debug('PineAP output: ' + out.decode() + '\nPineAP err :' + err.decode())
        reply(message, out.decode() if not err else err.decode())

def main():
    try:
        bot.polling(none_stop=False, interval=0)
    except Exception as e:
        logging.critical(e)
        exit(-1)

if __name__ == '__main__':
    signal.signal(signal.SIGINT, exit) #Workaround to deal with bot.polling being a blocking call
    main()
