import requests
import time
import multiprocessing
import menu
import user_api
import conversations_api
import longpoll
import group_background_process
import vk_api
import db_api
import user_class
import text_extension as t_ext
# import longpoll_test as longpoll
# import vk_api_test as vk_api
import os
from Keys import Keys


# private_group_token='57f01a1f0384e151ae68d6b2e1129c078c821886f5b5e77ee0a3e9390c69ef70accd490a9eabe98978b83'

# class LastRequest(object):
#     def __init__(self, initval=0.0):
#         self.time = multiprocessing.Value('d', initval)
#
#     def update(self):
#         with self.time.get_lock():
#             self.time.value = time.time()
#
#     def get_time(self):
#         with self.time.get_lock():
#             return self.time.value
#
#
# class User(object):
#     def __init__(self, request_times, user_id, peer_id, db_filename, db_lock):
#         self.peer_id = peer_id
#         self.stdin = multiprocessing.Queue()
#         if user_id == peer_id:
#             self.process = multiprocessing.Process(target=user_api.main,
#                                                    args=(request_times, self.stdin, user_id, db_filename, db_lock))
#             self.process.start()
#             self.last_action_time = time.time()
#         else:
#             self.process = multiprocessing.Process(target=conversations_api.main,
#                                                    args=(request_times, self.stdin, peer_id, db_filename, db_lock))
#             self.process.start()
#             self.last_action_time = time.time()
#
#     def is_working(self, timeout):
#         try:
#             if time.time() - self.last_action_time > timeout:
#                 self.process.terminate()
#                 keyboard = vk_api.KeyConstruct().one_button('Я снова тут').get_buttons()
#                 bot_api.msg_send(self.peer_id, '', attachments=[t_ext.sticker('goodbye')], keyboard=keyboard)
#                 return False
#             return True
#         except Exception as e:
#             print('main User.process.is_working()', e, 'peer_id', self.peer_id)
#
#
# def clear_offline_users(user_dict):
#     offline_users = []
#     for key, user in user_dict.items():
#         try:
#             if not user.process.is_alive() or not user.is_working(15*60):
#                 offline_users.append(key)
#         except Exception as e:
#             print('clear_offline_users', e, 'peer_id', user.peer_id)
#     for key in offline_users:
#         user_dict.pop(key)
#         print('user %s is offline' % key)


if __name__ == '__main__':
    bot_api = vk_api.Api(Keys().get_group_token(), 'main')

    user_class.User.create_table()
    user_class.RpProfile.create_table()
    user_class.ProfileOwner.create_table()

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
