import logging
from vk_api import vk_api
from database import db_api
from menu import system
from menu import user_profile
from menu import text_extension as t_ext
from menu import notification


def get_menus():
    menus = {
        'profiles_search': profiles_search,
        'search_by_preset': search_by_preset,
        'choose_preset_to_search': choose_preset_to_search,
        'create_preset': create_preset,
        'delete_preset': delete_preset,
        'change_preset': change_preset,
        'show_all_player_profiles': show_all_player_profiles,
        'show_player_profile': show_player_profile,
    }
    menus.update(ChangeName().get_menu_ids())
    menus.update(ChangeSettingList().get_menu_ids())
    menus.update(ChangeRpRatingList().get_menu_ids())
    menus.update(ChangeGenderList().get_menu_ids())
    menus.update(ChangeSpeciesList().get_menu_ids())
    menus.update(ChangeOptionalTagList().get_menu_ids())
    return menus

# поиск со-игроков


def profiles_search(user):
    # message = 'Поиск соигроков'
    # # button_by_profile = vk_api.new_button('Найти соигроков подходящих к анкете',
    # #                                       {'m_id': 'choose_profile_to_search', 'args': None})
    # button_by_preset = vk_api.new_button('Найти соигроков по пресету', {'m_id': 'choose_preset_to_search'})
    # button_main = vk_api.new_button('Главное меню', {'m_id': 'main', 'args': None}, 'primary')
    # return {'message': message, 'keyboard': [[button_by_preset],
    #                                          # [button_by_profile],
    #                                          [button_main]]}
    return choose_preset_to_search(user)


def choose_preset_to_search(user):
    message = 'Выберите один из списка ваших поисковых пресетов:'
    profiles = db_api.RpProfile().get_user_profiles(user.info.id, search_preset=True)
    pr_buttons = list()
    for num, pr in enumerate(profiles):
        message += f'\n{num+1}){pr.name}'
        pr_buttons.append([vk_api.new_button(pr.name,
                                             {'m_id': 'change_preset',
                                              'args': {'item_id': pr.id}})])

    if len(profiles) < 4:
        button_create_preset = vk_api.new_button('создать новый пресет', {'m_id': 'create_preset'}, 'primary')
    else:
        button_create_preset = vk_api.new_button('создать новый пресет', {'m_id': 'choose_preset_to_search'})

    # button_main = vk_api.new_button('Главное меню', {'m_id': 'main', 'args': None}, 'primary')
    return {'message': message, 'keyboard': pr_buttons + [[button_create_preset]]}


def create_preset(user):
    search_preset = db_api.RpProfile().create_profile(user.info.id, search_preset=True)
    user.info.item_id = search_preset.id
    user.info.save()
    return change_preset(user)


def delete_preset(user):
    try:
        profile = db_api.RpProfile().get_profile(user.info.item_id).name
        if db_api.RpProfile().delete_profile(user.info.item_id):
            message = f'Ваш поисковой пресет "{profile}" успешно удален.'
        else:
            message = f'Во время удаления пресета произошла ошибка, попробуйте повторить запрос через некоторое время.'
    except:
        message = f'Во время удаления пресета произошла ошибка, попробуйте повторить запрос через некоторое время.'
    button_return = vk_api.new_button('Вернуться к списку пресетов',
                                      {'m_id': 'choose_preset_to_search', 'args': None})
    return {'message': message, 'keyboard': [[button_return]]}


def change_preset(user):
    if 'item_id' in user.menu_args:
        user.info.item_id = user.menu_args['item_id']
    else:
        return system.access_error()
    message = system.rp_profile_display(user.info.item_id)

    user.info.menu_id = 'change_preset'
    user.info.save()

    message['message'] = 'Пресет для поиска:\n\n' + message['message']
    button_main = vk_api.new_button('Назад', {'m_id': 'choose_preset_to_search'}, 'primary')
    buttons_change_name = vk_api.new_button('Название', {
        'm_id': ChangeName().menu_names['change'],
        'args': {'profile_id': user.menu_args['item_id']}
    })
    buttons_change_gender = vk_api.new_button('Пол', {'m_id': ChangeGenderList().menu_names['change']})
    buttons_change_setting = vk_api.new_button('Сеттинг', {'m_id': ChangeSettingList().menu_names['change']})
    buttons_change_rp_rating = vk_api.new_button('Рейтинг', {'m_id': ChangeRpRatingList().menu_names['change']})
    buttons_change_optional_tag = vk_api.new_button('Теги', {'m_id': ChangeOptionalTagList().menu_names['change']})
    buttons_change_species = vk_api.new_button('Вид', {'m_id': ChangeSpeciesList().menu_names['change']})
    buttons_delete = vk_api.new_button('Удалить пресет',
                                       {'m_id': 'confirm_action',
                                        'args': {'m_id': 'delete_preset',
                                                 'args': {'profile_id': user.menu_args['item_id']}}},
                                       'negative')
    button_search = vk_api.new_button('Искать по пресету', {'m_id': 'search_by_preset'}, 'positive')
    return {'message': message['message'],
            'attachment': message.get('attachment', []),
            'keyboard': [[buttons_change_name],
                         [buttons_change_gender, buttons_change_species],
                         [buttons_change_setting, buttons_change_optional_tag, buttons_change_rp_rating],
                         [button_search],
                         [buttons_delete],
                         [button_main]]}


