import requests
import time
import hashlib
import hmac
import base64



def generate_auth_headers(api_key, api_secret, api_passphrase, method, endpoint):
    timestamp = int(time.time() * 1000)

    # Create prehash string
    prehash_string = f"{timestamp}{method}{endpoint}"
    # Generate signature
    signature = base64.b64encode(hmac.new(api_secret.encode(), prehash_string.encode(), hashlib.sha256).digest())

    headers = {
        'KC-API-KEY': api_key,
        'KC-API-SIGN': signature.decode(),
        'KC-API-TIMESTAMP': str(timestamp),
        'KC-API-PASSPHRASE': api_passphrase,
        'Content-Type': 'application/json'
    }

    return headers


def get_accounts(api_key, api_secret, api_passphrase):
    endpoint = 'https://api.kucoin.com/api/v1/accounts'
    headers = generate_auth_headers(api_key, api_secret, api_passphrase, 'GET', '/api/v1/accounts')

    balances = {}
    encountered_currencies = set()

    response = requests.get(endpoint, headers=headers)
    account_data = response.json()

    if account_data is not None:
        for a in account_data["data"]:
            if a['currency'] not in encountered_currencies:
                balances[a['currency']] = a['balance']
                encountered_currencies.add(a['currency'])

    return balances


def get_coins(limit=20):
    endpoint = f'https://api.kucoin.com/api/v1/symbols?limit={limit}'

    response = requests.get(endpoint)

    if response.status_code == 200:
        data = response.json()
        symbols = [symbol['symbol'] for symbol in data['data']]

        return symbols
    else:
        print(f"Error: {response.status_code} - {response.text}")
        return None


def get_coin(api_key, api_secret, api_passphrase, symbol):
    endpoint = f'https://api.kucoin.com/api/v1/market/orderbook/level1?symbol={symbol}'
    headers = generate_auth_headers(api_key, api_secret, api_passphrase, 'GET',f'/api/v1/market/orderbook/level1?symbol={symbol}')

    response = requests.get(endpoint, headers=headers)

    if response.status_code == 200:
        data = response.json()

        # print("Magnify:", data['data'])
        # print("More:", data)

        price = data['data']['price']

        return price
    else:
        print(f"Error: {response.status_code} - {response.text}")
        return None


def place_order():
    return


def cancel_order():
    return


def get_order_status():
    return