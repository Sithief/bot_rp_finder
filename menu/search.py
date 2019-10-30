import time
import json
from bot_rp_finder.vk_api import vk_api
from bot_rp_finder.database import user_class
from bot_rp_finder.menu import system


def get_menus():
    menus = {
        'profiles_search': profiles_search,
        'choose_profile_to_search': choose_profile_to_search,
        'search_by_profile': search_by_profile,
        'show_player_profile': show_player_profile,
    }
    return menus

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

    message = system.rp_profile_display(user_info.tmp_item_id)
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
