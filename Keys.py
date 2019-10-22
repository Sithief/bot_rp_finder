import json
import os


class Keys:
    # def __init__(self, keys_filename='keys.txt'):
    def __init__(self, keys_filename='keys_private.txt', db_filename='bot_data.db',
                 bot_data_dir='~\\Documents\\bot_data'):
        bot_path = os.path.expanduser(bot_data_dir)
        if not os.path.exists(bot_path):
            print(f'Директрия {bot_path} не обнаружена и будет создана')
            os.mkdir(bot_path)

        self.__db_filename = os.path.join(bot_path, db_filename)
        self.__keys_filename = os.path.join(bot_path, keys_filename)

        if not os.path.exists(self.__keys_filename):
            print(f'Файл с ключами не найден и будет создан в директории: {bot_path}')
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
            print(e)
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
