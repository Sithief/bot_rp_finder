import time
import multiprocessing
import logging
from bot_rp_finder.menu import menu
from bot_rp_finder.vk_api import vk_api, longpoll
from bot_rp_finder.vk_api.Keys import Keys
from bot_rp_finder.database import user_class

logging.basicConfig(format='%(filename)-15s[LINE:%(lineno)d]# %(levelname)-8s [%(asctime)s]  %(message)s',
                    level=logging.DEBUG)


if __name__ == '__main__':
    bot_api = vk_api.Api(Keys().get_group_token(), 'main')

    user_class.init_db()

    longpoll_stdout = multiprocessing.Queue()
    longpoll_listner = multiprocessing.Process(target=longpoll.listen, args=(longpoll_stdout,))
    longpoll_listner.start()
    last_message_time = time.time()
    while 1:
        new_messages = longpoll_stdout.get(timeout=120)
        for msg in new_messages:
            print('usr msg:', msg)
            if not user_class.get_user(msg['from_id']):
                user_info = bot_api.get_user_info(msg['from_id'])
                user_class.create_user(user_id=user_info['id'],
                                       name=user_info['first_name'],
                                       is_fem=user_info['sex'] % 2)

            bot_message = menu.menu_hub(msg)
            print('bot msg:', bot_message)
            print()
            bot_api.msg_send(peer_id=msg['from_id'], payload=bot_message)
