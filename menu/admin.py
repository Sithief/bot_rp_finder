import logging
from bot_rp_finder.vk_api import vk_api
from bot_rp_finder.database import user_class
from bot_rp_finder.menu import system


def get_menus():
    menus = {
         'admin_setting_list': admin_setting_list,
         'admin_create_setting': admin_create_setting,
         'admin_setting_info': admin_setting_info,
         'admin_change_setting_title': admin_change_setting_title,
         'admin_save_setting_title': admin_save_setting_title,
         'admin_change_setting_description': admin_change_setting_description,
         'admin_save_setting_description': admin_save_setting_description,
         'admin_delete_setting': admin_delete_setting,

         'admin_rp_rating_list': admin_rp_rating_list,
         'admin_create_rp_rating': admin_create_rp_rating,
         'admin_rp_rating_info': admin_rp_rating_info,
         'admin_change_rp_rating_title': admin_change_rp_rating_title,
         'admin_save_rp_rating_title': admin_save_rp_rating_title,
         'admin_change_rp_rating_description': admin_change_rp_rating_description,
         'admin_save_rp_rating_description': admin_save_rp_rating_description,
         'admin_delete_rp_rating': admin_delete_rp_rating
    }
    return menus

# Меню администратора


def admin_setting_list(user_message):
    user_info = user_class.get_user(user_message['from_id'])

    if not user_info.is_admin:
        return system.access_error()

    message = 'Список доступных сеттингов.\n' \
              'Выберите тот, который хотите изменить или удалить.'
    setting = user_class.SettingList().get_item_list()

    setting_btn = list()
    for stt in setting:
        setting_btn.append(vk_api.new_button(stt.title, {'m_id': 'admin_setting_info',
                                                         'args': {'setting_id': stt.id}}, 'default'))

    button_create = vk_api.new_button('Добавить новый сеттинг', {'m_id': 'admin_create_setting',
                                                                 'args': None}, 'positive')
    button_return = vk_api.new_button('Вернуться в главное меню', {'m_id': 'main', 'args': None}, 'primary')
    return {'message': message, 'keyboard': [setting_btn, [button_create], [button_return]]}


def admin_create_setting(user_message):
    new_setting = user_class.SettingList().create_item()
    if not new_setting:
        return system.access_error()
    user_info = user_class.get_user(user_message['from_id'])
    user_info.item_id = new_setting.id
    user_info.save()
    return admin_setting_info(user_message)


def admin_setting_info(user_message):
    user_info = user_class.get_user(user_message['from_id'])

    try:
        user_info.item_id = user_message['payload']['args']['setting_id']
    except:
        print('что-то пошло не так')

    user_info.menu_id = 'admin_setting_info'
    user_info.save()
    setting = user_class.SettingList().get_item(user_info.item_id)
    message = f'Название сеттинга: {setting.title}\n' \
              f'Описание сеттинга: {setting.description}'
    btn_change_title = vk_api.new_button('Изменить название сеттинга',
                                         {'m_id': 'admin_change_setting_title', 'args': None})
    btn_change_description = vk_api.new_button('Изменить описание сеттинга',
                                               {'m_id': 'admin_change_setting_description', 'args': None})
    btn_del = vk_api.new_button('Удалить сеттинг',
                                {'m_id': 'confirm_action',
                                 'args': {'m_id': 'admin_delete_setting',
                                                  'args': {'setting_id': user_info.item_id}}},
                                'negative')
    button_return = vk_api.new_button('Вернуться к списку сеттингов',
                                      {'m_id': 'admin_setting_list', 'args': None}, 'primary')
    return {'message': message, 'keyboard': [[btn_change_title], [btn_change_description], [btn_del], [button_return]]}


def admin_change_setting_title(user_message):
    menu = system.InputText(user_id=user_message['from_id'],
                            next_menu='admin_save_setting_title',
                            prew_menu='admin_setting_info')
    return menu.change_text('Введите название сеттинга')


def admin_save_setting_title(user_message):
    menu = system.InputText(user_id=user_message['from_id'],
                            next_menu='admin_change_setting_title',
                            prew_menu='admin_setting_info')
    return menu.save_title(user_message=user_message,
                           table_class=user_class.SettingList(),
                           success_menu=admin_setting_info)


def admin_change_setting_description(user_message):
    menu = system.InputText(user_id=user_message['from_id'],
                            next_menu='admin_save_setting_description',
                            prew_menu='admin_setting_info')
    return menu.change_text('Введите описание сеттинга')


def admin_save_setting_description(user_message):
    menu = system.InputText(user_id=user_message['from_id'],
                            prew_menu='admin_change_setting_description',
                            next_menu='admin_setting_info')
    return menu.save_description(user_message=user_message,
                                 table_class=user_class.SettingList(),
                                 success_menu=admin_setting_info)


