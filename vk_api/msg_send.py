import logging
import threading
from bot_rp_finder.vk_api import vk_api
from bot_rp_finder.vk_api.Keys import Keys


def send(stdin):
    bot_api = vk_api.Api(Keys().get_group_token(), 'msg_send')
    while threading.main_thread().is_alive():
        try:
            peer_id, payload = stdin.get(timeout=120)
        except Exception as error_msg:
            logging.error(f'msg send: {error_msg}')
            continue
        bot_api.msg_send(peer_id=peer_id, payload=payload)

