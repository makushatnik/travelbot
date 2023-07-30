from peewee import SqliteDatabase, Model, CharField, IntegerField, DecimalField,\
    ForeignKeyField, TextField, DateField, BooleanField

orm = SqliteDatabase("hotels.db")


def create_models():
    orm.create_tables(BaseModel.__subclasses__())


def get_region_id_by_city_name(name: str) -> int | None:
    city = City.get_or_none(City.name == name)
    if city:
        return city.region_id
    return None


class BaseModel(Model):
    class Meta:
        database = orm


class User(BaseModel):
    user_id = IntegerField(primary_key=True)
    first_name = CharField()
    last_name = CharField()
    username = CharField()
    banned = BooleanField(default=False)


class Hotel(BaseModel):
    hotels_com_id = IntegerField(null=False)
    name = CharField(null=False)
    region_id = IntegerField(null=False)
    distance = DecimalField(max_digits=8, decimal_places=2)
    price = DecimalField(max_digits=8, decimal_places=2)


class HotelImage(BaseModel):
    hotel = ForeignKeyField(Hotel, backref="images")
    url = TextField(null=False)


class City(BaseModel):
    name = CharField(null=False)
    query_name = CharField(null=False)
    region_id = IntegerField(null=False)


class History(BaseModel):
    user_id = ForeignKeyField(User, backref="requests")
    command = CharField(null=False)
    made_at = DateField()