def admin_delete_setting(user_message):
    menu = system.ItemMenu(user_id=user_message['from_id'],
                           table_class=user_class.SettingList(),
                           prew_menu='admin_setting_list')
    return menu.delete_item()


def admin_create_rp_rating(user_message):
    new_item = user_class.RpRating().create_item()
    if not new_item:
        return system.access_error()
    user_info = user_class.get_user(user_message['from_id'])
    user_info.item_id = new_item.id
    user_info.save()
    return admin_rp_rating_info(user_message)


def admin_rp_rating_list(user_message):
    user_info = user_class.get_user(user_message['from_id'])

    if not user_info.is_admin:
        return system.access_error()

    message = 'Список доступных рейтингов ролевых.\n' \
              'Выберите тот, который хотите изменить или удалить.'
    items = user_class.RpRating().get_item_list()

    items_btn = list()
    for rpr in items:
        items_btn.append(vk_api.new_button(rpr.title, {'m_id': 'admin_rp_rating_info',
                                                       'args': {'rp_rating_id': rpr.id}}, 'default'))

    button_create = vk_api.new_button('Добавить новый рейтинг ролевой', {'m_id': 'admin_create_rp_rating',
                                                                         'args': None}, 'positive')
    button_return = vk_api.new_button('Вернуться в главное меню', {'m_id': 'main', 'args': None}, 'primary')
    return {'message': message, 'keyboard': [items_btn, [button_create], [button_return]]}


def admin_rp_rating_setting(user_message):
    new_item = user_class.RpRating().create_item()
    if not new_item:
        return system.access_error()
    user_info = user_class.get_user(user_message['from_id'])
    user_info.item_id = new_item.id
    user_info.save()
    return admin_rp_rating_info(user_message)


def admin_rp_rating_info(user_message):
    user_info = user_class.get_user(user_message['from_id'])

    try:
        user_info.item_id = user_message['payload']['args']['rp_rating_id']
    except:
        print('что-то пошло не так')

    user_info.menu_id = 'admin_rp_rating_info'
    user_info.save()
    item = user_class.RpRating().get_item(user_info.item_id)
    message = f'Название рейтинга ролевой: {item.title}\n' \
              f'Описание рейтинга ролевой: {item.description}'
    btn_change_title = vk_api.new_button('Изменить название',
                                         {'m_id': 'admin_change_rp_rating_title', 'args': None})
    btn_change_description = vk_api.new_button('Изменить описание',
                                               {'m_id': 'admin_change_rp_rating_description', 'args': None})
    btn_del = vk_api.new_button('Удалить сеттинг',
                                {'m_id': 'confirm_action',
                                 'args': {'m_id': 'admin_delete_rp_rating',
                                                  'args': {'rp_rating_id': user_info.item_id}}},
                                'negative')
    button_return = vk_api.new_button('Вернуться к списку',
                                      {'m_id': 'admin_rp_rating_list', 'args': None}, 'primary')
    return {'message': message, 'keyboard': [[btn_change_title], [btn_change_description], [btn_del], [button_return]]}


def admin_change_rp_rating_title(user_message):
    menu = system.InputText(user_id=user_message['from_id'],
                            next_menu='admin_save_rp_rating_title',
                            prew_menu='admin_rp_rating_info')
    return menu.change_text('Введите название возрастного рейтинга')


def admin_save_rp_rating_title(user_message):
    menu = system.InputText(user_id=user_message['from_id'],
                            next_menu='admin_change_rp_rating_title',
                            prew_menu='admin_rp_rating_info')
    return menu.save_title(user_message=user_message,
                           table_class=user_class.RpRating(),
                           success_menu=admin_rp_rating_info)


def admin_change_rp_rating_description(user_message):
    menu = system.InputText(user_id=user_message['from_id'],
                            next_menu='admin_save_rp_rating_description',
                            prew_menu='admin_rp_rating_info')
    return menu.change_text('Введите описание возрастного рейтинга')


def admin_save_rp_rating_description(user_message):
    menu = system.InputText(user_id=user_message['from_id'],
                            prew_menu='admin_change_rp_rating_description',
                            next_menu='admin_rp_rating_info')
    return menu.save_description(user_message=user_message,
                                 table_class=user_class.RpRating(),
                                 success_menu=admin_rp_rating_info)


def admin_delete_rp_rating(user_message):
    menu = system.ItemMenu(user_id=user_message['from_id'],
                           table_class=user_class.RpRating(),
                           prew_menu='admin_rp_rating_list')
    return menu.delete_item()

