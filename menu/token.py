from database import db_api


class Token:
    info = None
    menu_id = None
    menu_args = None
    bot_message = None
    user_actions = None

    def __init__(self, message):
        self.msg_text = message['text']
        self.msg_attach = message['attachments']
        user = db_api.User().get_user(message['from_id'])
        if user:
            self.update_user_info(user, message)

    def update_user_info(self, user, message):
        self.info = user
        if message.get('payload', None) and message['payload'].get('m_id', None):
            self.menu_id = message['payload']['m_id']
            if message['payload'].get('args', None):
                self.menu_args = message['payload']['args']
            else:
                self.menu_args = dict()
        else:
            self.menu_id = self.info.menu_id
            self.menu_args = dict()

        print('menu id:', self.menu_id)
