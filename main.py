import threading
import queue
import logging
import traceback
import sys
try:
    from bot_rp_finder.menu import menu
    from bot_rp_finder.menu.execute_time import Timer
    from bot_rp_finder.vk_api import vk_api, longpoll, msg_send
    from bot_rp_finder.vk_api.Keys import Keys
    from bot_rp_finder.database import db_api
    from bot_rp_finder.dropbox_api import dropbox_backup
    from bot_rp_finder.menu import notification
except:
    sys.path.append('../')
    from bot_rp_finder.menu import menu
    from bot_rp_finder.menu.execute_time import Timer
    from bot_rp_finder.vk_api import vk_api, longpoll, msg_send
    from bot_rp_finder.vk_api.Keys import Keys
    from bot_rp_finder.database import db_api
    from bot_rp_finder.dropbox_api import dropbox_backup
    from bot_rp_finder.menu import notification


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
            if not db_api.User().get_user(msg['from_id']):
                user_info = bot_api.get_user_info(msg['from_id'])
                db_api.User().create_user(user_id=user_info['id'],
                                          name=user_info['first_name'],
                                          is_fem=user_info['sex'] % 2)
                bot_message = menu.main(msg)

            else:
                timer.start(msg.get('payload', {}).get('m_id', 'None'))
                bot_message = menu.menu_hub(msg)
                timer.time_stamp(msg.get('payload', {}).get('m_id', 'None'))

            actions = vk_api.get_actions_from_buttons(bot_message['keyboard'])
            db_api.AvailableActions().update_actions(msg['from_id'], actions)
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

