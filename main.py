import threading
import queue
import logging
import time
import sys
from flask import Flask, request
from menu import menu, user_profile
from menu.execute_time import Timer
from vk_api import vk_api, longpoll, msg_send
from vk_api.Keys import Keys
from database import db_api
from dropbox_api import dropbox_backup
from menu import notification
from menu.token import Token
from __init__ import *


app = Flask(__name__)


def init():
    if 'update_db' in sys.argv:
        db_api.update_db()

    for msg in bot_api.unanswered():
        message_processing(msg)

    admin_list = bot_api.get_admins()
    db_api.init_db()
    db_api.update_admins(admin_list)


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


def message_processing(msg):
    print('usr msg:', msg)
    if msg.get('cropped'):
        full_msg = bot_api.msg_get(message_id=msg.get('id'))
        if full_msg:
            msg = full_msg
    user_token = Token(msg)
    if not user_token.info:
        vk_user_info = bot_api.get_user_info(msg['from_id'])
        try:
            user_info = db_api.User().create_user(user_id=vk_user_info['id'],
                                                  name=vk_user_info['first_name'],
                                                  is_fem=vk_user_info['sex'] % 2)
            user_token.update_user_info(user_info, msg)
        except:
            pass

    bot_message = menu.menu_hub(user_token)
    print('bot_msg', bot_message)
    actions = vk_api.get_actions_from_buttons(bot_message['keyboard'])
    db_api.AvailableActions().update_actions(msg['from_id'], actions)

    bot_api.msg_send(peer_id=msg['peer_id'], payload=bot_message)
    notification.send_unread_notifications(bot_api)
    # if new_messages:
    #     timer.time_stamp('total')
    #     changes_count += 1
    #     logging.info(timer.quick_stat('total'))
    #
    # elif changes_count > 1:
    #     timer.output()
    #     changes_count = 0
    #     timer.start('dropbox')
    #     dropbox_backup.backup_db()
    #     timer.time_stamp('dropbox')
    #
    #     timer.start('new notifications')
    #     notification.send_unread_notifications(bot_api)
    #     timer.time_stamp('new notifications')


@app.route('/vk_callback/', methods=['POST'])
def vk_callback():
    t_start = time.time()
    content = request.get_json(force=True)
    print('content', content)
    if content.get('type') == 'confirmation':
        confirm = CONF.get('VK', 'confirm', fallback='no confirm')
        return confirm

    elif content.get('type') == 'message_new':
        global events
        if content['event_id'] in events:
            return 'Ok'
        events = [content['event_id']] + events[:1000]
        message_processing(content['object']['message'])
        global timers
        timers = [time.time() - t_start] + timers[:10000]
    return 'Ok'


@app.route("/")
def index():
    uptime_days = int(time.time() - uptime) // (24 * 60 * 60)
    uptime_time = time.strftime('%X', time.gmtime(time.time() - uptime))
    if timers:
        msg_time = f"msg: {len(timers)} msg time: " \
           f"5: {round(sum(timers[:5])/len(timers[:5]), 3)}s. " \
           f"25: {round(sum(timers[:25])/len(timers[:25]), 3)}s. " \
           f"100: {round(sum(timers[:100])/len(timers[:100]), 3)}s. "
    else:
        msg_time = ''
    return f"uptime: {uptime_days} days and {uptime_time} \n" + msg_time


if __name__ == '__main__':
    init()
    app.run()

