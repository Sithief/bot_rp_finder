import configparser
import time
import traceback
import sys
import os
import logging
from logging.handlers import RotatingFileHandler
from vk_api import vk_api


def init_logging():
    log_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'log')
    if not os.path.exists(log_path):
        os.makedirs(log_path)
    logging.basicConfig(
        handlers=[RotatingFileHandler(os.path.join(log_path, 'my_log.log'), maxBytes=100000, backupCount=10)],
        format='%(filename)-25s[LINE:%(lineno)d]# %(levelname)-8s [%(asctime)s]  %(message)s',
        level=logging.DEBUG,
        datefmt='%m-%d %H:%M',
    )
    # console = logging.StreamHandler()
    # console.setLevel(logging.INFO)
    # formatter = logging.Formatter('%(name)-12s: %(levelname)-8s %(message)s')
    # console.setFormatter(formatter)
    # logging.getLogger('').addHandler(console)


def foo(exctype, value, tb):
    import logging
    import time
    init_logging()
    logging.critical(f'EXCEPTION: Type: {exctype}, Value: {value}')
    log_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'log')
    if not os.path.exists(log_path):
        os.makedirs(log_path)
    with open(os.path.join(log_path, 'bot_errors.log'), 'w') as error_file:
        error_file.write(time.asctime() + '\n')
        traceback.print_exception(exctype, value, tb, file=error_file)


uptime = time.time()
timers = list()
events = list()
current_path = os.path.dirname(os.path.abspath(__file__))
CONF = configparser.ConfigParser()
CONF.read(os.path.join(current_path, 'bot_settings.inf'), encoding='utf-8')
init_logging()
sys.excepthook = foo
bot_api = vk_api.Api(CONF.get('VK', 'token', fallback='no confirm'), 'main')
if not bot_api.valid:
    logging.error('Токен для VK API не подходит')
    exit(1)
