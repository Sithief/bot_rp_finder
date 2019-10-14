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
    user_class.SearchPreset.create_table()
    user_class.SearchPresetOwner.create_table()

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
        # bot_api.msg_send(363230444, 'test', keyboard=)

    # db_filename = 'art_hub.db'
    # # if not db_api.DataBase(db_filename).check():
    # #     print('db problem')
    # #     input()
    # requests_timer = {'group': LastRequest(time.time()), 'user': LastRequest(time.time())}
    # db_lock = multiprocessing.Lock()
    # bot_api = vk_api.Api(Keys().get_group_token(), requests_timer['group'], 'main')
    # bot_api.msg_send(363230444, 'Бот запущен')
    #
    # active_users = {}
    #
    # longpoll_stdout = multiprocessing.Queue()
    # longpoll_listner = multiprocessing.Process(target=longpoll.listen, args=(requests_timer,
    #                                                                          longpoll_stdout))
    #
    # longpoll_listner.start()
    # last_message_time = time.time()
    #
    # live_cover_updater = multiprocessing.Process(target=group_background_process.main, args=(requests_timer,
    #                                                                                          db_filename,
    #                                                                                          db_lock))
    # live_cover_updater.start()
    #
    # while 1:
    #     try:
    #         new_messages = longpoll_stdout.get(timeout=120)
    #         last_message_time = time.time()
    #     except:
    #         try:
    #             bot_api.log_write('new longpoll listner', 'new longpoll listner')
    #             longpoll_listner.terminate()
    #             longpoll_listner.join()
    #             longpoll_listner = multiprocessing.Process(target=longpoll.listen, args=(requests_timer,
    #                                                                                      longpoll_stdout))
    #             longpoll_listner.start()
    #         except Exception as e:
    #             bot_api.log_write('cant start new longpoll listner' + str(e),
    #                               'cant start new longpoll listner' + str(e))
    #         continue
    #
    #     clear_offline_users(active_users)
    #     for message in new_messages:
    #         user_full_id = str(message['peer_id'])
    #         if user_full_id not in active_users.keys():
    #             if message['from_id'] == message['peer_id'] and \
    #                     bot_api.messages_count(message['from_id']) > bot_api.max_msg_per_hour:
    #                 bot_api.request_get('messages.markAsAnsweredConversation',
    #                                     {'peer_id': message['peer_id'], 'answered': 1})
    #                 bot_api.request_get('messages.markAsRead',
    #                                     {'peer_id': message['peer_id']})
    #                 continue
    #             active_users.update({user_full_id: User(requests_timer, message['from_id'],
    #                                                     message['peer_id'], db_filename, db_lock)})
    #         active_users[user_full_id].stdin.put(message)
    #         active_users[user_full_id].last_action_time = time.time()
    #
    #
    #
    # longpoll_listner.join()
    # live_cover_updater.join()
