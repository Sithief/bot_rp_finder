import json
import logging
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
        'change_gender': change_gender,
        'change_setting_list': change_setting_list,
        'change_rp_rating_list': change_rp_rating_list,
        'change_images': change_images, 'input_images': input_images, 'save_images': save_images
    }
    menus.update(ChangeName().get_menu_ids())
    menus.update(ChangeDescription().get_menu_ids())
    return menus


def change_profile(user_message):
    user_info = user_class.get_user(user_message['from_id'])

    try:
        user_info.item_id = user_message['payload']['args']['profile_id']
    except Exception as error_msg:
        logging.error(str(error_msg))
    message = system.rp_profile_display(user_info.item_id)

    user_info.menu_id = 'change_profile'
    user_info.save()

    message['message'] = 'Ваша анкета:\n\n' + message['message']
    button_main = vk_api.new_button('Главное меню', {'m_id': 'main', 'args': None}, 'primary')
    buttons_change_name = vk_api.new_button('Имя', {'m_id': ChangeName().menu_names['change']})
    buttons_change_gender = vk_api.new_button('Пол', {'m_id': 'change_gender', 'args': None})
    buttons_change_setting = vk_api.new_button('Сеттинг',
                                               {'m_id': 'change_setting_list', 'args': None})
    buttons_change_rp_rating = vk_api.new_button('Рейтинг',
                                                 {'m_id': 'change_rp_rating_list', 'args': None})
    buttons_change_description = vk_api.new_button('Описание', {'m_id': ChangeDescription().menu_names['change']})
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


class InputText:
    check_function = staticmethod(system.input_title_check)
    prew_func = staticmethod(change_profile)
    prew_menu = 'change_profile'
    user_info = None
    menu_prefix = ''
    message_to_user = 'Введите текст'

    def update_db(self, text):
        rp_profile = user_class.get_rp_profile(self.user_info.item_id)
        rp_profile.name = text
        rp_profile.save()

    def __init__(self):
        self.menu_names = {
            'change': self.menu_prefix + 'change',
            'save':   self.menu_prefix + 'save',
        }
        self.menu_ids = {
            self.menu_names['change']: self.change,
            self.menu_names['save']:   self.save,
        }

    def get_menu_ids(self):
        return self.menu_ids

    def init(self, user_message):
        self.user_info = user_class.get_user(user_message['from_id'])

    def change(self, user_message):
        self.init(user_message)
        self.user_info.menu_id = self.menu_names['save']
        self.user_info.save()
        message = self.message_to_user
        button_return = vk_api.new_button('Назад', {'m_id': self.prew_menu}, 'negative')
        return {'message': message, 'keyboard': [[button_return]]}

    def save(self, user_message):
        check_function = self.check_function
        error_message = check_function(user_message['text'])
        if error_message:
            button_return = vk_api.new_button('Назад', {'m_id': self.prew_menu}, 'negative')
            button_try_again = vk_api.new_button('Ввести снова', {'m_id':  self.menu_names['change']}, 'positive')
            return {'message': error_message, 'keyboard': [[button_return, button_try_again]]}

        self.init(user_message)
        self.update_db(user_message['text'])
        return self.prew_func(user_message)


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


class ChangeProfileText(InputText):
    prew_func = staticmethod(change_profile)
    prew_menu = 'change_profile'
    user_info = None


class ChangeName(ChangeProfileText):
    check_function = staticmethod(system.input_title_check)
    menu_prefix = 'profile_name_'
    message_to_user = 'Введите имя персонажа'

    def update_db(self, text):
        rp_profile = user_class.get_rp_profile(self.user_info.item_id)
        rp_profile.name = text
        rp_profile.save()


class ChangeDescription(ChangeProfileText):
    check_function = staticmethod(system.input_description_check)
    menu_prefix = 'profile_description_'
    message_to_user = 'Введите описание персонажа'

    def update_db(self, text):
        rp_profile = user_class.get_rp_profile(self.user_info.item_id)
        rp_profile.description = text
        rp_profile.save()


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
    setting = user_class.SettingList().get_item_list()
    user_setting = user_class.ProfileSettingList().get_list(profile_id)
    user_setting_list = {i.item.id: i for i in user_setting}

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
                user_class.ProfileSettingList().delete_from_list(user_message['payload']['args']['profile_id'],
                                                                 user_message['payload']['args']['setting_id'])
        else:
            user_class.ProfileSettingList().add(user_message['payload']['args']['profile_id'],
                                                user_message['payload']['args']['setting_id'])
            setting_info = user_class.SettingList().get_item(user_message['payload']['args']['setting_id'])
            message += f'\n\n' \
                       f'Вы добавили сеттинг: "{setting_info.title}"\n' \
                       f'Его описание: {setting_info.description}'
        user_setting = user_class.ProfileSettingList().get_list(profile_id)
        user_setting_list = {i.item_id: i for i in user_setting}

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
    user_item_list = user_class.ProfileRpRatingList().get_list(profile_id)
    user_item_dict = {i.item.id: i for i in user_item_list}

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
                user_class.ProfileRpRatingList().delete_from_list(profile_id, item_id)
        else:
            user_class.ProfileRpRatingList().add(profile_id, item_id)
            item_info = user_class.RpRating().get_item(item_id)
            message += f'\n\n' \
                       f'Вы добавили рейтинг: "{item_info.title}"\n' \
                       f'Его описание: {item_info.description}'
        user_item_list = user_class.ProfileRpRatingList().get_list(profile_id)
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
