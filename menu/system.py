import json
import logging
from bot_rp_finder.vk_api import vk_api
from bot_rp_finder.database import user_class


def get_menus():
    menus = {
        'confirm_action': confirm_action
    }
    return menus


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


def input_title_check(message_text, title_len=25):
    symbols = 'abcdefghijklmnopqrstuvwxyz' + 'абвгдеёжзийклмнопрстуфхцчшщьыъэюя' + "1234567890_-+,. '()"

    if len(message_text) > title_len:
        message = f'Длина текста превосходит {title_len} символов.\n Придумайте более короткий вариант.'
        return message

    elif len(message_text) == 0:
        message = f'Нужно было ввести текст.'
        return message

    elif not all([i in symbols for i in message_text.lower()]):
        error_symbols = ['"' + i.replace('\\', '\\\\') + '"' for i in message_text.lower() if i not in symbols]
        message = f"Текст содержит недопустимые символы: {' '.join(error_symbols)}"
        return message
    return ''


def input_description_check(message_text, description_len=500, lines_count=15):
    if len(message_text) > description_len:
        message = f'Длина описания превосходит {description_len} символов.\n' \
                  f'Постарайтесь сократить описание, оставив только самое важное.'
        return message

    if len(message_text) == 0:
        message = f'Для описания нужно ввести текст.'
        return message

    if message_text.count('\n') > lines_count:
        message = f"Вы использовали перенос строки слишком часто, " \
                  f"теперь описание занимает слишком много места на экране.\n" \
                  f"Попробуйте уменьшить количество переносов на новую строку."
        return message
    return ''


def get_profile_parameter(db_table, profile_id):
    profile_parameter_list = db_table.get_list(profile_id)
    user_want_parameter_list = [i.item.title for i in profile_parameter_list if i.is_allowed]
    user_unwant_parameter_list = [i.item.title for i in profile_parameter_list if not i.is_allowed]
    return user_want_parameter_list, user_unwant_parameter_list


def rp_profile_display(profile_id):
    rp_profile = user_class.get_rp_profile(profile_id)
    if not rp_profile:
        return access_error()
    profile = dict({'message': '', 'attachment': ''})
    profile['message'] += f'Имя: {rp_profile.name}\n'

    gender_list, _ = get_profile_parameter(user_class.ProfileGenderList(), profile_id)
    if gender_list:
        profile['message'] += f'Пол: {", ".join(gender_list)}\n'

    species_list, _ = get_profile_parameter(user_class.ProfileSpeciesList(), profile_id)
    if species_list:
        profile['message'] += f'Вид: {", ".join(species_list)}\n'

    want_rating_list, unwant_rating_list = get_profile_parameter(user_class.ProfileRpRatingList(), profile_id)
    if want_rating_list:
        profile['message'] += f'Желательный рейтинг: {", ".join(want_rating_list)}\n'
    if unwant_rating_list:
        profile['message'] += f'Нежелательный рейтинг: {", ".join(unwant_rating_list)}\n'

    want_setting_list, unwant_setting_list = get_profile_parameter(user_class.ProfileSettingList(), profile_id)
    if want_setting_list:
        profile['message'] += f'Желательный сеттинг: {", ".join(want_setting_list)}\n'
    if unwant_setting_list:
        profile['message'] += f'Нежелательный сеттинг: {", ".join(unwant_setting_list)}\n'

    profile['message'] += f'Описание: {rp_profile.description}\n'
    profile['attachment'] = ','.join(json.loads(rp_profile.arts))
    return profile


def empty_func(user_message):
    user_info = user_class.get_user(user_message['from_id'])
    message = 'Этого меню еще нет, но раз вы сюда пришли, вот вам монетка!'
    user_info.money += 1
    user_info.save()
    button_1 = vk_api.new_button('Главное меню', {'m_id': 'main', 'args': None}, 'primary')
    return {'message': message, 'keyboard': [[button_1]]}


class InputText:
    status = True

    def __init__(self, user_id, next_menu, prew_menu):
        self.user_id = user_id
        self.user_info = user_class.get_user(user_id)
        self.next_menu = next_menu
        self.prew_menu = prew_menu

    def change_text(self, message):
        self.user_info.menu_id = self.next_menu
        self.user_info.save()
        button_return = vk_api.new_button('Назад', {'m_id': self.prew_menu, 'args': None}, 'negative')
        return {'message': message, 'keyboard': [[button_return]]}

    def save_text(self, user_message, check_function):
        self.status = True
        error_message = check_function(user_message)
        if error_message:
            button_return = vk_api.new_button('Назад', {'m_id': self.prew_menu, 'args': None}, 'negative')
            button_try_again = vk_api.new_button('Ввести снова', {'m_id': self.next_menu, 'args': None}, 'positive')
            self.status = False
            return {'message': error_message, 'keyboard': [[button_return, button_try_again]]}
        return {'item_id': self.user_info.item_id, 'text': user_message['text']}

    def save_title(self, user_message, table_class, success_menu):
        data = self.save_text(user_message, check_function=input_title_check)
        if self.status:
            item = table_class.get_item(data['item_id'])
            item.title = data['text']
            item.save()
            return success_menu(user_message)
        return data

    def save_description(self, user_message, table_class, success_menu):
        data = self.save_text(user_message, check_function=input_description_check)
        if self.status:
            item = table_class.get_item(data['item_id'])
            item.description = data['text']
            item.save()
            return success_menu(user_message)
        return data


class ItemMenu:
    def __init__(self, user_id, table_class, prew_menu):
        self.user_info = user_class.get_user(user_id)
        self.table_class = table_class
        self.prew_menu = prew_menu

    def delete_item(self):
        try:
            item_title = self.table_class.get_item(self.user_info.item_id).title
            if self.table_class.delete_item(self.user_info.item_id):
                message = f'Объект "{item_title}" успешно удален.'
            else:
                message = f'Во время удаления произошла ошибка, попробуйте повторить запрос через некоторое время.'
        except Exception as error_message:
            logging.error(f'{error_message}')
            message = f'Во время удаления произошла ошибка, попробуйте повторить запрос через некоторое время.'
        button_return = vk_api.new_button('Назад', {'m_id': self.prew_menu, 'args': None}, 'primary')
        return {'message': message, 'keyboard': [[button_return]]}
