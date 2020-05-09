import configparser
import os
import time
from bot_rp_finder.vk_api import vk_api


current_path = os.path.dirname(os.path.abspath(__file__))
CONF = configparser.ConfigParser()
CONF.read(os.path.join(current_path, 'bot_settings.inf'), encoding='utf-8')
bot_api = vk_api.Api(CONF.get('VK', 'token', fallback='no confirm'), 'main')


def get_all_users():
    offset, step = 0, 200
    conv_info = bot_api.request_get("messages.getConversations",
                                    {'count': step, 'offset': offset})
    if 'response' not in conv_info:
        print('conv_info:', conv_info)
    conv_count = conv_info['response']['count']
    peers = [u['conversation']['peer']['id']
             for u in conv_info['response']['items']
             if u['conversation'].get('can_write', {}).get('allowed')]
    for offset in range(step, min(conv_count, 2000), step):
        print(f'peers_count: {len(peers)}')
        conv_info = {}
        while 'response' not in conv_info:
            conv_info = bot_api.request_get("messages.getConversations",
                                            {'count': step, 'offset': offset})
            if 'response' not in conv_info:
                print('conv_info:', conv_info)
        peers += [u['conversation']['peer']['id']
                  for u in conv_info['response']['items']
                  if u['conversation'].get('can_write', {}).get('allowed')]
    print(f'peers_count: {len(peers)}')
    return peers


def send_messages(peers, payload, time_between=10):
    start_time = time.time()
    for num, peer_id in enumerate(peers):
        S = round(time.time() - start_time)
        M = (S // 60) % 60
        H = (S // 60 // 60)
        S %= 60
        print(f"{num}) {H}:{M}:{S} peer: {peer_id} msg: {bot_api.msg_send(peer_id, payload.copy())}")
        time.sleep(time_between)


if __name__ == "__main__":
    peer_ids = get_all_users()
    send_messages(peer_ids, {"message": "Важная информация!",
                             'attachment': "wall-144135506_10413"})
