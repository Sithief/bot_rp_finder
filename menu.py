import vk_api
import user_class
import json

genders = ['Мужской', 'Женский', 'Не указано']


def menu_hub(user_message):
    menus = {'main': main,
             'confirm_action': confirm_action,
             'user_profiles': user_profiles,
             'create_profile': create_profile, 'delete_profile': delete_profile,
             'change_profile': change_profile,
             'change_name': change_name, 'save_name': save_name,
             'change_gender': change_gender,
             'change_setting_list': change_setting_list,
             'change_description': change_description, 'save_description': save_description,
             'change_images': change_images, 'input_images': input_images, 'save_images': save_images,
             'profiles_search': profiles_search,
             'choose_profile_to_search': choose_profile_to_search,
             'search_by_profile': search_by_profile,
             'show_player_profile': show_player_profile,
             'notifications': notifications,
             'user_account': user_account,
             'admin_setting_list': admin_setting_list,
             'admin_create_setting': admin_create_setting,
             'admin_setting_info': admin_setting_info,
             'admin_change_setting_title': admin_change_setting_title,
             'admin_save_setting_title': admin_save_setting_title,
             'admin_delete_setting': admin_delete_setting}
    if 'payload' in user_message:
        if 'menu_id' in user_message['payload'] and user_message['payload']['menu_id'] in menus:
            return menus[user_message['payload']['menu_id']](user_message)
        else:
            return empty_func(user_message)
    else:
        user_info = user_class.get_user(user_message['from_id'])
        return menus[user_info.menu_id](user_message)

# системные меню


def confirm_action(user_message):
    button_main = vk_api.new_button('Главное меню', {'menu_id': 'main', 'arguments': None}, 'primary')
    message = 'Вы действительно хотите сделать это?'
    try:
        confirm_btn = vk_api.new_button('Да',
                                        {'menu_id': user_message['payload']['arguments']['menu_id'],
                                         'arguments': user_message['payload']['arguments']['arguments']},
                                        'positive')
        return {'message': message, 'keyboard': [[confirm_btn], [button_main]]}
    except:
        return {'message': message, 'keyboard': [[button_main]]}


def access_error(user_message):
    message = 'Ошибка доступа'
    button_return = vk_api.new_button('Вернуться в главное меню', {'menu_id': 'main', 'arguments': None}, 'primary')
    return {'message': message, 'keyboard': [[button_return]]}


def main(user_message):
    user_info = user_class.get_user(user_message['from_id'])
    user_info.menu_id = 'main'
    user_info.item_id = -1
    user_info.tmp_item_id = -1
    user_info.list_iter = 0
    user_info.save()

    message = 'Главное меню'
    button_profiles = vk_api.new_button('Мои анкеты', {'menu_id': 'user_profiles'})
    button_search = vk_api.new_button('Найти соигроков', {'menu_id': 'profiles_search'}, 'positive')
    button_admin_setting = []
    if user_info.is_admin:
        button_admin_setting = [vk_api.new_button('Настройки списка сеттингов', {'menu_id': 'admin_setting_list'})]

    # button_notifications = vk_api.new_button('Мои Уведомления', {'menu_id': 'notifications'})
    # button_user_account = vk_api.new_button('Настройки аккаунта', {'menu_id': 'user_account'})
    return {'message': message, 'keyboard': [[button_profiles],
                                             [button_search],
                                             button_admin_setting]}

# создание и изменение анкет


def user_profiles(user_message):
    profiles = user_class.get_user_profiles(user_message['from_id'])
    message = 'Список ваших анкет:'
    pr_buttons = list()
    for num, pr in enumerate(profiles):
        pr_buttons.append([vk_api.new_button(pr.profile.name,
                                             {'menu_id': 'change_profile',
                                              'arguments': {'profile_id': pr.profile.id}})])

    button_main = vk_api.new_button('Главное меню', {'menu_id': 'main', 'arguments': None}, 'primary')
    if len(profiles) < 4:
        button_create_rp = vk_api.new_button('создать новую анкету', {'menu_id': 'create_profile',
                                                                      'arguments': None}, 'primary')
    else:
        button_create_rp = vk_api.new_button('создать новую анкету', {'menu_id': 'user_profiles',
                                                                      'arguments': None}, 'default')
    return {'message': message, 'keyboard': pr_buttons + [[button_create_rp], [button_main]]}


