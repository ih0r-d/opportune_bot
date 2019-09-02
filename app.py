import signal
import sys
from pprint import pprint
from time import sleep

import telebot

from config import utils
from config.properties import token, database_schedules_file, lang
from config.utils import init_storage, get_logger, init_logger, get_offset_storage, get_state_storage, set_new_at_job, \
    get_time_storage, parse_time, PastDateError, ParseError
from lang.ua import common_welcome_text, common_guide_time, common_is_time_correct, common_guide_timezone
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
    # db = SQLInstance(database_schedules_file)
    pprint(msg)
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


@bot.message_handler(commands=['set_offset'])
def cmd_set_offset(message):
    logger.debug('User {0!s} is going to set offset'.format(
        str(message.from_user.username) + ' (' + str(message.chat.id) + ')'))
    set_new_state(message.chat.id, States.STATE_SETTING_TIMEZONE_SEPARATE)
    bot.send_message(message.chat.id, common_guide_timezone)


# If cancel - reset state
@bot.message_handler(commands=['cancel'])
def cmd_cancel(message):
    set_new_state(message.chat.id, States.STATE_START)
    logger.debug('User {0!s} cancelled current task'.format(
        str(message.from_user.username) + ' (' + str(message.chat.id) + ')'))
    bot.send_message(message.chat.id, lang.common_cancel)


@bot.message_handler(func=lambda message: state_storage.get(str(message.chat.id)) in [
    States.STATE_SETTING_TIMEZONE_SEPARATE, States.STATE_SETTING_TIMEZONE_FOR_EVENT])
def cmd_update_timezone_for_user(message):
    timezone = utils.parse_time_zone(message.text)
    if timezone is None:
        # "Could not recognize timezone"
        bot.send_message(message.chat.id, lang.error_timezone_not_recognized)
        set_new_state(message.chat.id, States.STATE_SETTING_TIMEZONE_FOR_EVENT)
        return None
    else:
        logger.debug('User {1!s} set timezone: {0!s}'.format(timezone,
                                                             str(message.from_user.username) + ' (' + str(
                                                                 message.chat.id) + ')'))
        offset_storage.save(key=str(message.chat.id), value=timezone, force_save=True)
        if state_storage.get(str(message.chat.id)) == States.STATE_SETTING_TIMEZONE_FOR_EVENT:
            bot.send_message(message.chat.id, lang.common_guide_time)
            set_new_state(message.chat.id, States.STATE_SETTING_TIME)
        if state_storage.get(str(message.chat.id)) == States.STATE_SETTING_TIMEZONE_SEPARATE:
            logger.info('Timezone successfully saved')
            bot.send_message(message.chat.id, lang.common_timezone_set)
            set_new_state(message.chat.id, States.STATE_START)


# User is setting time
@bot.message_handler(func=lambda message: state_storage.get(
    str(message.chat.id)) == States.STATE_SETTING_TIME)
def cmd_set_time(message):
    global time
    global error_msg

    # Check if timezone already set
    if not offset_storage.exists(str(message.chat.id)):
        'No offset storage'
        logger.warning('Whoa! It looks like {0!s} hasn\'t set offset yet! What a shame!'.format(
            str(message.from_user.username) + ' (' + str(message.chat.id) + ')'))
        bot.send_message(message.chat.id, lang.error_timezone_not_set)
        set_new_state(message.chat.id, States.STATE_SETTING_TIMEZONE_FOR_EVENT)
        return None
    timezone = offset_storage.get(str(message.chat.id))
    time = None
    error_msg = None
    try:
        time = parse_time(message.text, int(timezone))
    except PastDateError as ex:
        error_msg = str(ex)
    except ParseError as ex:
        error_msg = str(ex)
    else:
        pass
    # If there was an error getting time
    if time is None:
        logger.warning(
            'User {0!s} set incorrect time: {1!s}'.format(
                str(message.from_user.username) + ' (' + str(message.chat.id) + ')', message.text))
        if error_msg is None:
            # "Could not recognize timezone. Please try again"
            bot.send_message(message.chat.id, lang.error_time_not_recognized)
        else:
            bot.send_message(message.chat.id, error_msg)
        set_new_state(message.chat.id, States.STATE_SETTING_TIME)
    else:
        logger.debug('User {0!s} set time: {1!s}'.format(
            str(message.from_user.username) + ' (' + str(message.chat.id) + ')', time))
        get_time_storage().save(str(message.chat.id), time, force_save=True)
        set_new_state(message.chat.id, States.STATE_SETTING_TEXT)
        bot.send_message(message.chat.id, common_is_time_correct.format(time))
        pass


# User is satisfied with time and is going to save new note
@bot.message_handler(func=lambda message: state_storage.get(
    str(message.chat.id)) == States.STATE_SETTING_TEXT)
def cmd_save_text(message):
    if len(message.text) > 1000:
        bot.send_message(message.chat.id, lang.error_note_too_long)
        return None
    global offset_storage

    # Check, if message starts with bot mention -> remove it
    if message.text.startswith(r'@'):
        message.text = ' '.join(message.text.split()[1:])

    # Convert user's time to server's local time to set "at" command taking offset into account
    time_to_set = utils.convert_user_time_to_at_command(utils.get_time_storage().get(str(message.chat.id)),
                                                        offset_storage.get(key=str(message.chat.id)))
    logger.debug('User {0!s} is going to set time: {1!s}'.format(
        str(message.from_user.username) + ' (' + str(message.chat.id) + ')', time_to_set))
    # Get unix time to set to SQLite DB
    unix_time_to_save_to_db = utils.convert_user_time_to_local_timestamp(
        utils.get_time_storage().get(str(message.chat.id)), offset_storage.get(str(message.chat.id)))
    # Set "at" command and receive Job ID from it
    job_id = set_new_at_job(message.chat.id, time_to_set, message.text.replace('"', r'\"'))
    # If not job id provided (error happened or something else)
    if not job_id:
        bot.send_message(message.chat.id, lang.error_could_not_save_note)
        return None
    logger.info('Successfully set reminder #{0!s} at {1!s}'.format(job_id, time_to_set))
    # Insert new row in table
    db = SQLInstance(database_schedules_file)
    db.insert(message.chat.id, unix_time_to_save_to_db, job_id)
    db.close()
    bot.send_message(message.chat.id, lang.common_note_added.format(
        utils.get_time_storage().get(str(message.chat.id))))
    # After setting note, reset to START
    set_new_state(message.chat.id, States.STATE_START)


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
