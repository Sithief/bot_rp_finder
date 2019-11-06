import logging
from bot_rp_finder.vk_api import vk_api
from bot_rp_finder.database import user_class
from bot_rp_finder.menu import system


def get_menus():
    menus = {'admin_menu': admin_menu}
    menus.update(SettingConfiguration().get_menu_ids())
    menus.update(RpRatingConfiguration().get_menu_ids())
    menus.update(GenderConfiguration().get_menu_ids())
    menus.update(SpeciesConfiguration().get_menu_ids())
    return menus

# Меню администратора


def admin_menu(user_message):
    message = 'Меню администратора'
    button_admin_setting = vk_api.new_button('Настройки списка сеттингов',
                                             {'m_id': SettingConfiguration().menu_names['item_list']})
    button_admin_rp_rating = vk_api.new_button('Настройки списка рейтингов ролевой',
                                               {'m_id': RpRatingConfiguration().menu_names['item_list']})
    button_admin_gender = vk_api.new_button('Настройки списка гендеров анкеты',
                                            {'m_id': GenderConfiguration().menu_names['item_list']})
    button_admin_species = vk_api.new_button('Настройки списка видов существ',
                                             {'m_id': SpeciesConfiguration().menu_names['item_list']})
    button_main = vk_api.new_button('Главное меню', {'m_id': 'main'}, 'primary')
    return {'message': message, 'keyboard': [[button_admin_setting],
                                             [button_admin_rp_rating],
                                             [button_admin_gender],
                                             [button_admin_species],
                                             [button_main]]}


