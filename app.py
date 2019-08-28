import signal
import sys
from pprint import pprint
from time import sleep

import telebot

from config import utils
from config.properties import token, database_schedules_file, lang
from config.utils import init_storage, get_logger, init_logger, get_offset_storage, get_state_storage
from lang.en import error_maximum_number_of_notes
from lang.ua import common_welcome_text, common_guide_time
from config.states import *
from db.sql_instance import SQLInstance

bot = telebot.TeleBot(token=token)
global offset_storage
global logger
global state_storage


def signal_handler(signal, frame):
    logger.info('Signal cached, closing database')
    print('Signal cached, closing database')
    utils.close_storage()
    sys.exit(0)


def set_new_state(chat_id, state_name):
    state_storage.save(str(chat_id), state_name, force_save=True)


@bot.message_handler(commands=['start'])
def cmd_start_handler(msg):
    logger.debug(
        'User {0!s} started new chat with bot'.format(str(msg.from_user.username) + ' (' + str(msg.chat.id) + ')'))
    set_new_state(msg.chat.id, States.STATE_START)
    bot.send_message(msg.chat.id, common_welcome_text)


@bot.message_handler(commands=['new_event'])
def cmd_new_alarm(msg):
    db = SQLInstance(database_schedules_file)
    pprint(msg)
    print(msg)
    # if db.count_entries_for_id(msg.chat.id) == 5 and int(msg.chat.id):
    #     bot.send_message(msg.chat.id, error_maximum_number_of_notes)
    #     db.close()
    #     return None

    set_new_state(msg.chat.id, States.STATE_NEW_EVENT)

    if not offset_storage.exists(str(msg.chat.id)):
        logger.debug('User {0!s} is going to set new alarm. It\'s his first appear'.format(
            str(msg.from_user.username) + ' (' + str(msg.chat.id) + ')'))
        set_new_state(msg.chat.id, States.STATE_SETTING_TIMEZONE_FOR_EVENT)
        bot.send_message(msg.chat.id, lang.common_guide_timezone)
    # if we already have his timezone saved - ask him to set time
    else:
        logger.debug('User {0!s} is going to set new alarm. He has been here before'.format(
            str(msg.from_user.username) + ' (' + str(msg.chat.id) + ')'))
        set_new_state(msg.chat.id, States.STATE_SETTING_TIME)
        bot.send_message(msg.chat.id, common_guide_time)


if __name__ == '__main__':
    init_logger()
    logger = get_logger()
    logger.debug('Logger started')
    init_storage()
    offset_storage = get_offset_storage()
    state_storage = get_state_storage()
    signal.signal(signal.SIGINT, signal_handler)
    bot.polling(none_stop=True)
    while True:
        sleep(60)
        pass
