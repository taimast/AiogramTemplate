# -*- coding: utf-8 -*-

__all__ = [
    "getBalance",
    "getTransaction",
    "getPayout",
    "createPayout",
    "createPay"
]
__version__ = "0.1"
__author__ = "except - lolz.guru/members/2977610"

import hashlib
import urllib.parse

import requests


def getBalance(
        API_ID: int,
        API_KEY: str
) -> dict[float, float]:
    """
    Args:
        API_ID (int): ID вашего ключа API
        API_KEY (str): Ваш ключ API

    Answer (dict):
        balance (str(float)): Основной баланс кошелька.
        ref_balance (str(float)): Реферальный баланс кошелька.

    Example answer:
        {
            "balance":"339.44",
            "ref_balance":"6063.60"
        }
    Raises:
        Exception

    Returns:
        dict

    Doc:
        https://payok.io/cabinet/documentation/doc_api_balance
    """
    url = "https://payok.io/api/balance"
    data = {
        "API_ID": API_ID,
        "API_KEY": API_KEY
    }
    response = requests.post(
        url,
        data
    ).json()

    try:
        result = {
            "balance": float(response["balance"]),
            "ref_balance": float(response["ref_balance"]),
        }
        return result
    except:
        raise Exception(
            response
        )


def getTransaction(
        API_ID: int,
        API_KEY: str,
        shop: int,
        payment=None,
        offset: int = None
) -> dict:
    """
    Args:
        API_ID (int): ID вашего ключа API
        API_KEY (str): Ваш ключ API
        shop (int): ID магазина
        payment (optional): ID платежа в вашей системе
        offset (int, optional): Отступ, пропуск указанного количества строк

    Raises:
        Exception

    Returns:
        dict

    Doс and answer:
        https://payok.io/cabinet/documentation/doc_api_transaction
    """
    url = "https://payok.io/api/transaction"
    data = {
        "API_ID": API_ID,
        "API_KEY": API_KEY,
        "shop": shop,
        "payment": payment,
        "offset": offset
    }
    response = requests.post(
        url,
        data
    ).json()
    if response["status"] == "success":
        return response
    else:
        raise Exception(
            response
        )


def getPayout(
        API_ID: int,
        API_KEY: str,
        payout_id: int = None,
        offset: int = None
) -> dict:
    """
    Args:
        API_ID (int): ID вашего ключа API
        API_KEY (str): Ваш ключ API
        payout_id (int, optional): 	ID выплаты в системе Payok
        offset (int, optional): Отступ, пропуск указанного количества строк

    Raises:
        Exception

    Returns:
        dict

    Doc:
        https://payok.io/cabinet/documentation/doc_api_payout
    """
    url = "https://payok.io/api/payout"
    data = {
        "API_ID": API_ID,
        "API_KEY": API_KEY,
        "payout_id": payout_id,
        "offset": offset
    }
    response = requests.post(
        url,
        data
    ).json()
    if response["status"] == "success":
        return response
    else:
        raise Exception(
            response
        )


def createPayout(
        API_ID: int,
        API_KEY: str,
        amount: float,
        method: str,
        reciever: str,
        comission_type: str,
        webhook_url: str = None
) -> dict:
    """
    Args:
        API_ID (int): ID вашего ключа API
        API_KEY (str): Ваш ключ API
        amount (float): Сумма выплаты
        method (str): Специальное значение метода выплаты, список значений
        reciever (str): Реквизиты получателя выплаты
        comission_type (str): Тип расчета комиссии: balance - Комиссия с баланса; payment - Комиссия с платежа
        webhook_url (str, optional): URL для отправки Webhook при смене статуса выплаты. Defaults to None.

    Raises:
        Exception

    Returns:
        dict
    Doc:
        https://payok.io/cabinet/documentation/doc_api_payout_create
    """
    url = "https://payok.io/api/payout_create"
    data = {
        "API_ID": API_ID,
        "API_KEY": API_KEY,
        "amount": amount,
        "method": method,
        "reciever": reciever,
        "comission_type": comission_type,
        "webhook_url": webhook_url
    }
    response = requests.post(
        url,
        data
    ).json()
    if response["status"] == "success":
        return response
    else:
        raise Exception(
            response
        )


def createPay(
        secret: str,
        amount: float,
        payment: str,
        shop: int,
        desc: str,
        currency: str = "RUB",
        email: str = None,
        success_url: str = None,
        method: str = None,
        lang: str = None,
        custom=None,
) -> str:
    """
    Args:
        secret (str): SECRET KEY (Узнайте свой секретный ключ в личном кабинете)
        amount (float): Сумма заказа.
        payment (str): Номер заказа, уникальный в вашей системе, до 16 символов. (a-z0-9-_)
        shop (int): ID вашего магазина.
        desc (str): Название или описание товара.
        currency (str, optional): Валюта по стандарту ISO 4217. По умолчанию "RUB".
        email (str, optional): Эл. Почта покупателя. Defaults to None.
        success_url (str, optional): Ссылка для переадресации после оплаты, подробнее (https://payok.io/cabinet/documentation/doc_redirect.php). Defaults to None.
        method (str, optional): Способ оплаты (Cписок названий методов: https://payok.io/cabinet/documentation/doc_methods.php). Defaults to None.
        lang (str, optional): Язык интерфейса. RU или EN (Если не указан, берется язык браузера). Defaults to None.
        custom (_type_, optional): Ваш параметр, который вы хотите передать в уведомлении. Defaults to None.

    Returns:
        str: url
    """
    data = [
        amount,
        payment,
        shop,
        currency,
        desc,
        secret
    ]
    sign = hashlib.md5(
        "|".join(
            map(
                str,
                data
            )
        ).encode("utf-8")
    ).hexdigest()
    desc = urllib.parse.quote_plus(desc)
    success_url = urllib.parse.quote_plus(success_url)
    lang = urllib.parse.quote_plus(lang)
    url = f"https://payok.io/pay?amount={amount}&payment={payment}&desc={desc}&shop={shop}&sign={sign}&email={email}&success_url=&method={method}&customparam={custom}"
    return url
