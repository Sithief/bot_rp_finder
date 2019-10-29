import peewee
import json
from Keys import Keys

db_filename = Keys().get_db_filename()
db = peewee.SqliteDatabase(db_filename, pragmas={'journal_mode': 'wal',
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
    is_admin = peewee.IntegerField(default=0)

    class Meta:
        database = db


def create_user(user_id, name, is_fem):
    new_user = User.create(id=user_id, name=name, is_fem=is_fem)
    return new_user


def get_user(user_id):
    try:
        user = User.get(User.id == user_id)
        return user
    except User.DoesNotExist:
        return False


class RpProfile(peewee.Model):
    owner_id = peewee.IntegerField()
    name = peewee.CharField(default='Не указано')
    gender = peewee.CharField(default='Не указано')
    description = peewee.CharField(default='Не указано')
    arts = peewee.CharField(default='[]')

    class Meta:
        database = db


def get_user_profiles(owner_id):
    try:
        profiles = RpProfile.select().where(RpProfile.owner_id == owner_id)
        return profiles
    except RpProfile.DoesNotExist:
        return []


def create_rp_profile(user_id):
    new_rp_profile = RpProfile.create(owner_id=user_id)
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
        return True
    except RpProfile.DoesNotExist:
        return False


class RoleOffer(peewee.Model):
    from_owner_id = peewee.IntegerField()
    to_profile_id = peewee.IntegerField()
    to_owner_id = peewee.IntegerField()
    actual = peewee.BooleanField(default=True)

    class Meta:
        database = db
        primary_key = peewee.CompositeKey('from_owner_id', 'to_profile_id')

    def create_offer(self, from_owner_id, to_profile_id):
        try:
            to_owner_id = get_rp_profile(to_profile_id).owner_id
            new_rp_offer = self.create(from_owner_id=from_owner_id,
                                       to_profile_id=to_profile_id,
                                       to_owner_id=to_owner_id)
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

    def offer_to_profile(self, user_id, profile_id):
        try:
            user_offer = self.get((RoleOffer.from_owner_id == user_id) &
                                  (RoleOffer.to_profile_id == profile_id))
            return user_offer
        except self.DoesNotExist:
            return False

    def get_offers_to_profile_owner(self, user_id, profile_id):
        try:
            owner_id = get_rp_profile(profile_id).owner_id
            user_offers = self.select().where((RoleOffer.from_owner_id == user_id) &
                                              (RoleOffer.to_owner_id == owner_id))
            return user_offers
        except self.DoesNotExist:
            return []



class SettingList(peewee.Model):
    title = peewee.CharField(default='Не указано')
    description = peewee.CharField(default='Не указано')

    class Meta:
        database = db

    def create_setting(self):
        try:
            new_setting = self.create()
            return new_setting
        except:
            return False

    def get_setting(self, setting_id):
        try:
            settings = self.get(SettingList.id == setting_id)
            return settings
        except self.DoesNotExist:
            return []

    def get_setting_list(self):
        try:
            settings = self.select()
            return settings
        except self.DoesNotExist:
            return []

    def delete_setting(self, setting_id):
        try:
            delete_relations = ProfileSettingList().delete().where(ProfileSettingList.setting_id == setting_id)
            delete_relations.execute()
            deleted_setting = self.delete().where(SettingList.id == setting_id)
            deleted_setting.execute()
            return True
        except self.DoesNotExist:
            return False


class ProfileSettingList(peewee.Model):
    profile_id = peewee.IntegerField()
    setting_id = peewee.IntegerField()
    is_allowed = peewee.BooleanField(default=True)

    class Meta:
        database = db
        primary_key = peewee.CompositeKey('profile_id', 'setting_id')

    def add_setting(self, profile_id, setting_id):
        try:
            added_setting = self.create(profile_id=profile_id,
                                        setting_id=setting_id)
            return added_setting
        except:
            return False

    def get_setting_list(self, profile_id):
        try:
            setting_list = self.select(ProfileSettingList, SettingList)\
                               .where(ProfileSettingList.profile_id == profile_id)\
                               .join(SettingList, on=(ProfileSettingList.setting_id == SettingList.id).alias('setting'))
            return setting_list
        except self.DoesNotExist:
            return []

    def delete_setting_from_list(self, profile_id, setting_id):
        try:
            delete_setting = self.delete().where((ProfileSettingList.profile_id == profile_id) &
                                                 (ProfileSettingList.setting_id == setting_id))
            delete_setting.execute()
            return True
        except self.DoesNotExist:
            return False


class RpRating(peewee.Model):
    title = peewee.CharField(default='Не указано')
    description = peewee.CharField(default='Не указано')

    class Meta:
        database = db

    def create_item(self):
        try:
            new_rp_rating = self.create()
            return new_rp_rating
        except:
            return False

    def get_item(self, rp_rating_id):
        try:
            rp_rating = self.get(RpRating.id == rp_rating_id)
            return rp_rating
        except self.DoesNotExist:
            return []

    def get_item_list(self):
        try:
            rp_ratings = self.select()
            return rp_ratings
        except self.DoesNotExist:
            return []

    def delete_item(self, rp_rating_id):
        try:
            delete_relations = ProfileRpRatingList().delete().where(ProfileRpRatingList.rp_rating_id == rp_rating_id)
            delete_relations.execute()
            deleted_setting = self.delete().where(RpRating.id == rp_rating_id)
            deleted_setting.execute()
            return True
        except self.DoesNotExist:
            return False


class ProfileRpRatingList(peewee.Model):
    profile_id = peewee.IntegerField()
    item_id = peewee.IntegerField()
    is_allowed = peewee.BooleanField(default=True)

    class Meta:
        database = db
        primary_key = peewee.CompositeKey('profile_id', 'item_id')

    def add_item(self, profile_id, item_id):
        try:
            added_item = self.create(profile_id=profile_id,
                                     item_id=item_id)
            return added_item
        except:
            return False

    def get_item_list(self, profile_id):
        try:
            item_list = self.select(ProfileRpRatingList, RpRating)\
                            .where(ProfileRpRatingList.profile_id == profile_id)\
                            .join(RpRating, on=(ProfileRpRatingList.item_id == RpRating.id).alias('item'))
            return item_list
        except self.DoesNotExist:
            return []

    def delete_item_from_list(self, profile_id, item_id):
        try:
            delete_item = self.delete().where((ProfileRpRatingList.profile_id == profile_id) &
                                              (ProfileRpRatingList.item_id == item_id))
            delete_item.execute()
            return True
        except self.DoesNotExist:
            return False


class Notification(peewee.Model):
    owner_id = peewee.IntegerField(default=0)
    title = peewee.CharField()
    is_read = peewee.BooleanField(default=False)
    create_time = peewee.IntegerField(default=0)
    description = peewee.CharField(default='')
    attachment = peewee.CharField(default='[]')
    buttons = peewee.CharField(default='[]')

    class Meta:
        database = db


def create_notification(owner_id, title):
    new_notification = Notification.create(owner_id=owner_id, title=title)
    return new_notification


def get_user_notifications(owner_id):
    try:
        notifications = Notification.select().where(Notification.owner_id == owner_id)
        return notifications
    except Notification.DoesNotExist:
        return []


def get_notification(notofocation_id):
    try:
        notifications = Notification.get(Notification.id == notofocation_id)
        return notifications
    except Notification.DoesNotExist:
        return []


def delete_notification(notification_id):
    try:
        deleted_notification = Notification.delete().where(Notification.id == notification_id)
        deleted_notification.execute()
        return True
    except Notification.DoesNotExist:
        return False


def count_similarity_score(user_profile, player_profile):
    score = 0
    user_setting = ProfileSettingList().get_setting_list(user_profile.id)
    player_setting = ProfileSettingList().get_setting_list(player_profile.id)

    user_allowed_setting = set(i.setting_id for i in user_setting if i.is_allowed)
    player_allowed_setting = set(i.setting_id for i in player_setting if i.is_allowed)
    user_not_allowed_setting = set(i.setting_id for i in user_setting if not i.is_allowed)
    player_not_allowed_setting = set(i.setting_id for i in player_setting if not i.is_allowed)

    score += len(user_allowed_setting & player_allowed_setting)
    score += len(user_not_allowed_setting & player_not_allowed_setting)

    score -= len(user_allowed_setting & player_not_allowed_setting)
    score -= len(user_not_allowed_setting & player_allowed_setting)

    user_rating = ProfileRpRatingList().get_item_list(user_profile.id)
    player_rating = ProfileRpRatingList().get_item_list(player_profile.id)

    user_allowed_rating = set(i.item_id for i in user_rating if i.is_allowed)
    player_allowed_rating = set(i.item_id for i in player_rating if i.is_allowed)
    user_not_allowed_rating = set(i.item_id for i in user_rating if not i.is_allowed)
    player_not_allowed_rating = set(i.item_id for i in player_rating if not i.is_allowed)

    score += len(user_allowed_rating & player_allowed_rating)
    score += len(user_not_allowed_rating & player_not_allowed_rating)

    score -= len(user_allowed_rating & player_not_allowed_rating)
    score -= len(user_not_allowed_rating & player_allowed_rating)

    return score


def find_suitable_profiles(profile_id):
    # TODO доделать поиск по остальным параметрам
    try:
        user_profile = get_rp_profile(profile_id)
        setting_list = [i.setting_id for i in ProfileSettingList().get_setting_list(profile_id) if i.is_allowed]
        suit_by_setting_ids = [i.profile_id for i in
                               ProfileSettingList.select().where((ProfileSettingList.setting_id.in_(setting_list) &
                                                                  ProfileSettingList.is_allowed))]

        rating_list = [i.item_id for i in ProfileRpRatingList().get_item_list(profile_id) if i.is_allowed]
        suit_by_rating_ids = [i.profile_id for i in
                              ProfileRpRatingList.select().where((ProfileRpRatingList.item_id.in_(rating_list) &
                                                                  ProfileRpRatingList.is_allowed))]

        suit_prof_ids = list(set(suit_by_setting_ids + suit_by_rating_ids))
        suitable_profiles = RpProfile.select().where(RpProfile.id.in_(suit_prof_ids) &
                                                     (RpProfile.owner_id != user_profile.owner_id))

        suitable_profiles_scores = [[profile, count_similarity_score(user_profile, profile)]
                                    for profile in set(suitable_profiles)]
        suitable_profiles_scores.sort(key=lambda x: x[1], reverse=True)
        suitable_profiles = [profile[0] for profile in suitable_profiles_scores]
        return suitable_profiles
    except ProfileSettingList.DoesNotExist or RpProfile.DoesNotExist:
        return []


def init_db():
    User.create_table()
    RpProfile.create_table()
    RoleOffer.create_table()
    SettingList.create_table()
    ProfileSettingList.create_table()
    Notification.create_table()
    RpRating.create_table()
    ProfileRpRatingList.create_table()


if __name__ == "__main__":
    import playhouse.migrate as playhouse_migrate
    migrator = playhouse_migrate.SqliteMigrator(db)

    playhouse_migrate.migrate(
        # migrator.add_column('RoleOffer', 'is_actual', RoleOffer.is_actual),
        migrator.rename_column('RoleOffer', 'is_actual', 'actual'),
        # migrator.drop_column('story', 'some_old_field')
    )
