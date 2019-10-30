import json
import time
from bot_rp_finder.vk_api import vk_api
from bot_rp_finder.database import user_class
from bot_rp_finder.menu import system, admin, user_profile, search

# TODO сделать сортировку уведомлений по дате, разделение на страницы и ограничение количества уведомлений на человека


def menu_hub(user_message):
    menus = {'main': main,

             'notifications': notifications,
             'notification_display': notification_display,

             'user_account': user_account,
             }
    menus.update(admin.get_menus())
    menus.update(system.get_menus())
    menus.update(user_profile.get_menus())

    if 'payload' in user_message:
        if 'm_id' in user_message['payload'] and user_message['payload']['m_id'] in menus:
            return menus[user_message['payload']['m_id']](user_message)
        else:
            return empty_func(user_message)
    else:
        user_info = user_class.get_user(user_message['from_id'])
        return menus[user_info.menu_id](user_message)


def main(user_message):
    user_info = user_class.get_user(user_message['from_id'])
    user_info.menu_id = 'main'
    user_info.item_id = -1
    user_info.tmp_item_id = -1
    user_info.list_iter = 0
    user_info.save()

    message = 'Главное меню'
    button_profiles = vk_api.new_button('Мои анкеты', {'m_id': 'user_profiles'})
    button_search = vk_api.new_button('Найти соигроков', {'m_id': 'profiles_search'})
    button_admin_setting = []
    button_admin_rp_rating = []
    if user_info.is_admin:
        button_admin_setting = [vk_api.new_button('Настройки списка сеттингов', {'m_id': 'admin_setting_list'})]
        button_admin_rp_rating = [vk_api.new_button('Настройки списка рейтингов ролевой',
                                                    {'m_id': 'admin_rp_rating_list'})]

    notifications_list = user_class.get_user_notifications(user_message['from_id'])
    notification_count = len([i for i in notifications_list if not i.is_read])
    notifications_label = 'Мои Уведомления' + (f' ({notification_count})' if notification_count else '')
    notifications_color = 'positive' if notification_count else 'default'
    button_notifications = vk_api.new_button(notifications_label, {'m_id': 'notifications'}, notifications_color)
    # button_user_account = vk_api.new_button('Настройки аккаунта', {'m_id': 'user_account'})
    return {'message': message, 'keyboard': [[button_profiles],
                                             [button_search],
                                             [button_notifications],
                                             button_admin_setting,
                                             button_admin_rp_rating]}


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
    user_info = user_class.get_user(user_message['from_id'])
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


def user_account(user_message):
    message = 'Настройки аккаунта'
    button_main = vk_api.new_button('Главное меню', {'m_id': 'main', 'args': None}, 'primary')
    return {'message': message, 'keyboard': [[button_main]]}


def empty_func(user_message):
    user_info = user_class.get_user(user_message['from_id'])
    message = 'Этого меню еще нет, но раз вы сюда пришли, вот вам монетка!'
    user_info.money += 1
    user_info.save()
    button_1 = vk_api.new_button('Главное меню', {'m_id': 'main', 'args': None}, 'primary')
    return {'message': message, 'keyboard': [[button_1]]}


