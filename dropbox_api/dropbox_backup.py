import time
import requests
import json
import logging
import os
from vk_api.Keys import Keys


def upload_file(file_name):
    token = Keys().get_dropbox_token()
    if token:
        try:
            update_time = time.localtime(time.time())
            url = "https://content.dropboxapi.com/2/files/upload"
            dropbox_arg = {
                'path': f'/bot_rp_finder/%02d.%02d.%02d_{Keys().get_group_id()}_{os.path.basename(file_name)}' %
                        (update_time.tm_mday, update_time.tm_mon, update_time.tm_year % 100),
                'mode': {'.tag': 'overwrite'}
            }
            headers = {
                "Authorization": "Bearer " + token,
                "Content-Type": "application/octet-stream",
                "Dropbox-API-Arg": json.dumps(dropbox_arg, ensure_ascii=False)
            }
            r = requests.post(url, headers=headers, data=open(file_name, 'rb').read())
            logging.info(f'upload backup to dropbox {r.status_code}')
        except Exception as e:
            logging.error(f'dropbox Exception: {e}')


def backup_db():
    upload_file(Keys().get_db_filename())
