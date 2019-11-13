import time
import json
from bot_rp_finder.vk_api import vk_api
from bot_rp_finder.database import user_class
from bot_rp_finder.menu import system


def get_menus():
    menus = {
        'notifications': notifications,
        'notification_display': notification_display
    }
    return menus

# уведомления


def notifications(user_message):
    notifications_list = user_class.get_user_notifications(user_message['from_id'])
    message = 'Список уведомлений'
    nt_buttons = list()
    for num, nt in enumerate(notifications_list):
        color = 'positive'
        if nt.is_read:
            color = 'default'
        nt_buttons.append([vk_api.new_button(nt.title,
                                             {'m_id': 'notification_display',
                                              'args': {'nt_id': nt.id}}, color)])

    button_main = vk_api.new_button('Главное меню', {'m_id': 'main', 'args': None}, 'primary')
    return {'message': message, 'keyboard': nt_buttons + [[button_main]]}


def notification_display(user_message):
    user_info = user_class.User().get_user(user_message['from_id'])
    if user_message['payload']['args'] and 'nt_id' in user_message['payload']['args']:
        user_info.item_id = user_message['payload']['args']['nt_id']
        user_info.save()

    nt_info = user_class.get_notification(user_info.item_id)
    if not nt_info:
        return system.access_error()

    nt_info.is_read = True
    nt_info.save()
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