def rp_profile_display(profile_id):
    rp_profile = user_class.get_rp_profile(profile_id)
    if not rp_profile:
        return {'message': 'Такой анкеты не существует', 'attachment': ''}
    profile = dict({'message': '', 'attachment': ''})
    profile['message'] += f'Имя: {rp_profile.name}\n'
    if rp_profile.gender != 'Не указано':
        profile['message'] += f'Пол: {rp_profile.gender}\n'
    user_setting_list = user_class.ProfileSettingList().get_setting_list(profile_id)
    user_setting_list = [i.setting.title for i in user_setting_list]
    if user_setting_list:
        profile['message'] += f'Сеттинг: {", ".join(user_setting_list)}\n'
    profile['message'] += f'Описание: {rp_profile.description}\n'
    profile['attachment'] = ','.join(json.loads(rp_profile.arts))
    return profile


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
                                      {'menu_id': 'user_profiles', 'arguments': None})
    return {'message': message, 'keyboard': [[button_return]]}


def change_profile(user_message):
    user_info = user_class.get_user(user_message['from_id'])

    try:
        message = rp_profile_display(user_message['payload']['arguments']['profile_id'])
        user_info.item_id = user_message['payload']['arguments']['profile_id']
    except:
        message = rp_profile_display(user_info.item_id)

    user_info.menu_id = 'change_profile'
    user_info.save()

    message['message'] = 'Ваша анкета:\n\n' + message['message']
    button_main = vk_api.new_button('Главное меню', {'menu_id': 'main', 'arguments': None}, 'primary')
    buttons_change_name = vk_api.new_button('Изменить имя', {'menu_id': 'change_name', 'arguments': None})
    buttons_change_gender = vk_api.new_button('Изменить пол', {'menu_id': 'change_gender', 'arguments': None})
    buttons_change_setting = vk_api.new_button('Изменить сеттинг',
                                               {'menu_id': 'change_setting_list', 'arguments': None})
    buttons_change_description = vk_api.new_button('Изменить описание',
                                                   {'menu_id': 'change_description', 'arguments': None})
    buttons_change_images = vk_api.new_button('Изменить изображения',
                                              {'menu_id': 'change_images', 'arguments': None})
    buttons_delete = vk_api.new_button('Удалить анкету',
                                       {'menu_id': 'confirm_action',
                                        'arguments': {'menu_id': 'delete_profile',
                                                      'arguments': {'profile_id': user_info.item_id}}},
                                       'negative')
    return {'message': message['message'],
            'attachment': message['attachment'],
            'keyboard': [[buttons_change_name, buttons_change_description],
                         [buttons_change_gender, buttons_change_setting],
                         [buttons_change_images],
                         [buttons_delete],
                         [button_main]]}


def change_name(user_message):
    user_info = user_class.get_user(user_message['from_id'])
    user_info.menu_id = 'save_name'
    user_info.save()
    message = 'Введите имя вашего персонажа'
    button_return = vk_api.new_button('Вернуться к анкете',
                                      {'menu_id': 'change_profile', 'arguments': None}, 'negative')
    return {'message': message, 'keyboard': [[button_return]]}


