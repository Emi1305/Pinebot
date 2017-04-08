import telebot
from time import sleep


token = <TOKEN> #gitignore Replace with your token

bot = telebot.TeleBot(token)

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, 'Buenas wachin')
    with open('/home/deb/Documents/pinebot_messages', 'a+') as f:
        f.write(message.text)
        f.write('\n')

@bot.message_handler(commands=['archivo'])
def send_file(message):
    with open('/home/deb/Documents/pinebot_messages', 'r+') as f:
        bot.send_document(message.chat.id, f)
        f.write(message.text)
        f.write(help(message))
        f.write('\n')

@bot.callback_query_handler(func=lambda call: True)
def test_callback(call):
    with open('/home/deb/Documents/pinebot_messages', 'a+') as f:
        f.write('Aca empieza la call:\n')
        f.write(call)
        f.write('\n')
    sleep(3)
    send_file(call)

bot.polling()
