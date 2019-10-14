import vk_api
import user_class
import json
import text_extension as t_ext

genders = ['Мужской', 'Женский', 'Другой', 'Не указано']
orientation = ['Гетеро', 'Би', 'Гомо', 'Не указано']
fetishes = ['фетиш 1', 'фетиш 2', 'фетиш 3', 'фетиш 4', 'фетиш 5', 'фетиш 6']


def menu_hub(user_message):
    menus = {'main': main,
             'user_profiles': user_profiles,
             'create_profile': create_profile, 'delete_profile': delete_profile,
             'change_profile': change_profile,
             'change_name': change_name, 'save_name': save_name,
             'change_gender': change_gender,
             'change_orientation': change_orientation,
             'change_fetishes': change_fetishes,
             'change_description': change_description, 'save_description': save_description,
             'change_images': change_images, 'input_images': input_images, 'save_images': save_images,
             'profiles_search': profiles_search,
             'choose_profile_to_search': choose_profile_to_search,
             'search_by_profile': search_by_profile,
             'show_player_profile': show_player_profile,
             'notifications': notifications,
             'user_account': user_account}
    if 'payload' in user_message:
        if 'menu_id' in user_message['payload'] and user_message['payload']['menu_id'] in menus:
            return menus[user_message['payload']['menu_id']](user_message)
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
    button_profiles = vk_api.new_button('Мои анкеты', {'menu_id': 'user_profiles'})
    button_search = vk_api.new_button('Найти соигроков', {'menu_id': 'profiles_search'}, 'positive')
    button_notifications = vk_api.new_button('Мои Уведомления', {'menu_id': 'notifications'})
    button_user_account = vk_api.new_button('Настройки аккаунта', {'menu_id': 'user_account'})
    return {'message': message, 'keyboard': [[button_profiles],
                                                  [button_search],
                                                  [button_notifications],
                                                  [button_user_account]]}

# создание и изменение анкет


def user_profiles(user_message):
    profiles = user_class.get_user_profiles(user_message['from_id'])
    message = 'Список ваших анкет:'
    pr_buttons = list()
    for num, pr in enumerate(profiles):
        pr_buttons.append([vk_api.new_button(pr.name,
                                             {'menu_id': 'change_profile',
                                              'arguments': {'profile_id': pr.id}})])

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
    if rp_profile.orientation != 'Не указано':
        profile['message'] += f'Ориентация: {rp_profile.orientation}\n'
    user_fetishes = json.loads(rp_profile.fetish_list)
    if user_fetishes:
        profile['message'] += f'Фетиши: {", ".join(user_fetishes)}\n'
    user_taboos = json.loads(rp_profile.taboo_list)
    if user_taboos:
        profile['message'] += f'Табу: {", ".join(user_taboos)}\n'
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
    buttons_change_orientation = vk_api.new_button('Изменить ориентацию',
                                                   {'menu_id': 'change_orientation', 'arguments': None})
    buttons_change_fetishes = vk_api.new_button('Изменить список фетишей',
                                                {'menu_id': 'change_fetishes', 'arguments': None})
    buttons_change_description = vk_api.new_button('Изменить описание',
                                                   {'menu_id': 'change_description', 'arguments': None})
    buttons_change_images = vk_api.new_button('Изменить изображения',
                                              {'menu_id': 'change_images', 'arguments': None})
    buttons_delete = vk_api.new_button('Удалить анкету',
                                       {'menu_id': 'delete_profile', 'arguments': None}, 'negative')
    return {'message': message['message'],
            'attachment': message['attachment'],
            'keyboard': [[buttons_change_name, buttons_change_description],
                         [buttons_change_gender, buttons_change_orientation],
                         [buttons_change_fetishes, buttons_change_images],
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

    error_symbols = [f'"{i}"' for i in user_message['text'].lower() if i not in symbols]
    if error_symbols:
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


def change_orientation(user_message):
    user_info = user_class.get_user(user_message['from_id'])
    profile = user_class.get_rp_profile(user_info.item_id)

    if user_message['payload']['arguments']:
        profile.orientation = user_message['payload']['arguments']
        profile.save()

    message = 'Выберите сексуальную ориентацию вашего персонажа'

    orient_btn = list()
    for orient in orientation:
        color = 'default'
        if profile.orientation == orient:
            color = 'positive'
        orient_btn.append(vk_api.new_button(orient, {'menu_id': 'change_orientation', 'arguments': orient}, color))

    button_return = vk_api.new_button('Вернуться к анкете',
                                      {'menu_id': 'change_profile', 'arguments': None}, 'primary')
    return {'message': message, 'keyboard': [orient_btn, [button_return]]}


def change_fetishes(user_message):
    user_info = user_class.get_user(user_message['from_id'])
    profile = user_class.get_rp_profile(user_info.item_id)

    user_fetishes = [i for i in json.loads(profile.fetish_list) if i in fetishes]
    user_taboos = [i for i in json.loads(profile.taboo_list) if i in fetishes]
    profile.fetish_list = json.dumps(user_fetishes, ensure_ascii=False)
    profile.taboo_list = json.dumps(user_taboos, ensure_ascii=False)

    if user_message['payload']['arguments']:
        if user_message['payload']['arguments'] in user_fetishes:
            user_fetishes.remove(user_message['payload']['arguments'])
            user_taboos.append(user_message['payload']['arguments'])
            profile.fetish_list = json.dumps(user_fetishes, ensure_ascii=False)
            profile.taboo_list = json.dumps(user_taboos, ensure_ascii=False)

        elif user_message['payload']['arguments'] in user_taboos:
            user_taboos.remove(user_message['payload']['arguments'])
            profile.taboo_list = json.dumps(user_taboos, ensure_ascii=False)

        else:
            user_fetishes.append(user_message['payload']['arguments'])
            profile.fetish_list = json.dumps(user_fetishes, ensure_ascii=False)

        profile.save()

    message = 'Выберите подходящие фетиши:\n' \
              '• Первое нажатие добавляет фетиш\n' \
              '• Второе - переводит в список табу\n' \
              '• Третье - убирает из списков'

    fetish_btn = list()
    for fetish in fetishes:
        color = 'default'
        if fetish in user_fetishes:
            color = 'positive'
        elif fetish in user_taboos:
            color = 'negative'
        fetish_btn.append(vk_api.new_button(fetish, {'menu_id': 'change_fetishes', 'arguments': fetish}, color))

    button_return = vk_api.new_button('Вернуться к анкете',
                                      {'menu_id': 'change_profile', 'arguments': None}, 'primary')
    return {'message': message, 'keyboard': [fetish_btn, [button_return]]}


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
        pr_buttons.append([vk_api.new_button(pr.name,
                                             {'menu_id': 'search_by_profile',
                                              'arguments': {'profile_id': pr.id}})])

    button_main = vk_api.new_button('Главное меню', {'menu_id': 'main', 'arguments': None}, 'primary')
    return {'message': message, 'keyboard': pr_buttons + [[button_main]]}


def search_by_profile(user_message):
    profiles_per_page = 5
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
                                              'arguments': {'profile_id': pr.id,
                                                            'prew_menu_id': 'search_by_profile',
                                                            'prew_menu_label': 'К списку анкет'}}, color)])

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
    return {'message': message, 'keyboard': pr_buttons + [[button_prew, button_main, button_next]]}