def save_name(user_message):
    name_len = 25
    symbols = 'abcdefghijklmnopqrstuvwxyz' + 'абвгдеёжзийклмнопрстуфхцчшщьыъэюя' + '1234567890_-,. '
    button_return = vk_api.new_button('Вернуться к анкете',
                                      {'menu_id': 'change_profile', 'arguments': None}, 'negative')
    button_try_again = vk_api.new_button('Ввести имя снова',
                                         {'menu_id': 'change_name', 'arguments': None}, 'positive')
    if len(user_message['text']) > 25:
        message = f'Длина имени превосходит {name_len} символов.\n Придумайте более короткий вариант.'
        return {'message': message, 'keyboard': [[button_return, button_try_again]]}

    if len(user_message['text']) == 0:
        message = f'Это не слишком похоже на имя персонажа, вам так не кажется?'
        return {'message': message, 'keyboard': [[button_return, button_try_again]]}

    if not all([i in symbols for i in user_message['text'].lower()]):
        error_symbols = ['"' + i.replace('\\', '\\\\') + '"' for i in user_message['text'].lower() if i not in symbols]
        message = f"Имя содержит недопустимые символы: {' '.join(error_symbols)}"
        return {'message': message, 'keyboard': [[button_return, button_try_again]]}

    user_info = user_class.get_user(user_message['from_id'])
    rp_profile = user_class.get_rp_profile(user_info.item_id)
    rp_profile.name = user_message['text']
    rp_profile.save()
    return change_profile(user_message)


def change_gender(user_message):
    user_info = user_class.get_user(user_message['from_id'])
    profile = user_class.get_rp_profile(user_info.item_id)

    if user_message['payload']['arguments']:
        profile.gender = user_message['payload']['arguments']
        profile.save()

    message = 'Выберите пол вашего персонажа'

    gen_btn = list()
    for gen in genders:
        color = 'default'
        if profile.gender == gen:
            color = 'positive'
        gen_btn.append(vk_api.new_button(gen, {'menu_id': 'change_gender', 'arguments': gen}, color))

    button_return = vk_api.new_button('Вернуться к анкете',
                                      {'menu_id': 'change_profile', 'arguments': None}, 'primary')
    return {'message': message, 'keyboard': [gen_btn, [button_return]]}


def change_setting_list(user_message):
    user_info = user_class.get_user(user_message['from_id'])
    profile_id = user_info.item_id
    setting = user_class.SettingList().get_setting_list()
    user_setting = user_class.ProfileSettingList().get_setting_list(profile_id)

    if user_message['payload']['arguments']:
        if user_message['payload']['arguments']['setting_id'] in [i.setting_id for i in user_setting]:
            user_class.ProfileSettingList().delete_setting_from_list(user_message['payload']['arguments']['profile_id'],
                                                                     user_message['payload']['arguments']['setting_id'])

        else:
            user_class.ProfileSettingList().add_setting(user_message['payload']['arguments']['profile_id'],
                                                        user_message['payload']['arguments']['setting_id'])
        user_setting = user_class.ProfileSettingList().get_setting_list(profile_id)
    message = 'Выберите подходящие сеттинги для игры:\n' \
              '• Первое нажатие добавляет в список\n' \
              '• Второе - убирает из списка'

    setting_btn = list()
    user_setting_ids = [i.setting_id for i in user_setting]
    for stt in setting:
        color = 'default'
        if stt.id in user_setting_ids:
            color = 'positive'
        setting_btn.append(vk_api.new_button(stt.title, {'menu_id': 'change_setting_list',
                                                         'arguments': {'setting_id': stt.id,
                                                                       'profile_id': profile_id}}, color))

    button_return = vk_api.new_button('Вернуться к анкете',
                                      {'menu_id': 'change_profile', 'arguments': None}, 'primary')
    return {'message': message, 'keyboard': [setting_btn, [button_return]]}


def change_description(user_message):
    user_info = user_class.get_user(user_message['from_id'])
    user_info.menu_id = 'save_description'
    user_info.save()
    message = 'Введите описание вашего персонажа'
    button_return = vk_api.new_button('Вернуться к анкете',
                                      {'menu_id': 'change_profile', 'arguments': None}, 'negative')
    return {'message': message, 'keyboard': [[button_return]]}


