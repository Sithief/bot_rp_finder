import json
import os
import logging


class Keys:
    default = {
        'keys_filename': 'keys.txt',
        'db_filename': 'bot_data.db',
        'bot_data_dir': os.path.dirname(os.path.abspath(__file__))
    }

    def __init__(self, file_with_path='path.txt'):
        if not os.path.exists(file_with_path):
            logging.info(f'Файл с путём до дополнительных файлов "path.txt" не найден и будет создан в директории бота')
            json_keys = json.dumps({'keys_filename': self.default['keys_filename'],
                                    'db_filename': self.default['db_filename'],
                                    'bot_data_dir': self.default['bot_data_dir']}, ensure_ascii=False)
            with open(file_with_path, 'w', encoding='utf-8') as keys_file:
                keys_file.write(json_keys)

        try:
            with open(file_with_path, 'r', encoding='utf-8') as keys_file:
                json_keys = keys_file.read()
            keys = json.loads(json_keys)
            keys_filename = keys.get('keys_filename', self.default['keys_filename'])
            db_filename = keys.get('db_filename', self.default['db_filename'])
            bot_data_dir = keys.get('bot_data_dir', self.default['bot_data_dir'])

        except Exception as e:
            logging.error(str(e))
            keys_filename = self.default['keys_filename']
            db_filename = self.default['db_filename']
            bot_data_dir = self.default['bot_data_dir']

        data_path = os.path.expanduser(bot_data_dir)
        if not os.path.exists(data_path):
            logging.info(f'Директрия {data_path} не обнаружена и будет создана')
            os.mkdir(data_path)

        self.__db_filename = os.path.join(os.path.realpath(data_path), db_filename)
        self.__keys_filename = os.path.join(data_path, keys_filename)

        if not os.path.exists(self.__keys_filename):
            logging.info(f'Файл с ключами не найден и будет создан в директории: {data_path}')
            json_keys = json.dumps({'user_token': '',
                                    'group_token': '',
                                    'group_id': 0,
                                    'dropbox_token': ''}, ensure_ascii=False)
            with open(self.__keys_filename, 'w', encoding='utf-8') as keys_file:
                keys_file.write(json_keys)

        try:
            with open(self.__keys_filename, 'r', encoding='utf-8') as keys_file:
                json_keys = keys_file.read()
            keys = json.loads(json_keys)
            self.__user_token = keys.get('user_token', '')
            self.__group_token = keys.get('group_token', '')
            self.__group_id = keys.get('group_id', 0)
            self.__dropbox_token = keys.get('dropbox_token', '')

        except Exception as e:
            logging.error(str(e))
            self.__user_token = ''
            self.__group_token = ''
            self.__group_id = 0
            self.__dropbox_token = ''

    def get_user_token(self):
        return self.__user_token

    def get_group_token(self):
        return self.__group_token

    def get_group_id(self):
        return self.__group_id

    def get_dropbox_token(self):
        return self.__dropbox_token

    def get_db_filename(self):
        return self.__db_filename