class AdditionalField:
    user_info = None
    table_class = None

    menu_prefix = ''

    def __init__(self):
        self.menu_names = {
            'create':             self.menu_prefix + 'create',
            'item_list':          self.menu_prefix + 'item_list',
            'info':               self.menu_prefix + 'info',
            'change_title':       self.menu_prefix + 'change_title',
            'change_description': self.menu_prefix + 'change_description',
            'save_title':         self.menu_prefix + 'save_title',
            'save_description':   self.menu_prefix + 'save_description',
            'delete':             self.menu_prefix + 'delete'
        }
        self.menu_ids = {
            self.menu_names['create']:             self.create,
            self.menu_names['item_list']:          self.item_list,
            self.menu_names['info']:               self.info,
            self.menu_names['change_title']:       self.change_title,
            self.menu_names['change_description']: self.change_description,
            self.menu_names['save_title']:         self.save_title,
            self.menu_names['save_description']:   self.save_description,
            self.menu_names['delete']:             self.delete
        }

    def get_menu_ids(self):
        return self.menu_ids

    def init(self, user_message):
        self.user_info = user_class.get_user(user_message['from_id'])

    def create(self, user_message):
        new_item = self.table_class.create_item()
        if not new_item:
            return system.access_error()

        self.init(user_message)
        self.user_info.item_id = new_item.id
        self.user_info.save()
        return self.info(user_message)

    def item_list(self, user_message):
        self.init(user_message)

        if not self.user_info.is_admin:
            return system.access_error()

        message = 'Список доступных объектов.\n' \
                  'Выберите тот, который хотите изменить или удалить.'
        item_list = self.table_class.get_item_list()

        item_btn = list()
        for item in item_list:
            item_btn.append(vk_api.new_button(item.title, {'m_id': self.menu_names['info'],
                                                           'args': {'item_id': item.id}}))

        button_create = vk_api.new_button('Добавить новый объект',
                                          {'m_id': self.menu_names['create'], 'args': None}, 'positive')
        button_return = vk_api.new_button('Вернуться в главное меню', {'m_id': 'main', 'args': None}, 'primary')
        return {'message': message, 'keyboard': [item_btn, [button_create], [button_return]]}

    def info(self, user_message):
        self.init(user_message)
        try:
            self.user_info.item_id = user_message['payload']['args']['item_id']
        except:
            print('что-то пошло не так')

        self.user_info.menu_id = self.menu_names['info']
        self.user_info.save()
        item = self.table_class.get_item(self.user_info.item_id)
        message = f'Название: {item.title}\n' \
                  f'Описание: {item.description}'
        btn_change_title = vk_api.new_button('Изменить название', {'m_id': self.menu_names['change_title']})
        btn_change_description = vk_api.new_button('Изменить описание', {'m_id': self.menu_names['change_description']})
        btn_del = vk_api.new_button('Удалить', {
            'm_id': 'confirm_action',
            'args': {'m_id': self.menu_names['delete'], 'args': {'item_id': self.user_info.item_id}}
        }, 'negative')
        button_return = vk_api.new_button('Вернуться к списку',
                                          {'m_id': self.menu_names['item_list']}, 'primary')
        return {'message': message, 'keyboard': [[btn_change_title],
                                                 [btn_change_description],
                                                 [btn_del],
                                                 [button_return]]}

    def __change_text__(self, message, menu_id):
        self.user_info.menu_id = menu_id
        self.user_info.save()
        button_return = vk_api.new_button('Назад', {'m_id': self.menu_names['info'], 'args': None}, 'negative')
        return {'message': message, 'keyboard': [[button_return]]}

    def change_title(self, user_message):
        self.init(user_message)
        return self.__change_text__('Введите новое название', self.menu_names['save_title'])

    def change_description(self, user_message):
        self.init(user_message)
        return self.__change_text__('Введите новое описание', self.menu_names['save_description'])

    def __save_text__(self, user_message, check_function, try_again):
        error_message = check_function(user_message['text'])
        if error_message:
            button_return = vk_api.new_button('Назад', {'m_id': self.menu_names['info']}, 'negative')
            button_try_again = vk_api.new_button('Ввести снова', {'m_id': try_again}, 'positive')
            return False, {'message': error_message, 'keyboard': [[button_return, button_try_again]]}
        return True, {'item_id': self.user_info.item_id, 'text': user_message['text']}

    def save_title(self, user_message):
        self.init(user_message)
        status, data = self.__save_text__(user_message,
                                          check_function=system.input_title_check,
                                          try_again=self.menu_names['change_title'])
        if status:
            item = self.table_class.get_item(data['item_id'])
            item.title = data['text']
            item.save()
            return self.info(user_message)
        return data

    def save_description(self, user_message):
        self.init(user_message)
        status, data = self.__save_text__(user_message,
                                          check_function=system.input_description_check,
                                          try_again=self.menu_names['change_description'])
        if status:
            item = self.table_class.get_item(data['item_id'])
            item.description = data['text']
            item.save()
            return self.info(user_message)
        return data

    def delete(self, user_message):
        self.init(user_message)
        try:
            item_title = self.table_class.get_item(self.user_info.item_id).title
            if self.table_class.delete_item(self.user_info.item_id):
                message = f'Объект "{item_title}" успешно удален.'
            else:
                message = f'Во время удаления произошла ошибка, попробуйте повторить запрос через некоторое время.'
        except Exception as error_message:
            logging.error(f'{error_message}')
            message = f'Во время удаления произошла ошибка, попробуйте повторить запрос через некоторое время.'
        button_return = vk_api.new_button('Назад', {'m_id': self.menu_names['item_list']}, 'primary')
        return {'message': message, 'keyboard': [[button_return]]}


class SettingConfiguration(AdditionalField):
    table_class = user_class.SettingList()
    menu_prefix = 'admin_setting_'


class RpRatingConfiguration(AdditionalField):
    table_class = user_class.RpRating()
    menu_prefix = 'admin_rp_rating_'


class GenderConfiguration(AdditionalField):
    table_class = user_class.Gender()
    menu_prefix = 'admin_gender_'


class SpeciesConfiguration(AdditionalField):
    table_class = user_class.Species()
    menu_prefix = 'admin_species_'