def save_description(user_message):
    description_len = 500
    lines_count = 15
    button_return = vk_api.new_button('Вернуться к анкете',
                                      {'menu_id': 'change_profile', 'arguments': None}, 'negative')
    button_try_again = vk_api.new_button('Ввести описание заново',
                                         {'menu_id': 'change_description', 'arguments': None}, 'positive')
    if len(user_message['text']) > description_len:
        message = f'Длина описания превосходит {description_len} символов.\n' \
                  f'Постарайтесь сократить описание, оставив только самое важное.'
        return {'message': message, 'keyboard': [[button_return, button_try_again]]}

    if len(user_message['text']) == 0:
        message = f'Вам не кажется, что это не слишком подойдёт для описания персонажа?'
        return {'message': message, 'keyboard': [[button_return, button_try_again]]}

    if user_message['text'].count('\n') > lines_count:
        message = f"Вы использовали перенос строки слишком часто, " \
                  f"теперь анкета занимает слишком много места на экране.\n" \
                  f"Попробуйте уменьшить количество переносов на новую строку."
        return {'message': message, 'keyboard': [[button_return, button_try_again]]}

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
                                      {'menu_id': 'change_profile', 'arguments': None}, 'negative')
    return {'message': message, 'keyboard': [[button_return]]}


def input_images(user_message):
    # TODO добавить проверки ввода
    images_attachments = [i['photo'] for i in user_message['attachments'] if i['type'] == 'photo']
    images = [f"photo{i['owner_id']}_{i['id']}_{i.get('access_key', '')}" for i in images_attachments]

    message = 'Сохранить эти изображения?'
    button_yes = vk_api.new_button('Да, всё верно', {'menu_id': 'save_images', 'arguments': None}, 'positive')
    button_no = vk_api.new_button('Нет, загрузить другие', {'menu_id': 'change_images', 'arguments': None}, 'negative')
    return {'message': message, 'keyboard': [[button_yes], [button_no]], 'attachment': images}


def save_images(user_message):
    images_attachments = [i['photo'] for i in user_message['attachments'] if i['type'] == 'photo']
    images = [f"photo{i['owner_id']}_{i['id']}_{i.get('access_key', '')}" for i in images_attachments]

    button_return = vk_api.new_button('Вернуться к анкете',
                                      {'menu_id': 'change_profile', 'arguments': None}, 'negative')
    button_try_again = vk_api.new_button('Отправить изображения снова',
                                         {'menu_id': 'change_images', 'arguments': None}, 'positive')
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
                                          {'menu_id': 'choose_profile_to_search', 'arguments': None})
    button_main = vk_api.new_button('Главное меню', {'menu_id': 'main', 'arguments': None}, 'primary')
    return {'message': message, 'keyboard': [[button_by_profile], [button_main]]}


def choose_profile_to_search(user_message):
    profiles = user_class.get_user_profiles(user_message['from_id'])
    message = 'Выберите из списка ваших анкет ту, для которой нужно найти соигроков'
    pr_buttons = list()
    for num, pr in enumerate(profiles):
        pr_buttons.append([vk_api.new_button(pr.profile.name,
                                             {'menu_id': 'search_by_profile',
                                              'arguments': {'profile_id': pr.profile.id}})])

    button_main = vk_api.new_button('Главное меню', {'menu_id': 'main', 'arguments': None}, 'primary')
    return {'message': message, 'keyboard': pr_buttons + [[button_main]]}


