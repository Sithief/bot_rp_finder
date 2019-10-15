import requests
import time
import multiprocessing
import menu
import longpoll
import vk_api
import user_class
import os
from Keys import Keys


if __name__ == '__main__':
    bot_api = vk_api.Api(Keys().get_group_token(), 'main')

    user_class.User.create_table()
    user_class.RpProfile.create_table()
    user_class.ProfileOwner.create_table()
    user_class.RoleOffer.create_table()

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