class PresetList(user_profile.CheckButton):
    prew_func = staticmethod(change_preset)
    prew_menu = 'change_preset'


class ChangeSettingList(PresetList):
    table_class = db_api.ProfileSettingList()
    menu_prefix = 'preset_setting_'


class ChangeRpRatingList(PresetList):
    table_class = db_api.ProfileRpRatingList()
    menu_prefix = 'preset_rp_rating_'


class ChangeSpeciesList(PresetList):
    table_class = db_api.ProfileSpeciesList()
    menu_prefix = 'preset_species_'


class ChangeGenderList(PresetList):
    table_class = db_api.ProfileGenderList()
    menu_prefix = 'preset_gender_'


class ChangeOptionalTagList(PresetList):
    table_class = db_api.ProfileOptionalTagList()
    menu_prefix = 'preset_optional_tag_'


class ChangeName(user_profile.InputText):
    prew_func = staticmethod(change_preset)
    prew_menu = 'change_preset'
    user_info = None
    check_function = staticmethod(system.input_title_check)
    menu_prefix = 'preset_name_'
    message_to_user = 'Введите название пресета'

    def update_db(self, user):
        rp_profile = db_api.RpProfile().get_profile(user.info.item_id)
        rp_profile.name = user.msg_text
        rp_profile.save()


def search_by_preset(user):
    profiles_per_page = 15
    if 'iter' in user.menu_args:
        user.info.list_iter = user.menu_args['iter']
    user.info.menu_id = 'search_by_preset'
    user.info.save()

    offset = user.info.list_iter * profiles_per_page
    suitable_profiles = db_api.find_suitable_profiles(user.info.item_id, count=profiles_per_page+1, offset=offset)

    sent_offers = [pr.to_owner_id for pr in db_api.RoleOffer().get_offers_from_user(user.info.id) if pr.actual]
    confirmed_offers = [pr.from_owner_id for pr in db_api.RoleOffer().get_offers_to_user(user.info.id) if pr.actual]
    message = 'Список подходящих анкет.\n' \
              'Синим отправленные предложения.\n' \
              'Зелёным - взаимные предложения.'
    pr_buttons = list()
    for pr in suitable_profiles[:profiles_per_page]:
        color = 'default'
        if pr.owner_id in sent_offers:
            color = 'primary'
            if pr.owner_id in confirmed_offers:
                color = 'positive'
        pr_buttons.append(vk_api.new_button(pr.name,
                                            {'m_id': 'show_player_profile',
                                             'args': {'profile_id': pr.id,
                                                      'btn_back': {'label': 'К списку анкет',
                                                                   'm_id': 'search_by_preset'}
                                                      }}, color))
    steps = len(pr_buttons) // 3 * 3
    pr_buttons = [pr_buttons[i:i + 3] for i in range(0, steps, 3)] + [pr_buttons[steps:]]

    prew_color, next_color, prew_iter, next_iter = 'default', 'default', user.info.list_iter, user.info.list_iter
    if user.info.list_iter > 0:
        prew_color = 'primary'
        prew_iter = user.info.list_iter - 1
    if len(suitable_profiles) > profiles_per_page:
        next_color = 'primary'
        next_iter = user.info.list_iter + 1
    button_prew = vk_api.new_button('Предыдущая страница', {'m_id': 'search_by_preset',
                                                            'args': {'iter': prew_iter}}, prew_color)
    button_next = vk_api.new_button('Следующая страница', {'m_id': 'search_by_preset',
                                                           'args': {'iter': next_iter}}, next_color)
    button_main = vk_api.new_button('Назад', {'m_id': 'choose_preset_to_search'}, 'primary')
    return {'message': message, 'keyboard': pr_buttons + [[button_prew, button_main, button_next]]}