def search_by_profile(user_message):
    profiles_per_page = 4
    user_info = user_class.get_user(user_message['from_id'])
    try:
        if 'profile_id' in user_message['payload']['arguments']:
            user_info.item_id = user_message['payload']['arguments']['profile_id']
        if 'iter' in user_message['payload']['arguments']:
            user_info.list_iter = user_message['payload']['arguments']['iter']
        user_info.save()
    except:
        pass

    suitable_profiles = user_class.find_suitable_profiles(user_info.item_id)
    sent_profiles = [pr.to_profile_id for pr in user_class.RoleOffer().get_offers_from_user(user_info.id)]
    confirmed_profiles = [pr.from_profile_id for pr in user_class.RoleOffer().get_offers_to_user(user_info.id)]
    message = 'Список анкет подходящих к вашей.\n' \
              'Синим отправленные предложения.\n' \
              'Зелёным - взаимные предложения.'
    pr_buttons = list()
    for pr in suitable_profiles[user_info.list_iter * profiles_per_page:(user_info.list_iter + 1) * profiles_per_page]:
        color = 'default'
        if pr.id in sent_profiles:
            color = 'primary'
            if pr.id in confirmed_profiles:
                color = 'positive'
        pr_buttons.append([vk_api.new_button(pr.name,
                                             {'menu_id': 'show_player_profile',
                                              'arguments': {'profile_id': pr.id}}, color)])

    prew_color, next_color, prew_iter, next_iter = 'default', 'default', user_info.list_iter, user_info.list_iter
    if user_info.list_iter > 0:
        prew_color = 'primary'
        prew_iter = user_info.list_iter - 1
    if (user_info.list_iter + 1) * profiles_per_page < len(suitable_profiles):
        next_color = 'primary'
        next_iter = user_info.list_iter + 1
    button_prew = vk_api.new_button('Предыдущая страница', {'menu_id': 'search_by_profile',
                                                            'arguments': {'iter': prew_iter}}, prew_color)
    button_next = vk_api.new_button('Следующая страница', {'menu_id': 'search_by_profile',
                                                           'arguments': {'iter': next_iter}}, next_color)
    button_main = vk_api.new_button('Главное меню', {'menu_id': 'main', 'arguments': None}, 'primary')
    return {'message': message, 'keyboard': pr_buttons + [[button_prew, button_next]] + [[button_main]]}


def show_player_profile(user_message):
    user_info = user_class.get_user(user_message['from_id'])
    try:
        user_info.tmp_item_id = user_message['payload']['arguments']['profile_id']
        user_info.save()
    except:
        pass

    try:
        if user_message['payload']['arguments']['offer']:
            user_class.RoleOffer().create_offer(user_info.item_id, user_info.tmp_item_id)
        else:
            user_class.RoleOffer().delete_offer(user_info.item_id, user_info.tmp_item_id)
    except Exception as e:
        print(e)
        pass

    message = rp_profile_display(user_info.tmp_item_id)
    sent_profiles = [pr.to_profile_id for pr in user_class.RoleOffer().get_offers_from_user(user_info.id)]
    if user_info.tmp_item_id in sent_profiles:
        button_offer = vk_api.new_button('Отменить предложение', {'menu_id': 'show_player_profile',
                                                                'arguments': {'offer': False}}, 'negative')
    else:
        button_offer = vk_api.new_button('Предложить ролевую', {'menu_id': 'show_player_profile',
                                                                'arguments': {'offer': True}}, 'positive')
    button_back = vk_api.new_button('К списку анкет', {'menu_id': 'search_by_profile', 'arguments': None}, 'primary')
    message.update({'keyboard': [[button_offer], [button_back]]})
    return message


# уведомления


def notifications(user_message):
    message = 'Список уведомлений'
    button_main = vk_api.new_button('Главное меню', {'menu_id': 'main', 'arguments': None}, 'primary')
    return {'message': message, 'keyboard': [[button_main]]}


def role_offers(user_message):
    pass


def user_account(user_message):
    message = 'Настройки аккаунта'
    button_main = vk_api.new_button('Главное меню', {'menu_id': 'main', 'arguments': None}, 'primary')
    return {'message': message, 'keyboard': [[button_main]]}


def empty_func(user_message):
    user_info = user_class.get_user(user_message['from_id'])
    message = 'Этого меню еще нет, но раз вы сюда пришли, вот вам монетка!'
    user_info.money += 1
    user_info.save()
    button_1 = vk_api.new_button('Главное меню', {'menu_id': 'main', 'arguments': None}, 'primary')
    return {'message': message, 'keyboard': [[button_1]]}


# Меню администратора


