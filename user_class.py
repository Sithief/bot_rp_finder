import peewee
import json

# default_need_input = '{"input_type": null, "input_field": null, "next_func": null}'
# db = peewee.SqliteDatabase('people.db')
db = peewee.SqliteDatabase('people.db', pragmas={'journal_mode': 'wal',
                                                 'cache_size': -1 * 64000,  # 64MB
                                                 'foreign_keys': 1,
                                                 'ignore_check_constraints': 0,
                                                 'synchronous': 0})


class User(peewee.Model):
    id = peewee.IntegerField(unique=True)
    name = peewee.CharField()
    is_fem = peewee.BooleanField()
    money = peewee.IntegerField(default=0)
    menu_id = peewee.CharField(default='main')
    item_id = peewee.IntegerField(default=-1)
    tmp_item_id = peewee.IntegerField(default=-1)
    list_iter = peewee.IntegerField(default=0)

    class Meta:
        database = db


class RpProfile(peewee.Model):
    name = peewee.CharField(default='Не указано')
    gender = peewee.CharField(default='Не указано')
    setting_list = peewee.CharField(default='[]')
    description = peewee.CharField(default='Не указано')
    arts = peewee.CharField(default='[]')

    class Meta:
        database = db


class ProfileOwner(peewee.Model):
    profile_id = peewee.IntegerField()
    owner_id = peewee.IntegerField()

    class Meta:
        database = db


class RoleOffer(peewee.Model):
    from_owner_id = peewee.IntegerField()
    from_profile_id = peewee.IntegerField()
    to_owner_id = peewee.IntegerField()
    to_profile_id = peewee.IntegerField()

    class Meta:
        database = db

    def create_offer(self, from_profile_id, to_profile_id):
        try:
            from_owner_id = get_profile_owner(from_profile_id)
            to_owner_id = get_profile_owner(to_profile_id)
            new_rp_offer = self.create(from_owner_id=from_owner_id,
                                       from_profile_id=from_profile_id,
                                       to_owner_id=to_owner_id,
                                       to_profile_id=to_profile_id)
            return new_rp_offer
        except:
            return False

    def get_offers_from_user(self, user_id):
        try:
            user_offers = self.select().where(RoleOffer.from_owner_id == user_id)
            return user_offers
        except self.DoesNotExist:
            return []

    def get_offers_to_user(self, user_id):
        try:
            user_offers = self.select().where(RoleOffer.to_owner_id == user_id)
            return user_offers
        except self.DoesNotExist:
            return []

    def delete_offer(self, from_profile_id, to_profile_id):
        try:
            delete_profile = self.delete().where((RoleOffer.from_profile_id == from_profile_id) &
                                                 (RoleOffer.to_profile_id == to_profile_id))
            delete_profile.execute()
            return True
        except RpProfile.DoesNotExist:
            return False


def get_user_profiles(user_id):
    try:
        profiles_ids = ProfileOwner.select().where(ProfileOwner.owner_id == user_id)
        profiles = [RpProfile.get(RpProfile.id == pr.profile_id) for pr in profiles_ids]
        return profiles
    except ProfileOwner.DoesNotExist:
        return []


def get_profile_owner(profile_id):
    try:
        owner_id = ProfileOwner.get(ProfileOwner.profile_id == profile_id).owner_id
        return owner_id
    except ProfileOwner.DoesNotExist:
        return None


def create_rp_profile(user_id):
    new_rp_profile = RpProfile.create()
    ProfileOwner.create(profile_id=new_rp_profile.id,
                        owner_id=user_id)
    return new_rp_profile


def get_rp_profile(profile_id):
    try:
        rp_profile = RpProfile.get(RpProfile.id == profile_id)
        return rp_profile
    except RpProfile.DoesNotExist:
        return False


def delete_rp_profile(profile_id):
    try:
        delete_profile = RpProfile.delete().where(RpProfile.id == profile_id)
        delete_profile.execute()
        delete_owner = ProfileOwner.delete().where(ProfileOwner.profile_id == profile_id)
        delete_owner.execute()
        return True
    except RpProfile.DoesNotExist:
        return False


def count_similarity_score(user_profile, player_profile):
    score = 0
    user_setting = set(json.loads(user_profile.setting_list))
    player_setting = set(json.loads(player_profile.setting_list))

    score += len(user_setting & player_setting)
    return score


def find_suitable_profiles(profile_id):
    # TODO доделать поиск по остальным параметрам
    try:
        user_profile = get_rp_profile(profile_id)
        other_user_profiles = [profile.id for profile in get_user_profiles(get_profile_owner(profile_id))]
        setting_list = json.loads(user_profile.setting_list)
        suitable_profiles = []
        for setting in setting_list:
            suit_prof = RpProfile.select().where((RpProfile.setting_list.contains(setting) &
                                                  RpProfile.id.not_in(other_user_profiles)))
            suitable_profiles += [sp for sp in suit_prof]

        suitable_profiles_scores = [[profile, count_similarity_score(user_profile, profile)]
                                    for profile in set(suitable_profiles)]
        suitable_profiles_scores.sort(key=lambda x: x[1], reverse=True)
        suitable_profiles = [profile[0] for profile in suitable_profiles_scores]
        return suitable_profiles
    except RpProfile.DoesNotExist:
        return []


def create_user(user_id, name, is_fem):
    new_user = User.create(id=user_id, name=name, is_fem=is_fem)
    return new_user


def get_user(user_id):
    try:
        user = User.get(User.id == user_id)
        return user
    except User.DoesNotExist:
        return False


if __name__ == "__main__":
    User.create_table()
