import logging
import re
from time import mktime, time, strftime

from config import properties
from config.properties import server_offset, log_name, database_offsets_file, database_temp_time_storage, \
    database_states_file, database_schedules_file, log_level

from db.persistence_storage import PersistenceStorage as Storage
from datetime import datetime
from db.sql_instance import SQLInstance
import config.utils
from lang.ua import error_date_in_past, error_after_2022, error_incorrect_date, error_incorrect_input


class PastDateError(Exception):

    def __init__(self, message):
        self.message = message
        super(PastDateError, self).__init__('{0}'.format(self.message))


class ParseError(Exception):

    def __init__(self, message):
        self.message = message
        super(ParseError, self).__init__('{0}'.format(self.message))


DATE_01_01_2022 = 1483218000
SECONDS_IN_DAY = 86401

regexp_time_zone = re.compile(r'([0-9]|[01][0-9]|2[0-3]):[0-5][0-9]')
regexp_date_enhanced = re.compile(r'([0-9]|[01][0-9]|2[0-3]):[0-5][0-9] ([0-2][0-9]|3[0-1]).([1-9]|0[1-9]|1[0-2]).(2['
                                  r'0-9][1-9][0-9])')

regexp_timezone = re.compile(r'0|[+-][0-9]|[+-]1[0-6]', re.MULTILINE)


def init_logger():
    global logger
    logger = logging.getLogger(log_name)
    logging.basicConfig(filename=log_name + '.log',
                        format='[%(asctime)s] %(filename)s:%(lineno)d %(levelname)s - %(message)s',
                        datefmt='%d.%m.%Y %H:%M:%S')
    if log_level:
        if log_level.lower() == 'debug':
            logger.setLevel(logging.DEBUG)
        elif log_level.lower() == 'info':
            logger.setLevel(logging.INFO)
        elif log_level.lower() == 'warn' or log_level.lower() == 'warning':
            logger.setLevel(logging.WARNING)
        elif log_level.lower() == 'error':
            logger.setLevel(logging.ERROR)
        else:
            logger.setLevel(logging.WARNING)
    else:
        logger.setLevel(logging.WARNING)


def init_storage():
    global offset_storage
    global time_storage
    global state_storage
    global db
    offset_storage = Storage(database_offsets_file)
    time_storage = Storage(database_temp_time_storage)
    state_storage = Storage(database_states_file)
    db = SQLInstance(database_schedules_file)


def get_logger():
    return logger


def get_offset_storage():
    return offset_storage


def get_time_storage():
    return time_storage


def get_state_storage():
    global state_storage
    return state_storage


def get_database():
    global db
    return db


def close_storage():
    get_time_storage().close()
    get_state_storage().close()
    get_offset_storage().close()
    db.close()


def get_unix_time_from_date(date_string):
    return int(mktime(datetime.strptime(date_string, '%H:%M %d.%m.%Y').timetuple()))


def get_user_date(offset):
    return datetime.fromtimestamp(int(time()) + (3600 * offset) - (3600 * server_offset)).strftime('%d.%m.%Y')


def convert_user_time_to_local(text, offset):
    if offset == 0:
        return text
    return datetime.fromtimestamp(config.utils.get_unix_time_from_date(text) - (3600 * offset)).strftime('%H:%M %d.%m.%Y')


def convert_user_time_to_at_command(text, offset):
    if int(offset) == server_offset:
        return text
    elif int(offset) > server_offset:
        return strftime('{0!s} - {1!s} hours'.format(text, offset - server_offset))
    elif int(offset) < server_offset:
        return strftime('{0!s} + {1!s} hours'.format(text, -offset + server_offset))


def convert_user_time_to_local_timestamp(text, offset):
    return config.utils.get_unix_time_from_date(text) - (3600 * offset)


def is_valid_datetime(text, offset):
    try:
        entered_time = config.utils.get_unix_time_from_date(text)
        if (entered_time - (3600 * offset)) < (time() - (3600 * server_offset)):
            raise PastDateError(error_date_in_past)
        if entered_time > DATE_01_01_2022:
            raise ParseError(error_after_2022)
    except ValueError:
        raise ParseError(error_incorrect_date)
    except OverflowError:
        raise ParseError(error_incorrect_input)
    return True


def parse_time(text, user_timezone):
    global time_regexp
    if re.search(config.utils.regexp_date_enhanced, text) is not None:
        txt = re.search(config.utils.regexp_date_enhanced, text).group()
        if is_valid_datetime(txt, user_timezone):
            return txt
        else:
            raise ParseError(error_incorrect_input)
    else:
        if re.search(time_regexp, text) is not None:
            time_with_date = \
                str(re.search(time_regexp, text).group()) + ' ' + get_user_date(user_timezone)
            if is_valid_datetime(time_with_date, user_timezone):
                return time_with_date
            else:
                raise ParseError(error_incorrect_input)


def parse_time_zone(text):
    global regex
    match_results = re.search(regex, text.lstrip())
    if match_results is None:
        try:
            num = int(text.lstrip())
            if -16 < num < 16:
                return num
            else:
                return None
        except RuntimeError:
            get_logger().warning('Could not recognize timezone: {0!s}'.format(text.lstrip()))
            return None
    else:
        return int(match_results.group())


if __name__ == '__main__':
    print(get_user_date(5))
    pass
