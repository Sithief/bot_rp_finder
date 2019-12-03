import threading
import queue
import logging
import sys
sys.path.append('../')
from bot_rp_finder.menu import menu
from bot_rp_finder.menu.execute_time import Timer
from bot_rp_finder.vk_api import vk_api, longpoll
from bot_rp_finder.vk_api.Keys import Keys
from bot_rp_finder.database import user_class
from bot_rp_finder.dropbox_api import dropbox_backup


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
    init_logging()
    logging.critical(f'EXCEPTION: Type: {exctype}, Value: {value}')
    longpoll_listner.join(timeout=1)


if __name__ == '__main__':
    init_logging()
    sys.excepthook = foo
    dropbox_backup.backup_db()
    bot_api = vk_api.Api(Keys().get_group_token(), 'main')
    if not bot_api.valid:
        logging.error('Токен для VK API не подходит')
        exit(1)

    admin_list = bot_api.get_admins()
    user_class.init_db()
    user_class.update_admins(admin_list)

    longpoll_stdout = queue.Queue()
    longpoll_listner = threading.Thread(target=longpoll.listen, args=(longpoll_stdout,))
    longpoll_listner.start()

    changes_count = 0

    timer = Timer()

    while 1:
        new_messages = longpoll_stdout.get(timeout=120)
        timer.start('total')
        for msg in new_messages:
            print('usr msg:', msg)
            if not user_class.User().get_user(msg['from_id']):
                user_info = bot_api.get_user_info(msg['from_id'])
                user_class.User().create_user(user_id=user_info['id'],
                                              name=user_info['first_name'],
                                              is_fem=user_info['sex'] % 2)
                bot_message = menu.main(msg)

            else:
                timer.start(msg.get('payload', {}).get('m_id', 'None'))
                bot_message = menu.menu_hub(msg)
                timer.time_stamp(msg.get('payload', {}).get('m_id', 'None'))

            timer.start('msg_send')
            bot_api.msg_send(peer_id=msg['from_id'], payload=bot_message)
            timer.time_stamp('msg_send')

        if new_messages:
            timer.time_stamp('total')
            timer.output()
            changes_count += 1

        elif changes_count > 10:
            changes_count = 0
            timer.start('dropbox')
            dropbox_backup.backup_db()
            timer.time_stamp('dropbox')

