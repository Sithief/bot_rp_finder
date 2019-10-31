import json
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


def empty_func(user_message):
    user_info = user_class.get_user(user_message['from_id'])
    message = 'Этого меню еще нет, но раз вы сюда пришли, вот вам монетка!'
    user_info.money += 1
    user_info.save()
    button_1 = vk_api.new_button('Главное меню', {'m_id': 'main', 'args': None}, 'primary')
    return {'message': message, 'keyboard': [[button_1]]}


class InputText:
    def __init__(self, user_id, next_menu, prew_menu):
        self.user_id = user_id
        self.user_info = user_class.get_user(user_id)
        self.next_menu = next_menu
        self.prew_menu = prew_menu

    def change_title(self, message):
        self.user_info.menu_id = self.next_menu
        self.user_info.save()
        button_return = vk_api.new_button('Назад', {'m_id': self.prew_menu, 'args': None}, 'negative')
        return {'message': message, 'keyboard': [[button_return]]}

    def save_title(self, user_message):
        error_message = input_title_check(user_message)
        if error_message:
            button_return = vk_api.new_button('Назад', {'m_id': self.prew_menu, 'args': None}, 'negative')
            button_try_again = vk_api.new_button('Ввести снова', {'m_id': self.next_menu, 'args': None}, 'positive')
            return False, {'message': error_message, 'keyboard': [[button_return, button_try_again]]}

        return True, {'item_id': self.user_info.item_id, 'text': user_message['text']}