def show_player_profile(user):
    if 'profile_id' in user.menu_args:
        user.info.tmp_item_id = user.menu_args['profile_id']
        user.info.save()

    if 'btn_back' in user.menu_args:
        btn_back = user.menu_args['btn_back']
    else:
        btn_back = {'label': 'В главное меню', 'm_id': 'main', 'args': None}

    if 'offer' in user.menu_args:
        send_offer(user.info, user.menu_args['offer'])

    if 'block' in user.menu_args:
        block_user(user.info, user.menu_args['block'])

    message = system.rp_profile_display(user.info.tmp_item_id)
    if message == system.access_error():
        return message

    role_offer = db_api.RoleOffer().get_offer_to_profile(user.info.id, user.info.tmp_item_id)
    if role_offer and role_offer.actual:
        button_offer = vk_api.new_button('Отменить предложение',
                                         {'m_id': 'show_player_profile',
                                          'args': {'offer': False, 'btn_back': btn_back}},
                                         'negative')
    else:
        button_offer = vk_api.new_button('Предложить ролевую',
                                         {'m_id': 'show_player_profile',
                                          'args': {'offer': True, 'btn_back': btn_back}},
                                         'positive')

    block = db_api.BlockedUser().is_profile_blocked(user.info.id, user.info.tmp_item_id)
    if block:
        button_block = vk_api.new_button('Разблокировать',
                                         {'m_id': 'show_player_profile',
                                          'args': {'block': False, 'btn_back': btn_back}},
                                         'positive')
    else:
        button_block = vk_api.new_button('Скрыть пользователя',
                                         {'m_id': 'show_player_profile',
                                          'args': {'block': True, 'btn_back': btn_back}},
                                         'negative')

    profile_owner = db_api.RpProfile().get_profile(user.info.tmp_item_id).owner_id
    button_other_profiles = vk_api.new_button('другие анкеты пользователя',
                                              {'m_id': 'show_all_player_profiles',
                                               'args': {'player_id': profile_owner}})
    button_back = vk_api.new_button('Назад', {'m_id': btn_back['m_id'], 'args': btn_back.get('args', None)}, 'primary')
    message.update({'keyboard': [[button_block, button_offer], [button_other_profiles], [button_back]]})
    return message


def send_offer(user_info, add_offer):
    try:
        role_offer = db_api.RoleOffer().get_offer_to_profile(user_info.id, user_info.tmp_item_id)
        if add_offer:
            if not role_offer:
                new_offer = db_api.RoleOffer().create_offer(user_info.id, user_info.tmp_item_id)
                owner_id = new_offer.to_owner_id
                if db_api.RoleOffer().get_offer_from_profile(user_info.tmp_item_id, user_info.id):
                    title = 'Ответ на предложение ролевой'
                    description = f'Пользователь [id{user_info.id}|{user_info.name}] тоже' \
                                  f' хочет с вами сыграть. Вы можете просмотреть ' \
                                  f'{t_ext.gender_msg("его", "её", user_info.is_fem)} анкеты.'
                else:
                    title = 'Предложение ролевой'
                    description = f'Пользователь [id{user_info.id}|{user_info.name}] ' \
                                  f'{t_ext.gender_msg("предожил", "предожила", user_info.is_fem)}' \
                                  f' вам ролевую, вы можете просмотреть ' \
                                  f'{t_ext.gender_msg("его", "её", user_info.is_fem)} анкеты.'
                buttons = [{'label': 'Анкеты пользователя',
                            'm_id': 'show_all_player_profiles',
                            'args': {'player_id': user_info.id}}]
                notification.create_notification(owner_id, title, description, buttons)
            else:
                role_offer.actual = True
                role_offer.save()
        else:
            role_offer.actual = False
            role_offer.save()
    except Exception as e:
        logging.error(f'sent offer: {e}')
        pass


def block_user(user_info, add_block):
    blocked = db_api.BlockedUser().is_profile_blocked(user_info.id, user_info.tmp_item_id)
    block_profile = db_api.RpProfile().get_profile(user_info.tmp_item_id)
    if block_profile:
        block_user_id = block_profile.owner_id
        if blocked and not add_block:
            db_api.BlockedUser().delete_from_list(user_info.id, block_user_id)
        elif not blocked and add_block:
            db_api.BlockedUser().add(user_info.id, block_user_id)


def show_all_player_profiles(user):
    if 'player_id' not in user.menu_args:
        return system.access_error()
    profiles = db_api.RpProfile().get_user_profiles(user.menu_args['player_id'])
    pr_buttons = list()
    if not profiles:
        message = 'Список анкет пуст'
    else:
        message = 'Список анкет:\n'
        for num, pr in enumerate(profiles):
            message += f'\n{num+1}) {pr.name}'
            pr_buttons.append([vk_api.new_button(f'{pr.name}', {
                'm_id': 'show_player_profile',
                'args': {'profile_id': pr.id,
                         'btn_back': {'m_id': 'show_all_player_profiles',
                                      'args': {'player_id': user.menu_args['player_id']}}}})])

    button_back = vk_api.new_button('Назад', {'m_id': user.info.menu_id}, 'primary')
    return {'message': message, 'keyboard': pr_buttons + [[button_back]]}
