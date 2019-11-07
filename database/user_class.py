import peewee
import logging
from bot_rp_finder.vk_api.Keys import Keys

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

    def get_user(self, user_id):
        try:
            user = self.get(self._schema.model.id == user_id)
            return user
        except self.DoesNotExist:
            return False

    def create_user(self, user_id, name, is_fem):
        new_user = self.create(id=user_id, name=name, is_fem=is_fem)
        return new_user


class RpProfile(peewee.Model):
    owner_id = peewee.IntegerField()
    name = peewee.CharField(default='Не указано')
    gender = peewee.CharField(default='Не указано')
    description = peewee.CharField(default='Не указано')
    arts = peewee.CharField(default='[]')

    class Meta:
        database = db

    def get_profile(self, profile_id):
        try:
            rp_profile = self.get(self._schema.model.id == profile_id)
            return rp_profile
        except self.DoesNotExist:
            return False

    def get_user_profiles(self, owner_id):
        try:
            profiles = self.select().where(self._schema.model.owner_id == owner_id)
            return profiles
        except self.DoesNotExist:
            return []

    def create_profile(self, user_id):
        new_rp_profile = self.create(owner_id=user_id)
        return new_rp_profile

    def delete_profile(self, profile_id):
        try:
            delete_profile = self.delete().where(self._schema.model.id == profile_id)
            delete_profile.execute()
            return True
        except self.DoesNotExist:
            return False


class RoleOffer(peewee.Model):
    from_owner_id = peewee.IntegerField()
    to_owner_id = peewee.IntegerField()
    actual = peewee.BooleanField(default=True)

    class Meta:
        database = db
        primary_key = peewee.CompositeKey('from_owner_id', 'to_owner_id')

    def create_offer(self, from_owner_id, to_owner_id):
        try:
            new_rp_offer = self.create(from_owner_id=from_owner_id,
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


class AdditionalField(peewee.Model):
    title = peewee.CharField(default='Не указано')
    description = peewee.CharField(default='Не указано')

    class Meta:
        database = db

    def create_item(self):
        try:
            new_field = self.create()
            return new_field
        except Exception as error_message:
            logging.error(f'{error_message}')
            return False

    def get_item(self, field_id):
        try:
            field = self.get(self._schema.model.id == field_id)
            return field
        except self.DoesNotExist:
            return []

    def get_item_list(self):
        try:
            fields = self.select()
            return fields
        except self.DoesNotExist:
            return []

    def delete_item(self, field_id):
        try:
            deleteng_field = self.delete().where(self._schema.model.id == field_id)
            deleteng_field.execute()
            return True
        except self.DoesNotExist:
            return False


class ProfileAdditionalField(peewee.Model):
    profile_field = RpProfile
    additional_field = AdditionalField

    profile = peewee.ForeignKeyField(profile_field, on_delete='cascade')
    item = peewee.ForeignKeyField(additional_field, on_delete='cascade')
    is_allowed = peewee.BooleanField(default=True)

    class Meta:
        database = db
        primary_key = peewee.CompositeKey('profile', 'item')

    def add(self, profile_id, item_id):
        try:
            profile = self.profile_field().get_profile(profile_id)
            item = self.additional_field().get_item(item_id)
            added_item = self.create(profile=profile, item=item)
            return added_item
        except Exception as error_msg:
            logging.error(error_msg)
            return False

    def get_list(self, profile_id):
        try:
            item_list = self.select().join(self.additional_field).where(self._schema.model.profile_id == profile_id)
            return item_list
        except self.DoesNotExist:
            return []

    def delete_from_list(self, profile_id, item_id):
        try:
            delete_item = self.delete().where((self._schema.model.profile_id == profile_id) &
                                              (self._schema.model.item_id == item_id))
            delete_item.execute()
            return True
        except self.DoesNotExist:
            return False


class SettingList(AdditionalField):
    pass


class ProfileSettingList(ProfileAdditionalField):
    additional_field = SettingList
    item = peewee.ForeignKeyField(additional_field, on_delete='cascade')


class RpRating(AdditionalField):
    pass


class ProfileRpRatingList(ProfileAdditionalField):
    additional_field = RpRating
    item = peewee.ForeignKeyField(additional_field, on_delete='cascade')


class Gender(AdditionalField):
    pass


class ProfileGenderList(ProfileAdditionalField):
    additional_field = Gender
    item = peewee.ForeignKeyField(additional_field, on_delete='cascade')


class Species(AdditionalField):
    pass


class ProfileSpeciesList(ProfileAdditionalField):
    additional_field = Species
    item = peewee.ForeignKeyField(additional_field, on_delete='cascade')


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
    pass
    # TODO доделать поиск по остальным параметрам
    # try:
    #     user_profile = get_rp_profile(profile_id)
    #     setting_list = [i.setting_id for i in ProfileSettingList().get_list(profile_id) if i.is_allowed]
    #     suit_by_setting_ids = [i.profile_id for i in
    #                            ProfileSettingList.select().where((ProfileSettingList._id.in_(setting_list) &
    #                                                               ProfileSettingList.is_allowed))]
    #
    #     rating_list = [i.item_id for i in ProfileRpRatingList().get_item_list(profile_id) if i.is_allowed]
    #     suit_by_rating_ids = [i.profile_id for i in
    #                           ProfileRpRatingList.select().where((ProfileRpRatingList.item_id.in_(rating_list) &
    #                                                               ProfileRpRatingList.is_allowed))]
    #
    #     suit_prof_ids = list(set(suit_by_setting_ids + suit_by_rating_ids))
    #     suitable_profiles = RpProfile.select().where(RpProfile.id.in_(suit_prof_ids) &
    #                                                  (RpProfile.owner_id != user_profile.owner_id))
    #
    #     suitable_profiles_scores = [[profile, count_similarity_score(user_profile, profile)]
    #                                 for profile in set(suitable_profiles)]
    #     suitable_profiles_scores.sort(key=lambda x: x[1], reverse=True)
    #     suitable_profiles = [profile[0] for profile in suitable_profiles_scores]
    #     return suitable_profiles
    # except ProfileSettingList.DoesNotExist or RpProfile.DoesNotExist:
    #     return []


def init_db():
    User.create_table()
    RpProfile.create_table()
    RoleOffer.create_table()
    SettingList.create_table()
    ProfileSettingList.create_table()
    Notification.create_table()
    RpRating.create_table()
    ProfileRpRatingList.create_table()
    Gender.create_table()
    ProfileGenderList.create_table()
    Species.create_table()
    ProfileSpeciesList.create_table()


if __name__ == "__main__":
    # logging.basicConfig(format='%(filename)-15s[LINE:%(lineno)d]# %(levelname)-8s [%(asctime)s]  %(message)s',
    #                     level=logging.INFO)
    # TestField.create_table()
    # for i in range(2):
    #     af = TestField().create_field()
    #     af.title = f'test field {i}'
    #     af.save()
    # t_f = TestField().get_field_list()
    # for t in t_f:
    #     print(f'{t.id} - {t.title}')
    # t_id = int(input('delete id'))
    # print(TestField().delete_field(t_id))

    # import playhouse.migrate as playhouse_migrate
    # migrator = playhouse_migrate.SqliteMigrator(db)
    #
    # playhouse_migrate.migrate(
        # migrator.add_column('RoleOffer', 'is_actual', RoleOffer.is_actual),
        # migrator.rename_column('ProfileSettingList', 'setting_id', 'item_id'),
        # migrator.drop_column('story', 'some_old_field')
    # )
    pass
