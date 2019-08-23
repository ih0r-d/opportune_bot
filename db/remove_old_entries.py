from config.properties import database_schedules_file, log_name
from db.sql_instance import SQLInstance
from time import time
import logging

db = SQLInstance(database_schedules_file)

logger = logging.getLogger(log_name)
logging.basicConfig(filename=log_name + '.log',
                    format='[%(asctime)s] OLD_REMOVER %(levelname)s - %(message)s',
                    datefmt='%d.%m.%Y %H:%M:%S')
logger.setLevel(logging.INFO)

try:
    number_of_deleted = db.delete_old(int(time())).rowcount
    logger.info('Finished processing old rows. Rows deleted: {0!s}'.format(number_of_deleted))
except Exception as ex:
    logger.error('Failed to process old rows: {0!s}'.format(str(ex)))