def choose_preset_to_search(user_message):
    pass


def search_by_preset(user_message):
    pass


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

    sent_profiles = [pr.to_profile_id for pr in user_class.RoleOffer().get_offers_from_user(user_info.id)]
    confirmed_profiles = [pr.from_profile_id for pr in user_class.RoleOffer().get_offers_to_user(user_info.id)]

    message = rp_profile_display(user_info.tmp_item_id)
    if user_info.tmp_item_id in sent_profiles and user_info.tmp_item_id in confirmed_profiles:
        player_id = user_class.get_profile_owner(user_info.tmp_item_id)
        player_info = user_class.get_user(player_id)
        message['message'] = f'Анкета игрока [id{player_info.id}|{player_info.name}]\n' + \
                             f'У вас взаимная симпатия, можете ' \
                             f'{t_ext.gender_msg("ему", "ей", player_info.is_fem)} написать.\n\n' + \
                             message['message']

    if user_info.tmp_item_id in sent_profiles:
        button_offer = vk_api.new_button('Отменить предложение', {'menu_id': 'show_player_profile',
                                                                  'arguments': {'offer': False}}, 'negative')
    else:
        button_offer = vk_api.new_button('Предложить ролевую', {'menu_id': 'show_player_profile',
                                                                'arguments': {'offer': True}}, 'positive')

    try:
        button_back = vk_api.new_button(user_message['payload']['arguments']['prew_menu_label'],
                                        {'menu_id': user_message['payload']['arguments']['prew_menu_id'],
                                         'arguments': None}, 'primary')
    except:
        button_back = vk_api.new_button('В главное меню',
                                        {'menu_id': 'main',
                                         'arguments': None}, 'primary')
    message.update({'keyboard': [[button_offer], [button_back]]})
    return message


# уведомления


def notifications(user_message):
    message = 'Список уведомлений'
    button_main = vk_api.new_button('Главное меню', {'menu_id': 'main', 'arguments': None}, 'primary')
    return {'message': message, 'keyboard': [[button_main]]}


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
