import random
from datetime import datetime

ADMIN_LOGIN = "admin"
ADMIN_SCORE = "42"

ONLINE_SCORE = "online_score"
CLIENTS_INTERESTS = "clients_interests"


class ValidationError(Exception):
    def __init__(self, message):
        self.message = message


class Field(object):
    def __init__(self, required=True, nullable=True):
        self.required = required
        self.nullable = nullable
        self.label = None

    def __get__(self, instance, owner):
        print '__get__. Label = %s' % self.label
        return instance.__dict__.get(self.label, None)

    def __set__(self, instance, value):
        print '__set__'
        if self.nullable is False and len(value) == 0:
            raise ValueError("{} field can't be empty".format(self.label))
        if len(value) != 0 and self.validation():
            instance.__dict__[self.label] = value

    #def __str__(self):
        #return "{}".format(self.field)


class CharField(Field):
    #attr = Field()
    pass


class CharField(Field):
    def __init__(self, chars):
        self.chars = chars.decode('utf-8')

    def __str__(self):
        return "{}".format(self.chars)


class ArgumentsField(Field):
    def __init__(self, args):
        self.args = args
        """for key in args:
            if not (isinstance(key, str) and isinstance(args.get(key), str)
                    or isinstance(args.get(key), int)):
                raise Exception("Oops..!Argument should be in line with json")"""


class PhoneField(Field):
    def __init__(self, international_code, phone_num):
        if international_code != "7":
            raise Exception("Oops..! International code in phone number must equal 7")
        if len(phone_num) != 11:
            raise Exception("Oops..! Length of phone number must equal 11")

        self.phone_num = phone_num

    def __repr__(self):
        return "{}".format(self.phone_num)


class EmailField(CharField):
    def __set__(self, instance, email):
        super(EmailField, self).__init__(email)
        if '@' not in email:
            raise ValidationError("Oops..! Email must contain the @ character")
        self.email = email


class BirthDayField(Field):
    def __set__(self, instance, birthday):
        self.birthday = datetime.strptime(birthday, "%d.%m.%Y")

        if datetime.now().year - self.birthday.year > 70:
            raise ValidationError("Oops..! The age should not exceed 70")


class GenderField(Field):
    def __set__(self, instance, gender):
        if gender not in (0, 1, 2):
            raise ValidationError("Oops..! Error in gender")

        self.gender = gender


class DateField(Field):
    def __set__(self, instance, date):
        self.birthday = datetime.strptime(date, "%d.%m.%Y")


class ClientIDsField(Field):
    def __set__(self, instance, clients_ids):
        if not isinstance(clients_ids, list):
            raise ValidationError("Oops! Clients ids need to be in array")
        for item in clients_ids:
            if not isinstance(item, int):
                raise ValidationError("Oops! Clients ids should be integer")
        self.clients_ids = clients_ids
        self.offset = 0

    def next(self):
        if self.offset >= len(self.clients_ids):
            raise StopIteration
        else:
            item = self.clients_ids[self.offset]
            self.offset += 1
            return item

    def __iter__(self):
        return self


class DeclarativeRequestsMetaclass(type):
    account = CharField(required=False, nullable=True)
    login = CharField(required=True, nullable=True)
    token = CharField(required=True, nullable=True)
    arguments = ArgumentsField(required=True, nullable=True)
    method = CharField(required=True, nullable=False)

    first_name = CharField(required=False, nullable=True)
    last_name = CharField(required=False, nullable=True)
    email = EmailField(required=False, nullable=True)
    phone = PhoneField(required=False, nullable=True)
    birthday = BirthDayField(required=False, nullable=True)
    gender = GenderField(required=False, nullable=True)

    client_ids = ClientIDsField(required=True)
    date = DateField(required=False, nullable=True)


    def __new__(cls, name, bases, attribute_dict):
        declared_fields = []
        # find all requests, auto-set their labels
        for key, value in attribute_dict.items():
            if isinstance(value, Field):
                declared_fields.append((key, value))
                value.label = key
        new_class = super(DeclarativeRequestsMetaclass, cls).__new__(cls, attribute_dict)
        new_class.declared_fields = declared_fields
        return new_class


    def __init__(cls, name, bases, attributedict):
        #global declared_fields
        for key, value in attributedict.items():
            if (key, value) in declared_fields:
                key = Field(value)


class BaseRequest(object):
    _metaclass__ = DeclarativeRequestsMetaclass

    def __init__(self, data=None):
        self.data = data or {}
        self.errors = {}

        for name in self.declared_fields:
            value = self.data.get(name)
        try:
            setattr(self, name, value)
        except ValidationError as e:
            self.errors.update({name: e.message})

    def is_valid(self):
        return not self.errors


class MethodRequest(BaseRequest):

    account = CharField(required=False, nullable=True)
    login = CharField(required=True, nullable=True)
    token = CharField(required=True, nullable=True)
    arguments = ArgumentsField(required=True, nullable=True)
    method = CharField(required=True, nullable=False)

    @property
    def is_admin(self):
        return self.login == ADMIN_LOGIN

    @property
    def is_online_score(self):
        return self.method == ONLINE_SCORE

    @property
    def is_clients_interests(self):
        return self.method == CLIENTS_INTERESTS


class OnlineScoreRequest(BaseRequest):
    first_name = CharField(required=False, nullable=True)
    last_name = CharField(required=False, nullable=True)
    email = EmailField(required=False, nullable=True)
    phone = PhoneField(required=False, nullable=True)
    birthday = BirthDayField(required=False, nullable=True)
    gender = GenderField(required=False, nullable=True)


class ClientsInterestsRequest(BaseRequest):
    client_ids = ClientIDsField(required=True)
    date = DateField(required=False, nullable=True)


class OnlineScoreResponse(object):
    def __init__(self, score):
        self.score = score

    def __str__(self):
        return self.score


def get_score(phone, email, birthday, gender, first_name, last_name):
    if first_name == ADMIN_LOGIN:
        return ADMIN_SCORE
    score = 0
    if phone:
        score += 1.5
    if email:
        score += 1.5
    if birthday and gender:
        score += 1.5
    if first_name and last_name:
        score += 0.5
    return score


def get_interests(cid):
    interests = ["cars", "pets", "travel", "hi-tech", "sport", "music", "books", "tv", "cinema", "geek", "otus"]
    return random.sample(interests, 2)


def count_score(req):
    score = get_score(req.phone, req.email, req.birthday, req.gender, req.first_name, req.last_name)
    c = OnlineScoreResponse(score)
    return c


def count_interests(req):
    interests_response = dict()
    for cid in req.client_ids:
        interests_response[cid] = get_interests(cid)
    return interests_response
