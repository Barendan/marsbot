from kucoin.client import Market
# from pprint import pprint as pp
import pprint
import requests


# Spot and Margin REST API
client = Market(url='https://api.kucoin.com')
# Futures REST API
# client = Market(url='https://api-futures.kucoin.com')
# Sandbox REST API
# client = Market(url='https://api-sandbox-futures.kucoin.com')



# api_key = '<api_key>'
# api_secret = '<api_secret>'
# api_passphrase = '<api_passphrase>'


server_time = client.get_server_timestamp()


def get_contracts():
    coin_price = client.get_kline('BTC-USDT', '1min')
    print("price is:", coin_price)
    pprint.pprint(coin_price)
    print("End of get_contracts")


def get_contracts_request():
    response_object = requests.get('https://api.kucoin.com/api/v1/accounts?currency=BTC')
    print("res:", response_object)
    # pprint.pprint(response_object)

    pprint.pprint(response_object.json())


print("Time is:", server_time)
# get_contracts()
get_contracts_request()

