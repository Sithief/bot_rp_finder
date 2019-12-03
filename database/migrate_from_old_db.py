import sqlite3
import json
from bot_rp_finder.vk_api.Keys import Keys
from bot_rp_finder.database import db_api
from bot_rp_finder.vk_api import vk_api


def load_from_old_db(filename):
    json_fields = ['rating', 'race', 'theme', 'Rtheme', 'gender', 'image']
    connect = sqlite3.connect(filename)
    cursor = connect.cursor()
    cursor.execute("SELECT * FROM user")
    user_info = cursor.fetchall()
    cursor.execute('PRAGMA table_info(user)')
    table_info = [i[1] for i in cursor.fetchall()]
    connect.close()
    users_info = [dict(zip(table_info, i)) for i in user_info]
    for user in users_info:
        for field in json_fields:
            user[field] = json.loads(user[field])
    return users_info


def additional_field(rp_profile, old_list, orm_class):
    for item in old_list:
        if item not in [i.title for i in orm_class().additional_field().get_item_list()]:
            new_item = orm_class().additional_field().create_item()
            new_item.title = item
            new_item.save()
    item_list = [i for i in orm_class().additional_field().get_item_list() if i.title in old_list]
    for item in item_list:
        orm_class().add(rp_profile.id, item.id)


def write_to_new_db(old_data):
    db_api.init_db()
    for num, user in enumerate(old_data):
        user_info = bot_api.get_user_info(user['uid'])
        new_user = db_api.User().create_user(user_id=user_info['id'],
                                             name=user_info['first_name'],
                                             is_fem=user_info['sex'] % 2)
        new_user.money = user['user_money']
        new_user.save()

        rp_profile = db_api.RpProfile().create_profile(user['uid'])
        rp_profile.name = user_info['first_name']
        rp_profile.description = user['about_caracter'] + '\n' + user['story']
        rp_profile.arts = user['image']
        rp_profile.save()

        additional_field(rp_profile, user['rating'], db_api.ProfileRpRatingList)
        additional_field(rp_profile, user['theme'], db_api.ProfileSettingList)
        additional_field(rp_profile, user['gender'], db_api.ProfileGenderList)
        additional_field(rp_profile, user['race'], db_api.ProfileSpeciesList)

        print(f'write {num+1}/{len(old_data)}')


if __name__ == '__main__':
    bot_api = vk_api.Api(Keys().get_group_token(), 'main')
    if not bot_api.valid:
        print('Токен для VK API не подходит')
        exit(1)
    print('start loading old data')
    old_info = load_from_old_db('../../bot_data/RPF.db')
    print('old data loaded')
    print('write to new db')
    write_to_new_db(old_info[:])
