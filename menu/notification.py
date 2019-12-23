import time
import json
import logging
from bot_rp_finder.vk_api import vk_api
from bot_rp_finder.database import db_api
from bot_rp_finder.menu import system


def get_menus():
    menus = {
        'notifications': notifications,
        'notification_display': notification_display
    }
    return menus

# уведомления


def create_notification(owner_id, title, description, buttons):
    notification = db_api.Notification().create_item(owner_id, title)
    notification.description = description
    notification.create_time = int(time.time())
    notification.buttons = json.dumps(buttons, ensure_ascii=False)
    notification.save()


def notifications(user):
    notifications_list = db_api.Notification().get_item_list(user.info.id, 15)
    message = 'Список уведомлений'
    user.info.menu_id = 'notifications'
    user.info.save()
    nt_buttons = list()
    for num, nt in enumerate(notifications_list):
        color = 'positive'
        if nt.is_read:
            color = 'default'
        nt_buttons.append(vk_api.new_button(nt.title,
                                            {'m_id': 'notification_display',
                                             'args': {'nt_id': nt.id}}, color))

    steps = len(nt_buttons) // 3 * 3
    nt_buttons = [nt_buttons[i:i + 3] for i in range(0, steps, 3)] + [nt_buttons[steps:]]
    button_main = vk_api.new_button('Главное меню', {'m_id': 'main', 'args': None}, 'primary')
    return {'message': message, 'keyboard': nt_buttons + [[button_main]]}


def notification_constructor(nt_info):
    time_form = '%d.%m.%y %H:%M' if time.time() - nt_info.create_time > 24*60*60 else '%H:%M:%S'
    notification = dict({'message': ''})
    notification['message'] += f'Уведомление получено в: ' \
                               f'{time.strftime(time_form, time.gmtime(nt_info.create_time + 3*60*60))} (по Мск)\n'
    notification['message'] += f'Название: {nt_info.title}\n'
    notification['message'] += f'Сообщение: {nt_info.description}\n'
    notification['attachment'] = ','.join(json.loads(nt_info.attachment))
    notification['keyboard'] = list()
    for nt_btn in json.loads(nt_info.buttons):
        notification['keyboard'].append([vk_api.new_button(nt_btn['label'],
                                                           {'m_id': nt_btn['m_id'], 'args': nt_btn['args']})])
    notification['keyboard'].append([vk_api.new_button('Вернуться к уведомлениям',
                                                       {'m_id': 'notifications', 'args': None}, 'primary')])
    return notification


def notification_display(user):
    if 'nt_id' in user.menu_args:
        user.info.item_id = user.menu_args['nt_id']
        user.info.save()

    nt_info = db_api.Notification().get_item(user.info.item_id)
    if not nt_info:
        return system.access_error()

    nt_info.is_read = True
    nt_info.save()
    notification = notification_constructor(nt_info)

    return notification


def send_unread_notifications(msg_vk_api):
    users_notifications = db_api.Notification().get_new_items()
    for nt_info in users_notifications:
        message = notification_constructor(nt_info)
        actions = vk_api.get_actions_from_buttons(message['keyboard'])
        message['message'] = 'Вы получили новое уведомление!\n\n' + message['message']
        if msg_vk_api.send_notification(nt_info.owner_id, message):
            db_api.AvailableActions().update_actions(nt_info.owner_id, actions)
            nt_info.is_read = True
            nt_info.save()
            db_api.User().default_settings(nt_info.owner_id)
            user_info = db_api.User().get_user(nt_info.owner_id)
            user_info.item_id = nt_info.id
            user_info.save()
            logging.info(f'send notification {nt_info.owner_id}')
