from bot_rp_finder.database import db_api


class Token:
    def __init__(self, message):
        self.msg_text = message['text']
        self.msg_attach = message['attachments']
        self.info = db_api.User().get_user(message['from_id'])
        if message.get('payload', None) and message['payload'].get('menu_id', None):
            self.menu_id = message['payload']['menu_id']
            self.menu_args = message['payload'].get('args', None)
        else:
            self.menu_id = self.info.menu_id
            self.menu_args = None