def admin_setting_list(user_message):
    user_info = user_class.get_user(user_message['from_id'])

    if not user_info.is_admin:
        return access_error(user_message)

    message = 'Список доступных сеттингов.\n' \
              'Выберите тот, который хотите изменить или удалить.'
    setting = user_class.SettingList().get_setting_list()

    setting_btn = list()
    for stt in setting:
        setting_btn.append(vk_api.new_button(stt.title, {'menu_id': 'admin_setting_info',
                                                         'arguments': {'setting_id': stt.id}}, 'default'))

    button_create = vk_api.new_button('Добавить новый сеттинг', {'menu_id': 'admin_create_setting',
                                                                 'arguments': None}, 'positive')
    button_return = vk_api.new_button('Вернуться в главное меню', {'menu_id': 'main', 'arguments': None}, 'primary')
    return {'message': message, 'keyboard': [setting_btn, [button_create], [button_return]]}


def admin_create_setting(user_message):
    new_setting = user_class.SettingList().create_setting()
    if not new_setting:
        return access_error(user_message)
    user_info = user_class.get_user(user_message['from_id'])
    user_info.item_id = new_setting.id
    user_info.save()
    return admin_setting_info(user_message)


def admin_setting_info(user_message):
    user_info = user_class.get_user(user_message['from_id'])

    try:
        user_info.item_id = user_message['payload']['arguments']['setting_id']
    except:
        print('что-то пошло не так')

    user_info.menu_id = 'admin_setting_info'
    user_info.save()
    setting = user_class.SettingList().get_setting(user_info.item_id)
    message = f'Название сеттинга: {setting.title}'
    btn_change = vk_api.new_button('Изменить название сеттинга', {'menu_id': 'admin_change_setting_title', 'arguments': None})
    btn_del = vk_api.new_button('Удалить сеттинг',
                                {'menu_id': 'confirm_action',
                                 'arguments': {'menu_id': 'admin_delete_setting',
                                               'arguments': {'setting_id': user_info.item_id}}},
                                'negative')
    button_return = vk_api.new_button('Вернуться к списку сеттингов',
                                      {'menu_id': 'admin_setting_list', 'arguments': None}, 'primary')
    return {'message': message, 'keyboard': [[btn_change], [btn_del], [button_return]]}


def admin_change_setting_title(user_message):
    user_info = user_class.get_user(user_message['from_id'])
    user_info.menu_id = 'admin_save_setting_title'
    user_info.save()
    message = 'Введите название сеттинга'
    button_return = vk_api.new_button('Вернуться к списку сеттингов',
                                      {'menu_id': 'admin_setting_list', 'arguments': None}, 'negative')
    return {'message': message, 'keyboard': [[button_return]]}


def admin_save_setting_title(user_message):
    name_len = 25
    symbols = 'abcdefghijklmnopqrstuvwxyz' + 'абвгдеёжзийклмнопрстуфхцчшщьыъэюя' + '1234567890_-,. '
    button_return = vk_api.new_button('Вернуться к списку сеттингов',
                                      {'menu_id': 'admin_setting_list', 'arguments': None}, 'negative')
    button_try_again = vk_api.new_button('Ввести название снова',
                                         {'menu_id': 'admin_change_setting_title', 'arguments': None}, 'positive')
    if len(user_message['text']) > 25:
        message = f'Длина названия превосходит {name_len} символов.\n Придумайте более короткий вариант.'
        return {'message': message, 'keyboard': [[button_return, button_try_again]]}

    if len(user_message['text']) == 0:
        message = f'Это не слишком похоже на название сеттинга, вам так не кажется?'
        return {'message': message, 'keyboard': [[button_return, button_try_again]]}

    if not all([i in symbols for i in user_message['text'].lower()]):
        error_symbols = ['"' + i.replace('\\', '\\\\') + '"' for i in user_message['text'].lower() if i not in symbols]
        message = f"Название содержит недопустимые символы: {' '.join(error_symbols)}"
        return {'message': message, 'keyboard': [[button_return, button_try_again]]}

    user_info = user_class.get_user(user_message['from_id'])
    setting = user_class.SettingList().get_setting(user_info.item_id)
    setting.title = user_message['text']
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
                                      {'menu_id': 'admin_setting_list', 'arguments': None}, 'primary')
    return {'message': message, 'keyboard': [[button_return]]}
