import random
from datetime import datetime

ADMIN_LOGIN = "admin"
ADMIN_SCORE = "42"

ONLINE_SCORE = "online_score"
CLIENTS_INTERESTS = "clients_interests"


class CharField(object):
    def __init__(self, chars):
        self.chars = chars

    def __str__(self):
        return "{}".format(self.chars)


class ArgumentsField(object):
    def __init__(self, args):
        self.args = args
        """for key in args:
            if not (isinstance(key, str) and isinstance(args.get(key), str)
                    or isinstance(args.get(key), int)):
                raise Exception("Oops..!Argument should be in line with json")"""


class PhoneField(object):
    def __init__(self, international_code, phone_num):
        if international_code != "7":
            raise Exception("Oops..! International code in phone number must equal 7")
        if len(phone_num) != 11:
            raise Exception("Oops..! Length of phone number must equal 11")

        self.international_code = international_code
        self.phone_num = phone_num


class EmailField(CharField):
    def __init__(self, email):
        super(EmailField, self).__init__(email)
        if '@' not in email:
            raise Exception("Oops..! Email must contain the @ character")


class BirthDayField(object):
    def __init__(self, birthday):
        self.birthday = datetime.strptime(birthday, "%d%m%Y")

        if datetime.now().year - self.birthday.year > 70:
            raise Exception("Oops..! The age should not exceed 70")


class GenderField(object):
    def __init__(self, gender):
        if gender not in (0, 1, 2):
            raise Exception("Oops..! Error in gender")


class OnlineScoreRequest(object):
    def __init__(self, phone, email, first_name, last_name, birthday, gender):
        if phone is None:
            self.phone = ''
        else:
            self.phone = PhoneField(phone[0], phone)
        if email is None:
            self.email = ''
        else:
            self.email = EmailField(email)
        if first_name is None:
            self.first_name = ''
        else:
            self.first_name = CharField(first_name)
        if last_name is None:
            self.last_name = ''
        else:
            self.last_name = CharField(last_name)
        if birthday is None:
            self.birthday = ''
        else:
            self.birthday = BirthDayField(birthday.replace(".", ''))
        if gender is None:
            self.gender = ''
        else:
            self.gender = GenderField(gender)


class MethodRequest(object):
    def __init__(self, account, login, token, arguments, method):
        if account is None:
            self.account = ''
        else:
            self.account = CharField(account)
        if login is None:
            raise Exception("Please, fill up the login field")
        else:
            self.login = CharField(login)
        if token is None:
            raise Exception("Please, fill up the token field")
        else:
            self.token = CharField(token)
        if method is None:
            raise Exception("Please, fill up the method field")
        else:
            self.method = CharField(method)
        if arguments is None:
            raise Exception("Please, fill up the fields of arguments")
        else:
            self.arguments = ArgumentsField(arguments)

    @property
    def is_online_score(self):
        return self.method == ONLINE_SCORE

    @property
    def is_clients_interests(self):
        return self.method == CLIENTS_INTERESTS

    @property
    def is_admin(self):
        return self.login == ADMIN_LOGIN


class DateField(object):
    def __init__(self, date):
        self.birthday = datetime.strptime(date, "%d%m%Y")


class ClientIDsField(object):
    def __init__(self, clients_ids):
        for item in clients_ids:
            if not isinstance(item, int):
                raise Exception("Oops! Clients ids should be integer")
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


class ClientsInterestsRequest(object):
    def __init__(self, client_ids, date):
        if client_ids is None:
            raise Exception("Please, fill up the clients_ids field")
        else:
            self.client_ids = ClientIDsField(client_ids)
        if date is None:
            self.date = ''
        else:
            self.date = DateField(date.replace(".", ''))


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
