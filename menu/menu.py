from vk_api import vk_api
from database import db_api
from menu import system, admin, user_profile, search, notification


def menu_hub(token):
    menus = {'main': main}
    menus.update(system.get_menus())
    menus.update(user_profile.get_menus())
    menus.update(search.get_menus())
    menus.update(notification.get_menus())
    menus.update(admin.get_menus())

    if token.menu_id in menus:
        return menus[token.menu_id](token)
    else:
        return system.empty_func(token)


def main(user):
    db_api.User().default_settings(user.info.id)

    message = 'Главное меню'
    button_profiles = vk_api.new_button('Мои анкеты', {'m_id': 'user_profiles'})
    button_search = vk_api.new_button('Найти соигроков', {'m_id': 'profiles_search'})
    admin_button = []
    if user.info.is_admin:
        admin_button = [vk_api.new_button('Меню админа', {'m_id': 'admin_menu'})]

    notifications_list = db_api.Notification().get_item_list(user.info.id)
    notification_count = len([i for i in notifications_list if not i.is_read])
    notifications_label = 'Мои Уведомления' + (f' ({notification_count})' if notification_count else '')
    notifications_color = 'positive' if notification_count else 'default'
    button_notifications = vk_api.new_button(notifications_label, {'m_id': 'notifications'}, notifications_color)
    return {'message': message, 'keyboard': [[button_profiles],
                                             [button_search],
                                             [button_notifications],
                                             admin_button]}




