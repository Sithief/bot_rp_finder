import requests
import time
import json
import logging
from bot_rp_finder.vk_api import vk_api
from bot_rp_finder.vk_api.Keys import Keys


class LongPoll(vk_api.Api):
    def __init__(self, access_token, group_id, name='name', version='5.92'):
        self.session = requests.session()
        self.group_id = group_id
        self.key = ''
        self.server = ''
        self.ts = 0
        super().__init__(access_token, name, version)
        # print('start message', self.msg_send(363230444, 'бот запущен'))

    def new_long_poll_server(self):
        logging.info('get new long poll server')
        settings = self.request_get('groups.getLongPollServer', {'group_id': self.group_id})
        try:
            self.key = settings['response']['key']
            self.server = settings['response']['server']
            if not self.ts:
                self.ts = settings['response']['ts']
        except Exception as error_msg:
            logging.error(f'{error_msg}')
            self.new_long_poll_server()
            return

    def long_poll(self):
        logging.info('start long poll listen')
        try:
            url = '{server}?act=a_check&key={key}&ts={ts}&wait=60'.format(server=self.server, key=self.key, ts=self.ts)
            request = self.session.get(url)
            receive_time = time.time()
            if request.status_code == 200:
                response = request.json()
            else:
                logging.error(f'request.status_code = {request.status_code}')
                self.new_long_poll_server()
                return []

        except requests.exceptions.RequestException as error_msg:
            logging.error(f'long poll connection problems = {error_msg}')
            self.new_long_poll_server()
            return self.long_poll()

        except Exception as error_msg:
            logging.error(f'long poll connection problems = {error_msg}')
            self.new_long_poll_server()
            return self.long_poll()

        logging.info(f'long poll response: {response}')
        updates = []
        try:
            if 'failed' in response:
                self.new_long_poll_server()
                return []

            if 'ts' in response:
                self.ts = response['ts']

            if 'updates' in response:
                for i in response['updates']:
                    if i['type'] == 'message_new':
                        message = i['object']
                        if not message['out']:
                            message.update({'receive_time': receive_time})
                            if 'attachments' in message:
                                message = self.msg_get(message['id'])
                            if 'payload' in message:
                                message['payload'] = json.loads(message['payload'])
                            updates.append(message)
        except Exception as error_msg:
            logging.error(f'long poll updates: {error_msg}')
            self.new_long_poll_server()
            return []
        return updates

    def unread(self):
        logging.info(f'unread messages check')
        message_text = 'Модуль приёма сообщений был перезагружен. Отправьте команду снова.'
        unread_msg = self.request_get('messages.getConversations', {'filter': 'unanswered'})
        try:
            unread_msg = [i['last_message'] for i in unread_msg['response']['items']]
            for msg in unread_msg:
                sended_message = self.msg_send(msg['peer_id'], {'message': message_text})
                if not sended_message:
                    logging.warning(f'unread messages send {sended_message}')

        except Exception as error_msg:
            logging.error(f'unread_msg: {unread_msg} error: {error_msg}')
            self.new_long_poll_server()
            return


def listen(stdout):
    bot_api = LongPoll(Keys().get_group_token(), Keys().get_group_id(), 'long_poll')
    bot_api.unread()
    bot_api.new_long_poll_server()
    while 1:
        try:
            response = bot_api.long_poll()
            if response:
                stdout.put(response)
            else:
                stdout.put([])
        except Exception as error_msg:
            logging.error(f'long poll listen: {error_msg}')
