import telebot
from time import sleep
import os 

with open(os.getcwd() + 'token', 'r') as f:
    token = f.read()

log = os.getcwd() + '.pinebot_history'
bot = telebot.TeleBot(token)

available_commands = (
    '/start\t:\tStarts the bot',
    '/help\t:\tShows this help message',
    '/download_history\t:\tDownloads message history'
)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, 'Welcome to the pineapple telegram bot')
    with open(log, 'a+') as f:
        f.write(message.text)
        f.write('\n')

@bot.message_handler(commands=['help'])
def send_help(message):
    bot.reply_to(message, '\n'.join(available_commands))

@bot.message_handler(commands=['download_history'])
def send_file(message):
    with open(log, 'r+') as f:
        bot.send_document(message.chat.id, f)
        f.write(message.text)
        f.write('\n')

bot.polling()
