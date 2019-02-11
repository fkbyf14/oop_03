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
        # print '__get__. Label = %s' % self.label
        return instance.__dict__.get(self.label, None)

    def __set__(self, instance, value):
        # print '__set__'
        # print "value is:", value, "label is:", self.label, self.required, self.nullable

        if value is None and self.required:
            raise ValidationError("\'{}\' is required field".format(self.label))
        if not value and not self.nullable:
            raise ValidationError("\'{}\'-field can't be empty".format(self.label))
        if value is not None and self.validation(value):
            instance.__dict__[self.label] = value

    def __str__(self):
        return "{}".format(self.label)


class CharField(Field):
    def __init__(self, required, nullable):
        super(CharField, self).__init__(required, nullable)

    def validation(self, value):
        if self.label == "first_name" or self.label == "last_name":
            for ch in value:
                if not ch.isalpha():
                    raise ValidationError("Name should consist of letters")
        return True


class ArgumentsField(Field):
    def __init__(self, required, nullable):
        super(ArgumentsField, self).__init__(required, nullable)

    def validation(self, args):
        """
        try:
            for key in args:

                if not isinstance(key, str) or not (isinstance(args.get(key), str)
                                                    or isinstance(args.get(key), int) or isinstance(args.get(key),
                                                                                                    dict)):
                    raise ValidationError
                return True
        except Exception:
            raise ValidationError("Oops..!Argument should be in line with json")
"""
        return True

class PhoneField(Field):
    def __init__(self, required, nullable):
        super(PhoneField, self).__init__(required, nullable)

    def validation(self, value):
        value = str(value)
        if value[0] != "7":
            raise ValidationError("Oops..! International code in phone number must equal 7")
        if len(value) != 11:
            raise ValidationError("Oops..! Length of phone number must equal 11")
        return True


class EmailField(CharField):
    def __init__(self, required, nullable):
        super(EmailField, self).__init__(required, nullable)

    def validation(self, value):
        if '@' not in value:
            raise ValidationError("Oops..! Email must contain the @ character")
        return True


class BirthDayField(Field):
    def __init__(self, required, nullable):
        super(BirthDayField, self).__init__(required, nullable)

    def validation(self, value):
        delta = datetime.now() - datetime.strptime(value, "%d.%m.%Y")
        if delta.days > 365 * 70:
            raise ValidationError("Oops..! The age should not exceed 70")
        return True


class GenderField(Field):
    def __init__(self, required, nullable):
        super(GenderField, self).__init__(required, nullable)

    def validation(self, value):
        if value not in (0, 1, 2):
            raise ValidationError("Oops..! Error in gender")
        return True


class DateField(Field):
    def __init__(self, required, nullable):
        super(DateField, self).__init__(required, nullable)

    def validation(self, value):
        datetime.strptime(value, "%d.%m.%Y")
        return True


class ClientIDsField(Field):
    def __init__(self, required, nullable):
        super(ClientIDsField, self).__init__(required, nullable)
        self.offset = 0

    def next(self, value):
        if self.offset >= len(value):
            raise StopIteration
        else:
            item = value[self.offset]
            self.offset += 1
            return item

    def __iter__(self):
        return self

    def validation(self, value):
        if not isinstance(value, list):
            raise ValidationError("Oops! Clients ids need to be in array")
        for item in value:
            if not isinstance(item, int):
                raise ValidationError("Oops! Clients ids should be integer")
        return True


class DeclarativeRequestsMetaclass(type):
    def __new__(mcs, name, bases, attribute_dict):
        declared_fields = []
        # find all requests, auto-set their labels
        for key, value in attribute_dict.items():
            if isinstance(value, Field):
                declared_fields.append((key, value))
                value.label = key
        new_class = super(DeclarativeRequestsMetaclass, mcs).__new__(mcs, name, bases, attribute_dict)
        new_class.declared_fields = declared_fields

        return new_class


class BaseRequest(object):
    __metaclass__ = DeclarativeRequestsMetaclass

    def __init__(self, data=None):
        self.data = data or {}
        self.errors = {}
        # print "data is", data
        # print "self.declared_f", self.declared_fields
        for name, _ in self.declared_fields:
            # print name
            value = self.data.get(name)
            # print "value is", value
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

    def __init__(self, data):
        super(MethodRequest, self).__init__(data)

    @property
    def is_admin(self):
        return self.login == ADMIN_LOGIN

    @property
    def is_online_score(self):
        return self.method == ONLINE_SCORE

    @property
    def is_clients_interests(self):
        return self.method == CLIENTS_INTERESTS


method_req = {"login": "admin", "token": "toktok", "arguments": {"gender": 0, "birthday": "01.01.2000"},
              "method": "clients_interests"}
m = MethodRequest(method_req)
print m.errors
# print "data is", m.data
# print "__dict__ iiiis", m.__dict__
# print "method is", m.method, type(m.method)
# if m.is_admin:
#    print "Truuuue"
# else:
#    print "Falseee"
# print m.data
# print "m.ERRORS is:", m.errors


class OnlineScoreRequest(BaseRequest):
    first_name = CharField(required=False, nullable=True)
    last_name = CharField(required=False, nullable=True)
    email = EmailField(required=False, nullable=True)
    phone = PhoneField(required=False, nullable=True)
    birthday = BirthDayField(required=False, nullable=True)
    gender = GenderField(required=False, nullable=True)

    def __init__(self, data):
        super(OnlineScoreRequest, self).__init__(data)

        pair_1 = data.get("first_name") and data.get("last_name")
        pair_2 = data.get("phone") and data.get("email")
        pair_3 = data.get("gender") and data.get("birthday")
        if not pair_1 or not pair_2 or not pair_3:
            raise ValidationError("Request to get_score should consist of pair values")


# on_req = {"first_name": "aly", "last_name": "lolovich", "email": "i@lol",
#         "phone": 79523939611, "birthday": "11.12.1970", "gender": 1}
# on = OnlineScoreRequest(on_req)
# print on.data


class ClientsInterestsRequest(BaseRequest):
    client_ids = ClientIDsField(required=True, nullable=False)
    date = DateField(required=False, nullable=True)

    def __init__(self, data):
        super(ClientsInterestsRequest, self).__init__(data)


# clients_req = {"client_ids": (1, 2, 3, 4)}
# cl = ClientsInterestsRequest(clients_req)
# print cl.errors


class OnlineScoreResponse(object):
    def __init__(self, score):
        self.score = score

    def __str__(self):
        return self.score


def get_score(arg):
    phone = arg.get("phone")
    email = arg.get("email")
    first_name = arg.get("first_name")
    last_name = arg.get("last_name")
    birthday = arg.get("birthday")
    gender = arg.get("gender")

    # if arg.get("birthday"):
    #    birthday = BirthDayField(birthday).birthday
    # if first_name == ADMIN_LOGIN:
    #    return ADMIN_SCORE
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
    for cid in req.get("client_ids"):
        interests_response[cid] = get_interests(cid)
    return interests_response
