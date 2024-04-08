from enum import Enum


class HTTPMethods(str, Enum):
    '''Available HTTP methods.'''

    POST = 'POST'
    GET = 'GET'


class Currencies(str, Enum):
    RUB = 'RUB'
    UAH = 'UAH'
    USD = 'USD'
    EUR = 'EUR'
    RUB2 = 'RUB2'
