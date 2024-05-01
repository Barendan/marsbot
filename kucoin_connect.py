import requests
import time
import hashlib
import hmac
import base64
import json


class KucoinAPI:
    def __init__(self, api_key, api_secret, api_passphrase):
        self.api_key = api_key
        self.api_secret = api_secret
        self.api_passphrase = api_passphrase
        self.base_url = 'https://api.kucoin.com/api/v1'

    def generate_auth_headers(self, method, endpoint, data=None):
        timestamp = int(time.time() * 1000)

        prehash_string = f"{timestamp}{method}{endpoint}"

        if data is not None:
            prehash_string += json.dumps(data)

        signature = base64.b64encode(hmac.new(self.api_secret.encode('utf-8'), prehash_string.encode('utf-8'), hashlib.sha256).digest())

        headers = {
            'KC-API-SIGN': signature,
            'KC-API-KEY': self.api_key,
            'KC-API-TIMESTAMP': str(timestamp),
            'KC-API-PASSPHRASE': self.api_passphrase,
            'Content-Type': 'application/json'
        }

        # print("Head", prehash_string)

        return headers

    def get_accounts(self):
        endpoint = f'{self.base_url}/accounts'
        headers = self.generate_auth_headers('GET', '/api/v1/accounts')
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

    def get_coins(self, limit=20):
        endpoint = f'{self.base_url}/symbols?limit={limit}'

        response = requests.get(endpoint)

        if response.status_code == 200:
            data = response.json()
            symbols = [symbol['symbol'] for symbol in data['data']]

            return symbols
        else:
            print(f"Error: {response.status_code} - {response.text}")
            return None

    def get_coin(self, symbol):
        endpoint = f'{self.base_url}/market/orderbook/level1?symbol={symbol}'
        headers = self.generate_auth_headers('GET', f'/api/v1/market/orderbook/level1?symbol={symbol}')

        response = requests.get(endpoint, headers=headers)

        if response.status_code == 200:
            data = response.json()
            price = data['data']['price']

            return price
        else:
            print(f"Error: {response.status_code} - {response.text}")
            return None

    def get_historical_candles(self, params):
        endpoint = f'{self.base_url}/market/candles'

        response = requests.get(endpoint, params=params)

        print('some params', params)

        if response.status_code == 200:
            historical_candles = response.json()
            return historical_candles
        else:
            print(f"Error: {response.status_code} - {response.text}")
            return None

    def place_order(self, order_data):
        endpoint = f'{self.base_url}/orders'
        headers = self.generate_auth_headers('POST', '/api/v1/orders', order_data)

        response = requests.post(endpoint, json=order_data, headers=headers)

        if response.status_code == 200:
            order_status = response.json()
            print("Placed order:", order_status)
            return order_status
        else:
            print(f"Error: {response.status_code} - {response.text}")
            return None

    def cancel_order(self, order_id):
        endpoint = f'{self.base_url}/orders/{order_id}'
        headers = self.generate_auth_headers('DELETE', f'/api/v1/orders/{order_id}')

        response = requests.delete(endpoint, headers=headers)

        if response.status_code == 200:
            print("Order canceled successfully.")
            return True
        else:
            print(f"Error: {response.status_code} - {response.text}")
            return False

    def get_order_status(self, order_id):
        endpoint = f'{self.base_url}/orders/{order_id}'
        headers = self.generate_auth_headers('GET', f'/api/v1/orders/{order_id}')

        response = requests.get(endpoint, headers=headers)

        if response.status_code == 200:
            order_status = response.json()
            return order_status
        else:
            print(f"Error: {response.status_code} - {response.text}")
            return None