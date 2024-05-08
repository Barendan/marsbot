import logging
import time
import typing
import requests
import json

import hashlib
import hmac
import base64

import websocket
import threading

logger = logging.getLogger()


class KucoinAPI:
    def __init__(self, api_key: str, api_secret: str, api_passphrase: str):
        # self.base_url = 'https://api.kucoin.com/api/v1'
        self.base_url = 'https://api.kucoin.com'
        self.wss_url = 'wss://ws-api.kucoin.com/'
        self.api_key = api_key
        self.api_secret = api_secret
        self.api_passphrase = api_passphrase
        self.wss_public_token = '2neAiuYvAU61ZDXANAGAsiL4-iAExhsBXZxftpOeh_55i3Ysy2q2LEsEWU64mdzUOPusi34M_wGoSf7iNyEWJ14XEUPABGItB5NlghIT8Zl40HBGTta4otiYB9J6i9GjsxUuhPw3BlrzazF6ghq4L8B2G_md6Wmm6cIXiO17Mdo=._FmNwy4ke3ZtOo_RJLQULg=='

        self._ws = None

        self.prices = dict()

        self.logs = []

        # self._start_ws()

        # t = threading.Thread(target=self._start_ws)
        # t.start()

        logger.info("Kucoin Client successfully initialized")

    def add_log(self, msg: str):
        logger.info("%s", msg)
        self.logs.append({"log": msg, "displayed": False })

    def _generate_signature(self, method: str, endpoint: str, timestamp: str, data: typing.Dict) -> bytes:
        prehash_string = f"{timestamp}{method}{endpoint}"

        if len(data) > 0:
            prehash_string += json.dumps(data)

        print('Hash', prehash_string)

        return base64.b64encode(hmac.new(self.api_secret.encode('utf-8'), prehash_string.encode(), hashlib.sha256).digest())

    def _make_request(self, method: str, endpoint: str, data: typing.Dict):
        headers = dict()
        timestamp = str(int(time.time() * 1000))
        headers['KC-API-SIGN'] = self._generate_signature(method, endpoint, timestamp, data)
        headers['KC-API-KEY'] = self.api_key
        headers['KC-API-TIMESTAMP'] = timestamp
        headers['KC-API-PASSPHRASE'] = self.api_passphrase

        # print('show me the request:', self.base_url + endpoint, data)

        if method == "GET":
            try:
                response = requests.get(self.base_url + endpoint, params=data, headers=headers)
            except Exception as e:
                logger.error("Connection error while making %s request to %s: %s", method, endpoint, e)
                return None

        elif method == "POST":
            try:
                response = requests.post(self.base_url + endpoint, params=data, headers=headers)
            except Exception as e:
                logger.error("Connection error while making %s request to %s: %s", method, endpoint, e)
                return None

        elif method == "DELETE":
            try:
                response = requests.delete(self.base_url + endpoint, params=data, headers=headers)
            except Exception as e:
                logger.error("Connection error while making %s request to %s: %s", method, endpoint, e)
                return None
        else:
            raise ValueError()

        if response.status_code == 200:
            return response.json()
        else:
            logger.error("Error while making %s request to %s: %s (error code %s)",
                         method, endpoint, response.json(), response.status_code)
            return None

    def get_accounts(self):
        endpoint = '/api/v1/accounts'
        data = dict()
        balances = {}
        encountered_currencies = set()

        account_data = self._make_request("GET", endpoint, data)

        # print("account data:", account_data)

        if account_data is not None:
            for a in account_data["data"]:
                if a['currency'] not in encountered_currencies:
                    balances[a['currency']] = a['balance']
                    encountered_currencies.add(a['currency'])

        return balances

    def get_coins(self, limit=20):
        endpoint = f'/api/v1/symbols?limit={limit}'
        data = dict()

        all_coins = self._make_request("GET", endpoint, data)

        if len(all_coins) > 0:
            symbols = [symbol['symbol'] for symbol in all_coins['data']]
            return symbols
        else:
            return None

    def get_coin(self, data):
        endpoint = f'/api/v1/market/orderbook/level1?symbol={data}'

        coin = self._make_request("GET", endpoint, data)

        if len(coin) > 0:
            price = coin['data']['price']
            return price
        else:
            return None

    def get_historical_candles(self, params):
        endpoint = f'/api/v1/market/candles'

        candles = self._make_request("GET", endpoint, data=params)

        if len(candles) > 0:
            return candles['data']
        else:
            return None

    def generate_auth_headers(self, method, endpoint, data=None):
        timestamp = int(time.time() * 1000)

        prehash_string = f"{timestamp}{method}{endpoint}"

        if data is not None:
            prehash_string += json.dumps(data)

        print('Proper string', prehash_string)

        signature = base64.b64encode(
            hmac.new(self.api_secret.encode('utf-8'), prehash_string.encode('utf-8'), hashlib.sha256).digest())

        headers = {
            'KC-API-SIGN': signature,
            'KC-API-KEY': self.api_key,
            'KC-API-TIMESTAMP': str(timestamp),
            'KC-API-PASSPHRASE': self.api_passphrase,
            'Content-Type': 'application/json'
        }

        return headers

    # def place_order(self, order_data):
    #     endpoint = f'{self.base_url}/api/v1/orders'
    #     headers = self.generate_auth_headers('POST', '/api/v1/orders', order_data)
    #
    #     response = requests.post(endpoint, json=order_data, headers=headers)
    #
    #     if response.status_code == 200:
    #         order_status = response.json()
    #         print("Placed order:", order_status)
    #         return order_status
    #     else:
    #         print(f"Error: {response.status_code} - {response.text}")
    #         return None



    def place_order(self, order_data):
        endpoint = f'/api/v1/orders'
        # headers = self.generate_auth_headers('POST', '/api/v1/orders', data=order_data)

        order_placed = self._make_request("POST", endpoint, data=order_data)

        print("PLaced:", order_placed)
        # response = requests.post(endpoint, json=order_data, headers=headers)

        # if len(order_placed) > 0:
        #     print("Placed order:", order_placed)
        #     return order_placed
        # else:
        #     return None





    def cancel_order(self, order_id):
        endpoint = f'/api/v1/orders/{order_id}'
        headers = self.generate_auth_headers('DELETE', f'/api/v1/orders/{order_id}')

        response = requests.delete(endpoint, headers=headers)

        if response.status_code == 200:
            print("Order canceled successfully.")
            return True
        else:
            print(f"Error: {response.status_code} - {response.text}")
            return False

    def get_order_status(self, order_id):
        endpoint = f'/api/v1/orders/{order_id}'
        headers = self.generate_auth_headers('GET', f'/api/v1/orders/{order_id}')

        response = requests.get(endpoint, headers=headers)

        if response.status_code == 200:
            order_status = response.json()
            return order_status
        else:
            print(f"Error: {response.status_code} - {response.text}")
            return None

    def _start_ws(self):
        socket_url = self.wss_url + "endpoint" + "?token=" + self.wss_public_token

        self._ws = websocket.WebSocketApp(socket_url, on_open=self.on_open, on_close=self.on_close,
                                         on_error=self.on_error, on_message=self.on_message)

        # print("WS:", self._ws)
        while True:
            try:
                self._ws.run_forever()
            except Exception as e:
                logger.error("Kucoin error in run_forever() method: %s", e)
            time.sleep(2)

    def on_open(self, ws):
        print("Connection established")
        logger.info("Kucoin connection opened")

        self.subscribe_channel(["/market/ticker:BTC-USDT", "/market/ticker:ETH-USDT"])

    def on_close(self, ws):
        print("Connection closed")
        # logger.warning("Kucoin Websocket connection closed")

    def on_error(self, ws, msg: str):
        print("Connection error:", msg)
        logger.error("Kucoin connection error: %s", msg)

    def on_message(self, ws, msg: str):
        sub_data = json.loads(msg)

        # print("show me data:", sub_data)

        if 'data' in sub_data:
            symbol = sub_data['topic'].split(':')[-1]

            # print('sub', sub_data['data'])

            if symbol not in self.prices:
                self.prices[symbol] = {
                    'price': float(sub_data['data']['price']),
                    'bid': float(sub_data['data']['bestBid']),
                    'ask': float(sub_data['data']['bestAsk'])

                }
            else:
                self.prices[symbol]['price'] = float(sub_data['data']['price'])
                self.prices[symbol]['bid'] = float(sub_data['data']['bestBid'])
                self.prices[symbol]['ask'] = float(sub_data['data']['bestAsk'])


    def subscribe_channel(self, contracts):
        data = dict()
        data['id'] = 1515124123
        data['type'] = "subscribe"
        data['privateChannel'] = False
        data['response'] = True
        # data['topic'] = "/market/ticker:all"

        for contract in contracts:
            data['topic'] = contract
            try:
                self._ws.send(json.dumps(data))
                print("Subscribed to", contract)
            except Exception as e:
                print("WebSocket error while subscribing to", contract, ":", e)

