import json
from bot_rp_finder.vk_api import vk_api
from bot_rp_finder.database import user_class
from bot_rp_finder.menu import system

genders = ['Мужской', 'Женский', 'Не указано']
# создание и изменение анкет


def get_menus():
    menus = {
        'user_profiles': user_profiles,
        'create_profile': create_profile, 'delete_profile': delete_profile,
        'change_profile': change_profile,
        'change_name': change_name, 'save_name': save_name,
        'change_gender': change_gender,
        'change_setting_list': change_setting_list,
        'change_rp_rating_list': change_rp_rating_list,
        'change_description': change_description, 'save_description': save_description,
        'change_images': change_images, 'input_images': input_images, 'save_images': save_images
    }
    return menus


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
        message = system.rp_profile_display(user_message['payload']['args']['profile_id'])
        user_info.item_id = user_message['payload']['args']['profile_id']
    except:
        message = system.rp_profile_display(user_info.item_id)

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
    error_message = system.input_title_check(user_message)
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
    error_message = system.input_description_check(user_message)
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
