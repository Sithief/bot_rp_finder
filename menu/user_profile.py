import json
import logging
import time
from vk_api import vk_api
from menu.token import Token
from database import db_api
from menu import system
from bot_rp_finder.__init__ import *

# создание и изменение анкет


def get_menus():
    menus = {
        'user_profiles': user_profiles,
        'create_profile': create_profile, 'delete_profile': delete_profile,
        'change_profile': change_profile,
        'change_images': change_images, 'save_images': save_images
    }
    menus.update(ChangeName().get_menu_ids())
    menus.update(ChangeDescription().get_menu_ids())
    menus.update(ChangeSettingList().get_menu_ids())
    menus.update(ChangeRpRatingList().get_menu_ids())
    menus.update(ChangeGenderList().get_menu_ids())
    menus.update(ChangeSpeciesList().get_menu_ids())
    menus.update(ChangeOptionalTagList().get_menu_ids())
    return menus


def user_profiles(user):
    profiles = db_api.RpProfile().get_user_profiles(user.info.id)
    message = 'Список ваших анкет:\n' \
              'В скобках указано количество дней, которое анкета будет актуальна. Просто откройте анкету для обновления'
    pr_buttons = list()
    for num, pr in enumerate(profiles):
        days_actual = max(int((db_api.profile_actual_time - (time.time() - pr.create_date)) / (24 * 60 * 60)), 0)
        message += f'\n{num+1}){pr.name} ({days_actual})'
        pr_buttons.append([vk_api.new_button(f'{pr.name} ({days_actual})',
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


def create_profile(user):
    rp_profile = db_api.RpProfile().create_profile(user.info.id)
    user.info.item_id = rp_profile.id
    user.info.save()
    return change_profile(user)


def delete_profile(user):
    try:
        profile = db_api.RpProfile().get_profile(user.info.item_id).name
        if db_api.RpProfile().delete_profile(user.info.item_id):
            message = f'Ваша анкета "{profile}" успешно удалена.'
        else:
            message = f'Во время удаления анкеты произошла ошибка, попробуйте повторить запрос через некоторое время.'
    except:
        message = f'Во время удаления анкеты произошла ошибка, попробуйте повторить запрос через некоторое время.'
    button_return = vk_api.new_button('Вернуться к списку анкет',
                                      {'m_id': 'user_profiles', 'args': None})
    return {'message': message, 'keyboard': [[button_return]]}


def change_profile(user):
    if user.menu_args.get('profile_id', None):
        user.info.item_id = user.menu_args['profile_id']

    profile = db_api.RpProfile().get_profile(user.info.item_id)
    if not profile:
        return system.access_error()

    if user.menu_args.get('link', None) in (True, False):
        profile.show_link = user.menu_args['link']

    profile.create_date = int(time.time())
    profile.save()

    user.info.menu_id = 'change_profile'
    user.info.save()

    message = system.rp_profile_display(user.info.item_id)
    message['message'] = 'Ваша анкета:\n\n' + message['message']
    button_main = vk_api.new_button('Главное меню', {'m_id': 'main', 'args': None}, 'primary')
    buttons_change_name = vk_api.new_button('Имя', {'m_id': ChangeName().menu_names['change']})
    buttons_change_gender = vk_api.new_button('Пол', {'m_id': ChangeGenderList().menu_names['change']})
    buttons_change_setting = vk_api.new_button('Сеттинг', {'m_id': ChangeSettingList().menu_names['change']})
    buttons_change_rp_rating = vk_api.new_button('Рейтинг', {'m_id': ChangeRpRatingList().menu_names['change']})
    buttons_change_species = vk_api.new_button('Вид', {'m_id': ChangeSpeciesList().menu_names['change']})
    buttons_change_optional_tag = vk_api.new_button('Теги', {'m_id': ChangeOptionalTagList().menu_names['change']})
    buttons_change_description = vk_api.new_button('Описание', {'m_id': ChangeDescription().menu_names['change']})
    buttons_change_images = vk_api.new_button('Изображения', {'m_id': 'change_images', 'args': None})
    buttons_delete = vk_api.new_button('Удалить анкету',
                                       {'m_id': 'confirm_action',
                                        'args': {'m_id': 'delete_profile',
                                                 'args': {'profile_id': user.info.item_id}}},
                                       'negative')
    if profile.show_link:
        buttons_show_link = vk_api.new_button('Ваша подпись',
                                              {'m_id': 'change_profile', 'args': {'link': False}}, 'positive')
    else:
        buttons_show_link = vk_api.new_button('Ваша подпись',
                                              {'m_id': 'change_profile', 'args': {'link': True}}, 'negative')
    return {'message': message['message'],
            'attachment': message['attachment'],
            'keyboard': [[buttons_change_name, buttons_change_description, buttons_show_link],
                         [buttons_change_gender, buttons_change_species],
                         [buttons_change_setting, buttons_change_optional_tag, buttons_change_rp_rating],
                         [buttons_change_images],
                         [buttons_delete],
                         [button_main]]}


class InputText:
    check_function = staticmethod(system.input_title_check)
    prew_func = staticmethod(change_profile)
    prew_menu = 'change_profile'
    menu_prefix = ''
    message_to_user = 'Введите текст'

    def update_db(self, user):
        rp_profile = db_api.RpProfile().get_profile(user.info.item_id)
        rp_profile.name = user.msg_text
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

    def change(self, user):
        user.info.menu_id = self.menu_names['save']
        user.info.save()
        message = self.message_to_user
        button_return = vk_api.new_button('Назад', {'m_id': self.prew_menu}, 'negative')
        return {'message': message, 'keyboard': [[button_return]]}

    def save(self, user):
        check_function = self.check_function
        error_message = check_function(user.msg_text)
        if error_message:
            button_return = vk_api.new_button('Назад', {'m_id': self.prew_menu}, 'negative')
            button_try_again = vk_api.new_button('Ввести снова', {'m_id':  self.menu_names['change']}, 'positive')
            return {'message': error_message, 'keyboard': [[button_return, button_try_again]]}

        self.update_db(user)
        return self.prew_func(user)


class CheckButton:
    unique_option = False
    prew_func = staticmethod(change_profile)
    prew_menu = 'change_profile'
    table_class = None
    menu_prefix = ''

    def __init__(self):
        self.menu_names = {
            'change': self.menu_prefix + 'change',
        }
        self.menu_ids = {
            self.menu_names['change']: self.change_list
        }

    def get_menu_ids(self):
        return self.menu_ids

    def user_choise(self, user, user_items_dict):
        item_id = self.menu_prefix + 'id'
        item_info = self.table_class.additional_field().get_item(user.menu_args[item_id])
        if item_info:
            if user.menu_args[item_id] in user_items_dict:
                if user_items_dict[user.menu_args[item_id]].is_allowed:
                    user_items_dict[user.menu_args[item_id]].is_allowed = False
                    user_items_dict[user.menu_args[item_id]].save()
                else:
                    self.table_class.delete_from_list(user.menu_args['profile_id'], user.menu_args[item_id])
            else:
                self.table_class.add(user.menu_args['profile_id'], user.menu_args[item_id])
                return f'\n\n' \
                       f'Вы добавили: "{item_info.title}"\n' \
                       f'Его описание: {item_info.description}'
        return ''

    def user_unique_choise(self, user, user_items_dict):
        item_id = self.menu_prefix + 'id'
        item_info = self.table_class.additional_field().get_item(user.menu_args[item_id])
        if item_info:
            for actual_item_id in user_items_dict:
                self.table_class.delete_from_list(user.menu_args['profile_id'], actual_item_id)

            if user.menu_args[item_id] not in user_items_dict:
                self.table_class.add(user.menu_args['profile_id'], user.menu_args[item_id])
                if item_info:
                    return f'\n\n' \
                           f'Вы добавили: "{item_info.title}"\n' \
                           f'Его описание: {item_info.description}'
        return ''

    def item_buttons(self, profile_id, user_items_dict):
        items = self.table_class.additional_field().get_item_list()
        item_btn = list()
        item_id = self.menu_prefix + 'id'
        for itm in items:
            color = 'default'
            if itm.id in user_items_dict:
                if user_items_dict[itm.id].is_allowed:
                    color = 'positive'
                else:
                    color = 'negative'
            item_btn.append(vk_api.new_button(itm.title,
                                              {'m_id': self.menu_names['change'],
                                               'args': {item_id: itm.id, 'profile_id': profile_id}},
                                              color))
        return item_btn

    def change_list(self, user):
        profile_id = user.info.item_id

        user_item = self.table_class.get_list(profile_id)
        user_items_dict = {i.item.id: i for i in user_item}

        if self.unique_option:
            message = 'Выберите подходящий параметр для персонажа'
        else:
            message = 'Выберите подходящие параметры для персонажа:\n' \
                      '• Первое нажатие добавляет в список\n' \
                      '• Второе переносит в список исключений\n' \
                      '• третье - убирает из списков'

        if user.menu_args:
            if self.unique_option:
                message += self.user_unique_choise(user, user_items_dict)
            else:
                text = self.user_choise(user, user_items_dict)
                message += text
            user_item = self.table_class.get_list(profile_id)
            user_items_dict = {i.item.id: i for i in user_item}

        item_btn = self.item_buttons(profile_id, user_items_dict)
        button_return = vk_api.new_button('Назад', {'m_id': self.prew_menu}, 'primary')
        return {'message': message, 'keyboard': [item_btn, [button_return]]}


class ProfileList(CheckButton):
    prew_func = staticmethod(change_profile)
    prew_menu = 'change_profile'


class ChangeSettingList(ProfileList):
    table_class = db_api.ProfileSettingList()
    menu_prefix = 'profile_setting_'


class ChangeRpRatingList(ProfileList):
    table_class = db_api.ProfileRpRatingList()
    menu_prefix = 'profile_rp_rating_'


class ChangeSpeciesList(ProfileList):
    unique_option = True
    table_class = db_api.ProfileSpeciesList()
    menu_prefix = 'profile_species_'


class ChangeGenderList(ProfileList):
    unique_option = True
    table_class = db_api.ProfileGenderList()
    menu_prefix = 'profile_gender_'


class ChangeOptionalTagList(ProfileList):
    table_class = db_api.ProfileOptionalTagList()
    menu_prefix = 'profile_optional_tag_'


class ChangeProfileText(InputText):
    prew_func = staticmethod(change_profile)
    prew_menu = 'change_profile'


class ChangeName(ChangeProfileText):
    check_function = staticmethod(system.input_title_check)
    menu_prefix = 'profile_name_'
    message_to_user = 'Введите имя персонажа'

    def update_db(self, user):
        rp_profile = db_api.RpProfile().get_profile(user.info.item_id)
        rp_profile.name = user.msg_text
        rp_profile.save()


class ChangeDescription(ChangeProfileText):
    check_function = staticmethod(system.input_description_check)
    menu_prefix = 'profile_description_'
    message_to_user = 'Введите описание персонажа'

    def update_db(self, user):
        rp_profile = db_api.RpProfile().get_profile(user.info.item_id)
        rp_profile.description = user.msg_text
        rp_profile.save()


def change_images(user):
    user.info.menu_id = 'save_images'
    user.info.save()
    message = 'Отправьте до 10 изображений для анкеты.\n' \
              'Лучше всего использовать изображения, на которых хорошо видна внешность персонажа, ' \
              'его характер и подходящая для него обстановка.'
    button_return = vk_api.new_button('Вернуться к анкете',
                                      {'m_id': 'change_profile', 'args': None}, 'negative')
    return {'message': message, 'keyboard': [[button_return]]}


def save_images(user):
    sizes_table = {'w': 2560, 'z': 1080, 'y': 807, 'x': 604}
    images_attachments = [i['photo'] for i in user.msg_attach if i['type'] == 'photo']
    # images = [f"photo{i['owner_id']}_{i['id']}_{i.get('access_key', '')}" for i in images_attachments]
    img_urls = list()
    for img in images_attachments:
        image = max(img['sizes'], key=lambda x: sizes_table.get(x['type'], 0))
        if image['type'] in sizes_table:
            img_urls.append(image['url'])

    if len(img_urls) == 0:
        button_return = vk_api.new_button('Вернуться к анкете',
                                          {'m_id': 'change_profile', 'args': None}, 'negative')
        button_try_again = vk_api.new_button('Отправить снова',
                                             {'m_id': 'change_images', 'args': None}, 'positive')
        message = f'Это не слишком похоже на подходящие для анкеты изображения. Попробуйте загрузить заново.'
        return {'message': message, 'keyboard': [[button_return, button_try_again]]}

    # images = list()
    # for url in img_urls:
    #     img = bot_api.upload_image(url)
    #     if img:
    #         images.append(img)
    images = bot_api.upload_image_list(img_urls)

    user_info = db_api.User().get_user(user.info.id)
    if user_info:
        rp_profile = db_api.RpProfile().get_profile(user_info.item_id)
        if rp_profile:
            rp_profile.arts = json.dumps(images, ensure_ascii=False)
            rp_profile.save()
    message = 'Эти изображения сохранены'
    button_yes = vk_api.new_button('вернуться к анкете',
                                   {'m_id': 'change_profile', 'args': None}, 'positive')
    return {'message': message, 'keyboard': [[button_yes]], 'attachment': images}


def update_images(message):
    print('update_images', message)
    if not message:
        return False
    images_attachments = [i['photo'] for i in message['attachments'] if i['type'] == 'photo']
    images = [f"photo{i['owner_id']}_{i['id']}_{i.get('access_key', '')}" for i in images_attachments]

    print('images', images)
    user_info = db_api.User().get_user(message['peer_id'])
    if user_info:
        rp_profile = db_api.RpProfile().get_profile(user_info.item_id)
        if rp_profile:
            rp_profile.arts = json.dumps(images, ensure_ascii=False)
            rp_profile.save()
            return True
    return False

