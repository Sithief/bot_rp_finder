import json
import time
from bot_rp_finder.vk_api import vk_api
from bot_rp_finder.database import user_class
from bot_rp_finder.menu import text_extension as t_ext


genders = ['Мужской', 'Женский', 'Не указано']
# TODO сделать сортировку уведомлений по дате, разделение на страницы и ограничение количества уведомлений на человека


def menu_hub(user_message):
    menus = {'main': main,
             'confirm_action': confirm_action,

             'user_profiles': user_profiles,
             'create_profile': create_profile, 'delete_profile': delete_profile,
             'change_profile': change_profile,
             'change_name': change_name, 'save_name': save_name,
             'change_gender': change_gender,
             'change_setting_list': change_setting_list,
             'change_rp_rating_list': change_rp_rating_list,
             'change_description': change_description, 'save_description': save_description,
             'change_images': change_images, 'input_images': input_images, 'save_images': save_images,

             'profiles_search': profiles_search,
             'choose_profile_to_search': choose_profile_to_search,
             'search_by_profile': search_by_profile,
             'show_player_profile': show_player_profile,

             'notifications': notifications,
             'notification_display': notification_display,

             'user_account': user_account,
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
    if 'payload' in user_message:
        if 'm_id' in user_message['payload'] and user_message['payload']['m_id'] in menus:
            return menus[user_message['payload']['m_id']](user_message)
        else:
            return empty_func(user_message)
    else:
        user_info = user_class.get_user(user_message['from_id'])
        return menus[user_info.menu_id](user_message)

# системные меню


def confirm_action(user_message):
    button_main = vk_api.new_button('Главное меню', {'m_id': 'main', 'args': None}, 'primary')
    message = 'Вы действительно хотите сделать это?'
    try:
        confirm_btn = vk_api.new_button('Да',
                                        {'m_id': user_message['payload']['args']['m_id'],
                                         'args': user_message['payload']['args']['args']},
                                        'positive')
        return {'message': message, 'keyboard': [[confirm_btn], [button_main]]}
    except:
        return {'message': message, 'keyboard': [[button_main]]}


def access_error():
    message = 'Ошибка доступа'
    button_return = vk_api.new_button('Вернуться в главное меню', {'m_id': 'main', 'args': None}, 'primary')
    return {'message': message, 'keyboard': [[button_return]]}


def input_title_check(user_message, title_len=25):
    symbols = 'abcdefghijklmnopqrstuvwxyz' + 'абвгдеёжзийклмнопрстуфхцчшщьыъэюя' + "1234567890_-+,. '()"

    if len(user_message['text']) > title_len:
        message = f'Длина текста превосходит {title_len} символов.\n Придумайте более короткий вариант.'
        return message

    elif len(user_message['text']) == 0:
        message = f'Нужно было ввести текст.'
        return message

    elif not all([i in symbols for i in user_message['text'].lower()]):
        error_symbols = ['"' + i.replace('\\', '\\\\') + '"' for i in user_message['text'].lower() if i not in symbols]
        message = f"Текст содержит недопустимые символы: {' '.join(error_symbols)}"
        return message
    return ''


def input_description_check(user_message, description_len=500, lines_count=15):
    if len(user_message['text']) > description_len:
        message = f'Длина описания превосходит {description_len} символов.\n' \
                  f'Постарайтесь сократить описание, оставив только самое важное.'
        return message

    if len(user_message['text']) == 0:
        message = f'Для описания нужно ввести текст.'
        return message

    if user_message['text'].count('\n') > lines_count:
        message = f"Вы использовали перенос строки слишком часто, " \
                  f"теперь описание занимает слишком много места на экране.\n" \
                  f"Попробуйте уменьшить количество переносов на новую строку."
        return message
    return ''


def rp_profile_display(profile_id):
    rp_profile = user_class.get_rp_profile(profile_id)
    if not rp_profile:
        return access_error()
    profile = dict({'message': '', 'attachment': ''})
    profile['message'] += f'Имя: {rp_profile.name}\n'
    if rp_profile.gender != 'Не указано':
        profile['message'] += f'Пол: {rp_profile.gender}\n'

    user_rating_list = user_class.ProfileRpRatingList().get_item_list(profile_id)
    user_want_rating_list = [i.item.title for i in user_rating_list if i.is_allowed]
    user_unwant_rating_list = [i.item.title for i in user_rating_list if not i.is_allowed]
    if user_want_rating_list:
        profile['message'] += f'Желательный рейтинг: {", ".join(user_want_rating_list)}\n'
    if user_unwant_rating_list:
        profile['message'] += f'Нежелательный рейтинг: {", ".join(user_unwant_rating_list)}\n'

    user_setting_list = user_class.ProfileSettingList().get_setting_list(profile_id)
    user_want_setting_list = [i.setting.title for i in user_setting_list if i.is_allowed]
    user_unwant_setting_list = [i.setting.title for i in user_setting_list if not i.is_allowed]
    if user_want_setting_list:
        profile['message'] += f'Желательный сеттинг: {", ".join(user_want_setting_list)}\n'
    if user_unwant_setting_list:
        profile['message'] += f'Нежелательный сеттинг: {", ".join(user_unwant_setting_list)}\n'

    profile['message'] += f'Описание: {rp_profile.description}\n'
    profile['attachment'] = ','.join(json.loads(rp_profile.arts))
    return profile


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

# создание и изменение анкет


def user_profiles(user_message):
    profiles = user_class.get_user_profiles(user_message['from_id'])
    message = 'Список ваших анкет:'
    pr_buttons = list()
    for num, pr in enumerate(profiles):
        pr_buttons.append([vk_api.new_button(pr.name,
                                             {'m_id': 'change_profile',
                                              'args': {'profile_id': pr.id}})])

    button_main = vk_api.new_button('Главное меню', {'m_id': 'main', 'args': None}, 'primary')
    if len(profiles) < 4:
        button_create_rp = vk_api.new_button('создать новую анкету', {'m_id': 'create_profile',
                                                                      'args': None}, 'primary')
    else:
        button_create_rp = vk_api.new_button('создать новую анкету', {'m_id': 'user_profiles',
                                                                      'args': None}, 'default')
    return {'message': message, 'keyboard': pr_buttons + [[button_create_rp], [button_main]]}


def create_profile(user_message):
    rp_profile = user_class.create_rp_profile(user_message['from_id'])
    user_info = user_class.get_user(user_message['from_id'])
    user_info.item_id = rp_profile.id
    user_info.save()
    return change_profile(user_message)


def delete_profile(user_message):
    user_info = user_class.get_user(user_message['from_id'])
    try:
        profile = user_class.get_rp_profile(user_info.item_id).name
        if user_class.delete_rp_profile(user_info.item_id):
            message = f'Ваша анкета "{profile}" успешно удалена.'
        else:
            message = f'Во время удаления анкеты произошла ошибка, попробуйте повторить запрос через некоторое время.'
    except:
        message = f'Во время удаления анкеты произошла ошибка, попробуйте повторить запрос через некоторое время.'
    button_return = vk_api.new_button('Вернуться к списку анкет',
                                      {'m_id': 'user_profiles', 'args': None})
    return {'message': message, 'keyboard': [[button_return]]}


def change_profile(user_message):
    user_info = user_class.get_user(user_message['from_id'])

    try:
        message = rp_profile_display(user_message['payload']['args']['profile_id'])
        user_info.item_id = user_message['payload']['args']['profile_id']
    except:
        message = rp_profile_display(user_info.item_id)

    user_info.menu_id = 'change_profile'
    user_info.save()

    message['message'] = 'Ваша анкета:\n\n' + message['message']
    button_main = vk_api.new_button('Главное меню', {'m_id': 'main', 'args': None}, 'primary')
    buttons_change_name = vk_api.new_button('Имя', {'m_id': 'change_name', 'args': None})
    buttons_change_gender = vk_api.new_button('Пол', {'m_id': 'change_gender', 'args': None})
    buttons_change_setting = vk_api.new_button('Сеттинг',
                                               {'m_id': 'change_setting_list', 'args': None})
    buttons_change_rp_rating = vk_api.new_button('Рейтинг',
                                                 {'m_id': 'change_rp_rating_list', 'args': None})
    buttons_change_description = vk_api.new_button('Описание',
                                                   {'m_id': 'change_description', 'args': None})
    buttons_change_images = vk_api.new_button('Изображения',
                                              {'m_id': 'change_images', 'args': None})
    buttons_delete = vk_api.new_button('Удалить анкету',
                                       {'m_id': 'confirm_action',
                                        'args': {'m_id': 'delete_profile',
                                                      'args': {'profile_id': user_info.item_id}}},
                                       'negative')
    return {'message': message['message'],
            'attachment': message['attachment'],
            'keyboard': [[buttons_change_name, buttons_change_description],
                         [buttons_change_gender, buttons_change_setting, buttons_change_rp_rating],
                         [buttons_change_images],
                         [buttons_delete],
                         [button_main]]}


def change_name(user_message):
    user_info = user_class.get_user(user_message['from_id'])
    user_info.menu_id = 'save_name'
    user_info.save()
    message = 'Введите имя вашего персонажа'
    button_return = vk_api.new_button('Вернуться к анкете',
                                      {'m_id': 'change_profile', 'args': None}, 'negative')

    return {'message': message, 'keyboard': [[button_return]]}


def save_name(user_message):
    error_message = input_title_check(user_message)
    if error_message:
        button_return = vk_api.new_button('Вернуться к анкете',
                                          {'m_id': 'change_profile', 'args': None}, 'negative')
        button_try_again = vk_api.new_button('Ввести имя снова',
                                             {'m_id': 'change_name', 'args': None}, 'positive')
        return {'message': error_message, 'keyboard': [[button_return, button_try_again]]}

    user_info = user_class.get_user(user_message['from_id'])
    rp_profile = user_class.get_rp_profile(user_info.item_id)
    rp_profile.name = user_message['text']
    rp_profile.save()
    return change_profile(user_message)


def change_gender(user_message):
    user_info = user_class.get_user(user_message['from_id'])
    profile = user_class.get_rp_profile(user_info.item_id)

    if user_message['payload']['args']:
        profile.gender = user_message['payload']['args']
        profile.save()

    message = 'Выберите пол вашего персонажа'

    gen_btn = list()
    for gen in genders:
        color = 'default'
        if profile.gender == gen:
            color = 'positive'
        gen_btn.append(vk_api.new_button(gen, {'m_id': 'change_gender', 'args': gen}, color))

    button_return = vk_api.new_button('Вернуться к анкете',
                                      {'m_id': 'change_profile', 'args': None}, 'primary')
    return {'message': message, 'keyboard': [gen_btn, [button_return]]}


def change_setting_list(user_message):
    user_info = user_class.get_user(user_message['from_id'])
    profile_id = user_info.item_id
    setting = user_class.SettingList().get_setting_list()
    user_setting = user_class.ProfileSettingList().get_setting_list(profile_id)
    user_setting_list = {i.setting_id: i for i in user_setting}

    message = 'Выберите подходящие сеттинги для игры:\n' \
              '• Первое нажатие добавляет в список\n' \
              '• Второе переносит в список исключений\n' \
              '• третье - убирает из списков'

    if user_message['payload']['args']:
        if user_message['payload']['args']['setting_id'] in user_setting_list:
            if user_setting_list[user_message['payload']['args']['setting_id']].is_allowed:
                user_setting_list[user_message['payload']['args']['setting_id']].is_allowed = False
                user_setting_list[user_message['payload']['args']['setting_id']].save()
            else:
                user_class.ProfileSettingList().delete_setting_from_list(user_message['payload']['args']['profile_id'],
                                                                         user_message['payload']['args']['setting_id'])
        else:
            user_class.ProfileSettingList().add_setting(user_message['payload']['args']['profile_id'],
                                                        user_message['payload']['args']['setting_id'])
            setting_info = user_class.SettingList().get_setting(user_message['payload']['args']['setting_id'])
            message += f'\n\n' \
                       f'Вы добавили сеттинг: "{setting_info.title}"\n' \
                       f'Его описание: {setting_info.description}'
        user_setting = user_class.ProfileSettingList().get_setting_list(profile_id)
        user_setting_list = {i.setting_id: i for i in user_setting}

    setting_btn = list()
    for stt in setting:
        color = 'default'
        if stt.id in user_setting_list:
            if user_setting_list[stt.id].is_allowed:
                color = 'positive'
            else:
                color = 'negative'
        setting_btn.append(vk_api.new_button(stt.title, {'m_id': 'change_setting_list',
                                                         'args': {'setting_id': stt.id,
                                                                  'profile_id': profile_id}}, color))

    button_return = vk_api.new_button('Вернуться к анкете',
                                      {'m_id': 'change_profile', 'args': None}, 'primary')
    return {'message': message, 'keyboard': [setting_btn, [button_return]]}


def change_rp_rating_list(user_message):
    user_info = user_class.get_user(user_message['from_id'])
    profile_id = user_info.item_id
    item_list = user_class.RpRating().get_item_list()
    user_item_list = user_class.ProfileRpRatingList().get_item_list(profile_id)
    user_item_dict = {i.item_id: i for i in user_item_list}

    message = 'Выберите подходящие сеттинги для игры:\n' \
              '• Первое нажатие добавляет в список\n' \
              '• Второе переносит в список исключений\n' \
              '• третье - убирает из списков'

    if user_message['payload']['args']:
        profile_id = user_message['payload']['args']['profile_id']
        item_id = user_message['payload']['args']['item_id']
        if item_id in user_item_dict:
            if user_item_dict[item_id].is_allowed:
                user_item_dict[item_id].is_allowed = False
                user_item_dict[item_id].save()
            else:
                user_class.ProfileRpRatingList().delete_item_from_list(profile_id, item_id)
        else:
            user_class.ProfileRpRatingList().add_item(profile_id, item_id)
            item_info = user_class.RpRating().get_item(item_id)
            message += f'\n\n' \
                       f'Вы добавили рейтинг: "{item_info.title}"\n' \
                       f'Его описание: {item_info.description}'
        user_item_list = user_class.ProfileRpRatingList().get_item_list(profile_id)
        user_item_dict = {i.item_id: i for i in user_item_list}

    item_btn = list()
    for item in item_list:
        color = 'default'
        if item.id in user_item_dict:
            if user_item_dict[item.id].is_allowed:
                color = 'positive'
            else:
                color = 'negative'
        item_btn.append(vk_api.new_button(item.title, {'m_id': 'change_rp_rating_list',
                                                       'args': {'item_id': item.id,
                                                                'profile_id': profile_id}}, color))

    button_return = vk_api.new_button('Вернуться к анкете',
                                      {'m_id': 'change_profile', 'args': None}, 'primary')
    return {'message': message, 'keyboard': [item_btn, [button_return]]}


def change_description(user_message):
    user_info = user_class.get_user(user_message['from_id'])
    user_info.menu_id = 'save_description'
    user_info.save()
    message = 'Введите описание вашего персонажа'
    button_return = vk_api.new_button('Вернуться к анкете',
                                      {'m_id': 'change_profile', 'args': None}, 'negative')
    return {'message': message, 'keyboard': [[button_return]]}


def save_description(user_message):
    error_message = input_description_check(user_message)
    if error_message:
        button_return = vk_api.new_button('Вернуться к анкете',
                                          {'m_id': 'change_profile', 'args': None}, 'negative')
        button_try_again = vk_api.new_button('Ввести опсание снова',
                                             {'m_id': 'change_name', 'args': None}, 'positive')
        return {'message': error_message, 'keyboard': [[button_return, button_try_again]]}

    user_info = user_class.get_user(user_message['from_id'])
    rp_profile = user_class.get_rp_profile(user_info.item_id)
    rp_profile.description = user_message['text']
    rp_profile.save()
    return change_profile(user_message)


def change_images(user_message):
    user_info = user_class.get_user(user_message['from_id'])
    user_info.menu_id = 'save_images'
    user_info.save()
    message = 'Отправьте до 7 изображений для анкеты.\n' \
              'Лучше всего использовать изображения, на которых хорошо видна внешность персонажа, ' \
              'его характер и подходящая для него обстановка.'
    button_return = vk_api.new_button('Вернуться к анкете',
                                      {'m_id': 'change_profile', 'args': None}, 'negative')
    return {'message': message, 'keyboard': [[button_return]]}


def input_images(user_message):
    # TODO добавить проверки ввода
    images_attachments = [i['photo'] for i in user_message['attachments'] if i['type'] == 'photo']
    images = [f"photo{i['owner_id']}_{i['id']}_{i.get('access_key', '')}" for i in images_attachments]

    message = 'Сохранить эти изображения?'
    button_yes = vk_api.new_button('Да, всё верно', {'m_id': 'save_images', 'args': None}, 'positive')
    button_no = vk_api.new_button('Нет, загрузить другие', {'m_id': 'change_images', 'args': None}, 'negative')
    return {'message': message, 'keyboard': [[button_yes], [button_no]], 'attachment': images}


def save_images(user_message):
    images_attachments = [i['photo'] for i in user_message['attachments'] if i['type'] == 'photo']
    images = [f"photo{i['owner_id']}_{i['id']}_{i.get('access_key', '')}" for i in images_attachments]

    button_return = vk_api.new_button('Вернуться к анкете',
                                      {'m_id': 'change_profile', 'args': None}, 'negative')
    button_try_again = vk_api.new_button('Отправить изображения снова',
                                         {'m_id': 'change_images', 'args': None}, 'positive')
    if len(images) == 0:
        message = f'Это не слишком похоже на подходящие для анкеты изображения. Попробуйте загрузить заново.'
        return {'message': message, 'keyboard': [[button_return, button_try_again]]}

    user_info = user_class.get_user(user_message['from_id'])
    rp_profile = user_class.get_rp_profile(user_info.item_id)
    rp_profile.arts = json.dumps(images, ensure_ascii=False)
    rp_profile.save()
    return change_profile(user_message)

# поиск со-игроков


def profiles_search(user_message):
    message = 'Поиск соигроков'
    button_by_profile = vk_api.new_button('Найти соигроков подходящих к анкете',
                                          {'m_id': 'choose_profile_to_search', 'args': None})
    button_main = vk_api.new_button('Главное меню', {'m_id': 'main', 'args': None}, 'primary')
    return {'message': message, 'keyboard': [[button_by_profile], [button_main]]}


def choose_profile_to_search(user_message):
    profiles = user_class.get_user_profiles(user_message['from_id'])
    message = 'Выберите из списка ваших анкет ту, для которой нужно найти соигроков'
    pr_buttons = list()
    for num, pr in enumerate(profiles):
        pr_buttons.append([vk_api.new_button(pr.name,
                                             {'m_id': 'search_by_profile',
                                              'args': {'profile_id': pr.id}})])

    button_main = vk_api.new_button('Главное меню', {'m_id': 'main', 'args': None}, 'primary')
    return {'message': message, 'keyboard': pr_buttons + [[button_main]]}


def search_by_profile(user_message):
    profiles_per_page = 4
    user_info = user_class.get_user(user_message['from_id'])
    try:
        if 'profile_id' in user_message['payload']['args']:
            user_info.item_id = user_message['payload']['args']['profile_id']
        if 'iter' in user_message['payload']['args']:
            user_info.list_iter = user_message['payload']['args']['iter']
        user_info.save()
    except:
        pass

    suitable_profiles = user_class.find_suitable_profiles(user_info.item_id)
    sent_profiles = [pr.to_profile_id for pr in user_class.RoleOffer().get_offers_from_user(user_info.id) if pr.actual]
    confirmed_users = [pr.from_owner_id for pr in user_class.RoleOffer().get_offers_to_user(user_info.id) if pr.actual]
    message = 'Список анкет подходящих к вашей.\n' \
              'Синим отправленные предложения.\n' \
              'Зелёным - взаимные предложения.'
    pr_buttons = list()
    for pr in suitable_profiles[user_info.list_iter * profiles_per_page:(user_info.list_iter + 1) * profiles_per_page]:
        color = 'default'
        if pr.id in sent_profiles:
            color = 'primary'
            if pr.owner_id in confirmed_users:
                color = 'positive'
        pr_buttons.append([vk_api.new_button(pr.name,
                                             {'m_id': 'show_player_profile',
                                              'args': {'profile_id': pr.id,
                                                       'btn_back': {'label': 'К списку анкет',
                                                                    'm_id': 'search_by_profile',
                                                                    'args': None}
                                                       }}, color)])

    prew_color, next_color, prew_iter, next_iter = 'default', 'default', user_info.list_iter, user_info.list_iter
    if user_info.list_iter > 0:
        prew_color = 'primary'
        prew_iter = user_info.list_iter - 1
    if (user_info.list_iter + 1) * profiles_per_page < len(suitable_profiles):
        next_color = 'primary'
        next_iter = user_info.list_iter + 1
    button_prew = vk_api.new_button('Предыдущая страница', {'m_id': 'search_by_profile',
                                                            'args': {'iter': prew_iter}}, prew_color)
    button_next = vk_api.new_button('Следующая страница', {'m_id': 'search_by_profile',
                                                           'args': {'iter': next_iter}}, next_color)
    button_main = vk_api.new_button('Главное меню', {'m_id': 'main', 'args': None}, 'primary')
    return {'message': message, 'keyboard': pr_buttons + [[button_prew, button_next]] + [[button_main]]}


def show_player_profile(user_message):
    user_info = user_class.get_user(user_message['from_id'])
    if 'profile_id' in user_message['payload']['args']:
        user_info.tmp_item_id = user_message['payload']['args']['profile_id']
        user_info.save()

    if 'btn_back' in user_message['payload']['args']:
        btn_back = user_message['payload']['args']['btn_back']
    else:
        btn_back = {'label': 'В главное меню', 'm_id': 'main', 'args': None}


    try:
        if 'offer' in user_message['payload']['args']:
            user_role_offers = user_class.RoleOffer().get_offers_to_profile_owner(user_info.id, user_info.tmp_item_id)
            offers_dict = {i.to_profile_id: i for i in user_role_offers}
            if user_message['payload']['args']['offer']:
                if user_info.tmp_item_id not in offers_dict:
                    new_offer = user_class.RoleOffer().create_offer(user_info.id, user_info.tmp_item_id)
                    if not user_role_offers:
                        notification = user_class.create_notification(new_offer.to_owner_id, 'Предложение ролевой')
                        notification.description = f'Пользователь [id{user_info.id}|{user_info.name}] ' \
                                                   f'{t_ext.gender_msg("предожил", "предожила", user_info.is_fem)}' \
                                                   f' вам ролевую, вы можете просмотреть ' \
                                                   f'{t_ext.gender_msg("его", "её", user_info.is_fem)} анкеты.'
                        notification.create_time = int(time.time())
                        buttons = list()
                        profiles = user_class.get_user_profiles(user_message['from_id'])
                        for pr in profiles:
                            buttons.append({'label': pr.name,
                                            'm_id': 'show_player_profile',
                                            'args': {'profile_id': pr.id,
                                                     'btn_back': {'label': 'Вернуться к уведомлению',
                                                                  'm_id': 'notification_display',
                                                                  'args': None}}})
                        notification.buttons = json.dumps(buttons, ensure_ascii=False)
                        notification.save()
                else:
                    offers_dict[user_info.tmp_item_id].actual = True
                    offers_dict[user_info.tmp_item_id].save()
            else:
                offers_dict[user_info.tmp_item_id].actual = False
                offers_dict[user_info.tmp_item_id].save()
    except Exception as e:
        print('show_player_profile', e)
        pass

    message = rp_profile_display(user_info.tmp_item_id)
    offer_to_profile = user_class.RoleOffer().offer_to_profile(user_info.id, user_info.tmp_item_id)
    if offer_to_profile and offer_to_profile.actual:
        button_offer = vk_api.new_button('Отменить предложение',
                                         {'m_id': 'show_player_profile',
                                          'args': {'offer': False, 'btn_back': btn_back}},
                                         'negative')
    else:
        button_offer = vk_api.new_button('Предложить ролевую',
                                         {'m_id': 'show_player_profile',
                                          'args': {'offer': True, 'btn_back': btn_back}},
                                         'positive')

    button_back = vk_api.new_button(btn_back['label'], {'m_id': btn_back['m_id'], 'args': btn_back['args']})
    message.update({'keyboard': [[button_offer], [button_back]]})
    return message


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
        return access_error()

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


# Меню администратора


def admin_setting_list(user_message):
    user_info = user_class.get_user(user_message['from_id'])

    if not user_info.is_admin:
        return access_error()

    message = 'Список доступных сеттингов.\n' \
              'Выберите тот, который хотите изменить или удалить.'
    setting = user_class.SettingList().get_setting_list()

    setting_btn = list()
    for stt in setting:
        setting_btn.append(vk_api.new_button(stt.title, {'m_id': 'admin_setting_info',
                                                         'args': {'setting_id': stt.id}}, 'default'))

    button_create = vk_api.new_button('Добавить новый сеттинг', {'m_id': 'admin_create_setting',
                                                                 'args': None}, 'positive')
    button_return = vk_api.new_button('Вернуться в главное меню', {'m_id': 'main', 'args': None}, 'primary')
    return {'message': message, 'keyboard': [setting_btn, [button_create], [button_return]]}


def admin_create_setting(user_message):
    new_setting = user_class.SettingList().create_setting()
    if not new_setting:
        return access_error()
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
    setting = user_class.SettingList().get_setting(user_info.item_id)
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
    user_info = user_class.get_user(user_message['from_id'])
    user_info.menu_id = 'admin_save_setting_title'
    user_info.save()
    message = 'Введите название сеттинга'
    button_return = vk_api.new_button('Вернуться к списку сеттингов',
                                      {'m_id': 'admin_setting_list', 'args': None}, 'negative')
    return {'message': message, 'keyboard': [[button_return]]}


def admin_save_setting_title(user_message):
    error_message = input_title_check(user_message)
    if error_message:
        button_return = vk_api.new_button('Вернуться к списку сеттингов',
                                          {'m_id': 'admin_setting_list', 'args': None}, 'negative')
        button_try_again = vk_api.new_button('Ввести название снова',
                                             {'m_id': 'admin_change_setting_title', 'args': None}, 'positive')
        return {'message': error_message, 'keyboard': [[button_return, button_try_again]]}

    user_info = user_class.get_user(user_message['from_id'])
    setting = user_class.SettingList().get_setting(user_info.item_id)
    setting.title = user_message['text']
    setting.save()
    return admin_setting_info(user_message)


def admin_change_setting_description(user_message):
    user_info = user_class.get_user(user_message['from_id'])
    user_info.menu_id = 'admin_save_setting_description'
    user_info.save()
    message = 'Введите описание сеттинга'
    button_return = vk_api.new_button('Вернуться к списку сеттингов',
                                      {'m_id': 'admin_setting_list', 'args': None}, 'negative')
    return {'message': message, 'keyboard': [[button_return]]}


def admin_save_setting_description(user_message):
    error_message = input_description_check(user_message)
    if error_message:
        button_return = vk_api.new_button('Вернуться к списку сеттингов',
                                          {'m_id': 'admin_setting_list', 'args': None}, 'negative')
        button_try_again = vk_api.new_button('Ввести описание снова',
                                             {'m_id': 'admin_change_setting_title', 'args': None}, 'positive')
        return {'message': error_message, 'keyboard': [[button_return, button_try_again]]}

    user_info = user_class.get_user(user_message['from_id'])
    setting = user_class.SettingList().get_setting(user_info.item_id)
    setting.description = user_message['text']
    setting.save()
    return admin_setting_info(user_message)


def admin_delete_setting(user_message):
    user_info = user_class.get_user(user_message['from_id'])
    try:
        setting = user_class.SettingList().get_setting(user_info.item_id).title
        if user_class.SettingList().delete_setting(user_info.item_id):
            message = f'Сеттинг "{setting}" успешно удален.'
        else:
            message = f'Во время удаления сеттинга произошла ошибка, попробуйте повторить запрос через некоторое время.'
    except:
        message = f'Во время удаления сеттинга произошла ошибка, попробуйте повторить запрос через некоторое время.'
    button_return = vk_api.new_button('Вернуться к списку сеттингов',
                                      {'m_id': 'admin_setting_list', 'args': None}, 'primary')
    return {'message': message, 'keyboard': [[button_return]]}


def admin_create_rp_rating(user_message):
    new_item = user_class.RpRating().create_item()
    if not new_item:
        return access_error()
    user_info = user_class.get_user(user_message['from_id'])
    user_info.item_id = new_item.id
    user_info.save()
    return admin_rp_rating_info(user_message)


def admin_rp_rating_list(user_message):
    user_info = user_class.get_user(user_message['from_id'])

    if not user_info.is_admin:
        return access_error()

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
        return access_error()
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
    button_return = vk_api.new_button('Вернуться к списку сеттингов',
                                      {'m_id': 'admin_rp_rating_list', 'args': None}, 'primary')
    return {'message': message, 'keyboard': [[btn_change_title], [btn_change_description], [btn_del], [button_return]]}


def admin_change_rp_rating_title(user_message):
    user_info = user_class.get_user(user_message['from_id'])
    user_info.menu_id = 'admin_save_rp_rating_title'
    user_info.save()
    message = 'Введите название'
    button_return = vk_api.new_button('Вернуться к списку',
                                      {'m_id': 'admin_rp_rating_list', 'args': None}, 'negative')
    return {'message': message, 'keyboard': [[button_return]]}


def admin_save_rp_rating_title(user_message):
    error_message = input_title_check(user_message)
    if error_message:
        button_return = vk_api.new_button('Вернуться к списку',
                                          {'m_id': 'admin_rp_rating_list', 'args': None}, 'negative')
        button_try_again = vk_api.new_button('Ввести название снова',
                                             {'m_id': 'admin_change_rp_rating_title', 'args': None}, 'positive')
        return {'message': error_message, 'keyboard': [[button_return, button_try_again]]}

    user_info = user_class.get_user(user_message['from_id'])
    setting = user_class.RpRating().get_item(user_info.item_id)
    setting.title = user_message['text']
    setting.save()
    return admin_rp_rating_info(user_message)


def admin_change_rp_rating_description(user_message):
    user_info = user_class.get_user(user_message['from_id'])
    user_info.menu_id = 'admin_save_rp_rating_description'
    user_info.save()
    message = 'Введите описание'
    button_return = vk_api.new_button('Вернуться к списку',
                                      {'m_id': 'admin_rp_rating_list', 'args': None}, 'negative')
    return {'message': message, 'keyboard': [[button_return]]}


def admin_save_rp_rating_description(user_message):
    error_message = input_description_check(user_message)
    if error_message:
        button_return = vk_api.new_button('Вернуться к списку',
                                          {'m_id': 'admin_rp_rating_list', 'args': None}, 'negative')
        button_try_again = vk_api.new_button('Ввести описание снова',
                                             {'m_id': 'admin_change_rp_rating_title', 'args': None}, 'positive')
        return {'message': error_message, 'keyboard': [[button_return, button_try_again]]}

    user_info = user_class.get_user(user_message['from_id'])
    setting = user_class.RpRating().get_item(user_info.item_id)
    setting.description = user_message['text']
    setting.save()
    return admin_rp_rating_info(user_message)


def admin_delete_rp_rating(user_message):
    user_info = user_class.get_user(user_message['from_id'])
    try:
        setting = user_class.SettingList().get_setting(user_info.item_id).title
        if user_class.SettingList().delete_setting(user_info.item_id):
            message = f'Сеттинг "{setting}" успешно удален.'
        else:
            message = f'Во время удаления сеттинга произошла ошибка, попробуйте повторить запрос через некоторое время.'
    except:
        message = f'Во время удаления сеттинга произошла ошибка, попробуйте повторить запрос через некоторое время.'
    button_return = vk_api.new_button('Вернуться к списку сеттингов',
                                      {'m_id': 'admin_setting_list', 'args': None}, 'primary')
    return {'message': message, 'keyboard': [[button_return]]}

