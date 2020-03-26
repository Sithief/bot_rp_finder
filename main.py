import threading
import queue
import logging
import traceback
import sys
from menu import menu, user_profile
from menu.execute_time import Timer
from vk_api import vk_api, longpoll, msg_send
from vk_api.Keys import Keys
from database import db_api
from dropbox_api import dropbox_backup
from menu import notification
from menu.token import Token


def init_logging():
    logging.basicConfig(
        format='%(filename)-25s[LINE:%(lineno)d]# %(levelname)-8s [%(asctime)s]  %(message)s',
        # level=logging.INFO,
        level=logging.DEBUG,
        datefmt='%m-%d %H:%M',
        filename='log/bot.log',
        filemode='w'
    )
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    formatter = logging.Formatter('%(name)-12s: %(levelname)-8s %(message)s')
    console.setFormatter(formatter)
    logging.getLogger('').addHandler(console)


def foo(exctype, value, tb):
    import logging
    import time
    init_logging()
    logging.critical(f'EXCEPTION: Type: {exctype}, Value: {value}')
    with open('log/bot_errors.log', 'w') as error_file:
        error_file.write(time.asctime() + '\n')
        traceback.print_exception(exctype, value, tb, file=error_file)


def init_messages_get_thread():
    logging.info('init new longpoll thread')
    stdin = queue.Queue()
    listner = threading.Thread(target=longpoll.listen, args=(stdin,))
    listner.start()
    return stdin, listner


def init_messages_send_threads(count):
    logging.info('init new longpoll thread')
    stdout = queue.Queue()
    senders = list()
    for i in range(count):
        sender = threading.Thread(target=msg_send.send, args=(stdout,))
        sender.start()
        senders.append(sender)
    return stdout, senders


if __name__ == '__main__':
    init_logging()
    sys.excepthook = foo
    dropbox_backup.backup_db()

    if 'update_db' in sys.argv:
        db_api.update_db()

    bot_api = vk_api.Api(Keys().get_group_token(), 'main')
    if not bot_api.valid:
        logging.error('Токен для VK API не подходит')
        exit(1)

    admin_list = bot_api.get_admins()
    db_api.init_db()
    db_api.update_admins(admin_list)

    long_poll_stdout, long_poll_listner = init_messages_get_thread()
    msg_send_stdin, msg_senders = init_messages_send_threads(5)

    changes_count = 0

    timer = Timer()

    while 1:
        try:
            new_messages = long_poll_stdout.get(timeout=120)
        except queue.Empty:
            long_poll_stdout, long_poll_listner = init_messages_get_thread()
            continue

        timer.start('total')
        for msg in new_messages:
            print('usr msg:', msg)
            user_token = Token(msg)
            if not user_token.info:
                vk_user_info = bot_api.get_user_info(msg['from_id'])
                try:
                    user_info = db_api.User().create_user(user_id=vk_user_info['id'],
                                                          name=vk_user_info['first_name'],
                                                          is_fem=vk_user_info['sex'] % 2)
                    user_token.update_user_info(user_info, msg)
                except:
                    continue

            timer.start(user_token.menu_id)
            bot_message = menu.menu_hub(user_token)
            timer.time_stamp(user_token.menu_id)

            actions = vk_api.get_actions_from_buttons(bot_message['keyboard'])
            db_api.AvailableActions().update_actions(msg['from_id'], actions)

            if user_token.menu_id == 'save_images':
                msg_id = bot_api.msg_send(msg['peer_id'], bot_message)
                if msg_id:
                    message = bot_api.msg_get(msg_id)
                    user_profile.update_images(message)
            else:
                msg_send_stdin.put((msg['peer_id'], bot_message))

        if new_messages:
            timer.time_stamp('total')
            changes_count += 1
            logging.info(timer.quick_stat('total'))

        elif changes_count > 1:
            timer.output()
            changes_count = 0
            timer.start('dropbox')
            dropbox_backup.backup_db()
            timer.time_stamp('dropbox')

            timer.start('new notifications')
            notification.send_unread_notifications(bot_api)
            timer.time_stamp('new notifications')

