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
    search_preset = peewee.BooleanField(default=False)
    owner_id = peewee.IntegerField()
    name = peewee.CharField(default='Не указано')
    description = peewee.CharField(default='')
    arts = peewee.CharField(default='[]')

    class Meta:
        database = db

    def get_profile(self, profile_id):
        try:
            rp_profile = self.get(self._schema.model.id == profile_id)
            return rp_profile
        except self.DoesNotExist:
            return False

    def get_user_profiles(self, owner_id, search_preset=False):
        try:
            profiles = self.select().where((self._schema.model.owner_id == owner_id) &
                                           (self._schema.model.search_preset == search_preset))
            return profiles
        except self.DoesNotExist:
            return []

    def create_profile(self, user_id, search_preset=False):
        new_rp_profile = self.create(owner_id=user_id, search_preset=search_preset)
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

    def create_offer(self, from_owner_id, to_profile_id):
        try:
            to_owner_id = RpProfile().get_profile(to_profile_id).owner_id
            new_rp_offer = self.create(from_owner_id=from_owner_id,
                                       to_owner_id=to_owner_id)
            return new_rp_offer
        except:
            return False

    def get_offers_from_user(self, user_id):
        try:
            user_offers = self.select().where(self._schema.model.from_owner_id == user_id)
            return user_offers
        except self.DoesNotExist:
            return []

    def get_offers_to_user(self, user_id):
        try:
            user_offers = self.select().where(self._schema.model.to_owner_id == user_id)
            return user_offers
        except self.DoesNotExist:
            return []

    def get_offer_to_profile(self, from_user_id, profile_id):
        try:
            to_user_id = RpProfile().get_profile(profile_id).owner_id
            user_offers = self.get((self._schema.model.from_owner_id == from_user_id) &
                                   (self._schema.model.to_owner_id == to_user_id))
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


def count_similarity_score(parameter_list, user_pr_id, player_pr_id):
    score = 0
    for parameter in parameter_list:
        user_items_ids = parameter.select(parameter.item_id).where((parameter.profile_id == user_pr_id))
        score += parameter.select()\
            .where((parameter.profile_id == player_pr_id) &
                   parameter.item_id.in_(user_items_ids) &
                   parameter.is_allowed).count()
    return score


def get_unsuit_profiles(profile_id, parameter):
    # получаем id полей, которые пользователь исключил из поиска
    not_allowed_items = parameter.select(parameter.item_id) \
        .where((parameter.profile_id == profile_id) & ~parameter.is_allowed).distinct()

    # получаем id анкет, которые содержат недопустимые поля
    unsuit_profiles = parameter.select(parameter.profile_id) \
        .where(parameter.item_id.in_(not_allowed_items) & parameter.is_allowed).distinct()
    return unsuit_profiles


def get_suit_profiles(profile_id, parameter, unsuit_profiles):
    # получаем id полей, которые пользователь выбрал для поиска
    allowed_items = parameter.select(parameter.item_id) \
        .where((parameter.profile == profile_id) & parameter.is_allowed)

    # получаем id анкет, которые содержат необходимые поля
    suit_profiles = parameter.select(parameter.profile_id) \
        .where(parameter.item_id.in_(allowed_items) &
               parameter.is_allowed &
               parameter.profile_id.not_in(unsuit_profiles)).distinct()
    return suit_profiles


def suit_by_parameters(profile_id, parameter_list):
    try:
        unsuit_profiles = get_unsuit_profiles(profile_id, parameter_list[0])
        for parameter in parameter_list[1:]:
            unsuit_profiles += get_unsuit_profiles(profile_id, parameter)

        suit_profiles = get_suit_profiles(profile_id, parameter_list[0], unsuit_profiles)
        for parameter in parameter_list[1:]:
            suit_profiles += get_suit_profiles(profile_id, parameter, unsuit_profiles)

        # получаем анкеты, которые содержат необходимые поля
        user_id = RpProfile().get_profile(profile_id).owner_id

        profile_field = parameter_list[0].profile_field
        profiles_list = profile_field\
            .select()\
            .where(profile_field.id.in_(suit_profiles)
                   & ~profile_field.search_preset
                   & (profile_field.owner_id != user_id))\
            .distinct()
        # print('profiles_list.sql()', profiles_list.sql())
        return list(profiles_list)
    except tuple(parameter.DoesNotExist for parameter in parameter_list):
        return []


def find_suitable_profiles(profile_id):
    parameters = (
        ProfileGenderList,
        ProfileSettingList,
        ProfileSpeciesList,
        ProfileRpRatingList
    )

    suit_profiles = suit_by_parameters(profile_id, parameters)

    suit_profiles_score = [{'profile': i,
                            'score': count_similarity_score(parameters, profile_id, i.id)}
                           for i in suit_profiles]

    suit_profiles_score.sort(key=lambda x: x['score'], reverse=True)
    suit_profiles_sorted = [i['profile'] for i in suit_profiles_score]

    return suit_profiles_sorted


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

    import playhouse.migrate as playhouse_migrate
    migrator = playhouse_migrate.SqliteMigrator(db)

    playhouse_migrate.migrate(
        # migrator.add_column('RpProfile', 'search_preset', RpProfile.search_preset),
        # migrator.rename_column('ProfileSettingList', 'item_id', 'item'),
        # migrator.drop_column('RoleOffer', 'to_profile_id')
    )
    pass
