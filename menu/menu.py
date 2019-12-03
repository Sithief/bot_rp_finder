from bot_rp_finder.vk_api import vk_api
from bot_rp_finder.database import db_api
from bot_rp_finder.menu import system, admin, user_profile, search, notification

# TODO сделать сортировку уведомлений по дате, разделение на страницы и ограничение количества уведомлений на человека


def menu_hub(user_message):
    menus = {'main': main}
    menus.update(system.get_menus())
    menus.update(user_profile.get_menus())
    menus.update(search.get_menus())
    menus.update(notification.get_menus())
    menus.update(admin.get_menus())

    if 'payload' in user_message:
        if 'm_id' in user_message['payload'] and user_message['payload']['m_id'] in menus:
            return menus[user_message['payload']['m_id']](user_message)
        else:
            return system.empty_func(user_message)
    else:
        user_info = db_api.User().get_user(user_message['from_id'])
        return menus[user_info.menu_id](user_message)


def main(user_message):
    user_info = db_api.User().get_user(user_message['from_id'])
    user_info.menu_id = 'main'
    user_info.item_id = -1
    user_info.tmp_item_id = -1
    user_info.list_iter = 0
    user_info.save()

    message = 'Главное меню'
    button_profiles = vk_api.new_button('Мои анкеты', {'m_id': 'user_profiles'})
    button_search = vk_api.new_button('Найти соигроков', {'m_id': 'profiles_search'})
    admin_button = []
    if user_info.is_admin:
        admin_button = [vk_api.new_button('Меню админа', {'m_id': 'admin_menu'})]

    notifications_list = db_api.get_user_notifications(user_message['from_id'])
    notification_count = len([i for i in notifications_list if not i.is_read])
    notifications_label = 'Мои Уведомления' + (f' ({notification_count})' if notification_count else '')
    notifications_color = 'positive' if notification_count else 'default'
    button_notifications = vk_api.new_button(notifications_label, {'m_id': 'notifications'}, notifications_color)
    return {'message': message, 'keyboard': [[button_profiles],
                                             [button_search],
                                             [button_notifications],
                                             admin_button]}




