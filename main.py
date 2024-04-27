from config import API_KEY, API_SECRET, API_PASSPHRASE
from kucoin_connect import get_accounts, get_coin, get_coins

from pprint import pprint


def get_contracts():
    accounts = get_accounts(API_KEY, API_SECRET, API_PASSPHRASE)
    print("Res:", accounts)
    print("Done Nice")
    pprint(accounts)


# get_contracts()
symbol = 'BTC-USDT'


def get_price():
    price = get_coin(API_KEY, API_SECRET, API_PASSPHRASE, symbol)
    if price is not None:
        print(f"The current price of {symbol} is {price}")


# get_price()


def get_all():
    coins = get_coins()
    # print("all the coins:", coins)
    pprint(coins)
    print("all the coins:", len(coins))


get_all()



