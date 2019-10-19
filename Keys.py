import json


class Keys:
    # def __init__(self, keys_filename='keys.txt'):
    def __init__(self, keys_filename='keys_private.txt'):
        try:
            with open(keys_filename, 'r', encoding='utf-8') as keys_file:
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
