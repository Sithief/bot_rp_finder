import logging
import threading
from vk_api import vk_api
from vk_api.Keys import Keys


def send(stdin):
    bot_api = vk_api.Api(Keys().get_group_token(), 'msg_send')
    while threading.main_thread().is_alive():
        try:
            peer_id, payload = stdin.get()
        except Exception as error_msg:
            logging.error(f'msg send: {error_msg}')
            continue
        bot_api.msg_send(peer_id=peer_id, payload=payload)

