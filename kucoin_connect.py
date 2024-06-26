import logging
import time
import typing
import requests
import json
from datetime import datetime

import hashlib
import hmac
import base64

import websocket
import threading

from models import *

logger = logging.getLogger()


class KucoinAPI:
    def __init__(self, api_key: str, api_secret: str, api_passphrase: str):
        self.base_url = 'https://api.kucoin.com'
        self.futures_url = 'https://api-futures.kucoin.com'
        self.wss_url = 'wss://ws-api.kucoin.com/'
        self.api_key = api_key
        self.api_secret = api_secret
        self.api_passphrase = api_passphrase

        self.contracts = self.get_contracts()
        self.balances = self.get_balances()

        self.candleBox = self.get_symbol_stats("ETHUSDTM", 5, 3)

        # print('Show balances:', self.balances)
        # print('Show contracts:', self.contracts['XBTUSDTM'])

        self.prices = dict()
        self.logs = []

        self._ws_id = 1
        self._ws = None

        # t = threading.Thread(target=self._start_ws)
        # t.start()

        logger.info("Kucoin Client successfully initialized")

    def add_log(self, msg: str):
        logger.info("%s", msg)
        self.logs.append({"log": msg, "displayed": False})

    def _generate_signature(self, method: str, endpoint: str, timestamp: str, data: typing.Dict) -> bytes:
        prehash_string = f"{timestamp}{method}{endpoint}"

        if len(data) > 0:
            prehash_string += json.dumps(data)

        return base64.b64encode(hmac.new(self.api_secret.encode('utf-8'), prehash_string.encode(), hashlib.sha256).digest())

    def _make_request(self, method: str, endpoint: str, data: typing.Dict):
        headers = dict()
        timestamp = str(int(time.time() * 1000))
        headers['KC-API-SIGN'] = self._generate_signature(method, endpoint, timestamp, data)
        headers['KC-API-KEY'] = self.api_key
        headers['KC-API-TIMESTAMP'] = timestamp
        headers['KC-API-PASSPHRASE'] = self.api_passphrase

        if method == "GET":
            if endpoint.startswith('/api/v1/accounts'):
                try:
                    response = requests.get(self.base_url + endpoint, params=data, headers=headers)
                except Exception as e:
                    logger.error("Non futures url has failed.")
                    return None
            else:
                try:
                    if len(data) > 0:
                        response = requests.get(self.futures_url + endpoint, json=data, headers=headers)
                    else:
                        response = requests.get(self.futures_url + endpoint, params=data, headers=headers)
                except Exception as e:
                    logger.error("Connection error while making %s request to %s: %s", method, endpoint, e)
                    return None

        elif method == "POST":
            try:
                response = requests.post(self.futures_url + endpoint, json=data, headers=headers)
            except Exception as e:
                logger.error("Connection error while making %s request to %s: %s", method, endpoint, e)
                return None

        elif method == "DELETE":
            try:
                response = requests.delete(self.futures_url + endpoint, json=data, headers=headers)
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

    def get_balances(self):
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

    def get_contracts(self):
        endpoint = '/api/v1/contracts/active'
        contracts = dict()

        exchange_info = self._make_request("GET", endpoint, dict())

        if exchange_info['code'] == '200000':
            first_20_results = exchange_info['data'][:20]

            for contract_data in first_20_results:
                # print('Show all Contracts:', contract_data)
                contract_name = contract_data.get('symbol')
                contracts[contract_name] = Contract(contract_data)

            return contracts
        else:
            return print('Error during get contracts', exchange_info['code'])

    def get_bid_ask(self, contract: Contract):
        endpoint = f'/api/v1/ticker?symbol={contract.symbol}'

        # print('Getting 1 contract', contract.symbol)
        ba_response = self._make_request("GET", endpoint, contract.symbol)

        if ba_response['code'] == '200000':
            ba_data = ba_response['data']
            print('Getting 1 contract', ba_data)

            if contract.symbol not in self.prices:
                self.prices[contract.symbol] = {'bid': float(ba_data['bestBidPrice']), 'ask': float(ba_data['bestAskPrice'])}
            else:
                self.prices[contract.symbol]['bid'] = float(ba_data['bestBidPrice'])
                self.prices[contract.symbol]['ask'] = float(ba_data['bestAskPrice'])

            return self.prices[contract.symbol]
        else:
            return print('Error during get bid_ask of symbol', ba_response['code'])

    def get_historical_candles(self, symbol, interval):
        endpoint = f'/api/v1/kline/query?symbol={symbol}&granularity={interval}'
        candles = []
        data = dict()
        data['symbol'] = symbol
        data['granularity'] = interval
        # Start time (milisecond)
        # data['from'] = 1000
        # End time (milisecond)
        # data['to'] = 1000

        candles_res = self._make_request("GET", endpoint, data=data)
        raw_candles = candles_res['data']

        if candles_res['code'] == '200000':
            for c in raw_candles:
                # candles.append(Candle(c, interval))
                print(c)
            return candles
        else:
            return None

    def get_symbol_stats(self, symbol, interval, num_batches):
        all_candles = []
        total_difference = 0
        current_time = int(datetime.utcnow().timestamp() * 1000)
        interval_ms = interval * 60 * 1000 * 200
        total_green_candles = 0
        total_red_candles = 0

        data = dict()
        data['symbol'] = symbol
        data['granularity'] = interval

        for _ in range(num_batches):
            endpoint = f'/api/v1/kline/query?symbol={symbol}&granularity={interval}&to={current_time}'
            data['to'] = current_time
            batch_difference = 0
            batch_green_candles = 0
            batch_red_candles = 0

            print('****************')
            current_time -= interval_ms

            candles_res = self._make_request("GET", endpoint, data=data)
            candles = candles_res['data']

            print("Total candle count:", len(all_candles))
            print('First candle in batch:', candles[0])
            print('Last candle in batch', candles[-1])

            if not candles:
                break

            for entry in candles:
                timestamp = entry[0]
                highest_price = entry[2]
                lowest_price = entry[3]
                difference = highest_price - lowest_price
                batch_difference += difference

                readable_time = datetime.utcfromtimestamp(timestamp / 1000).strftime('%Y-%m-%d %H:%M:%S')

                all_candles.append({
                    'time': readable_time,
                    'difference': difference,
                    'open': entry[1],
                    'high': entry[2],
                    'low': entry[3],
                    'close': entry[4],
                    'volume': entry[5]
                })

                if entry[4] > entry[1]:
                    batch_green_candles += 1
                else:
                    batch_red_candles += 1

            total_difference += batch_difference
            total_green_candles += batch_green_candles
            total_red_candles += batch_red_candles
            print('Batch Green/red', batch_green_candles, batch_red_candles)
            print('Batch average true range:', batch_difference / 200)



        average_difference = total_difference / len(all_candles) if all_candles else 0
        print('')
        print('Total Green/red', total_green_candles, total_red_candles)
        print('Total atr:', average_difference)

        return all_candles, average_difference






    def place_order(self, order_data):
        endpoint = f'/api/v1/orders'
        order_placed = self._make_request('POST', endpoint, data=order_data)

        if len(order_placed) > 0:
            return order_placed
        else:
            return None

    def cancel_order(self, order_id):
        endpoint = f'/api/v1/orders/{order_id}'
        order_status = self._make_request('DELETE', endpoint, data=order_id)

        return order_status

    def get_order_status(self, order_id):
        clean_order_status = {}
        endpoint = f'/api/v1/orders/{order_id}'
        order_status = self._make_request('GET', endpoint, data=order_id)

        if order_status is not None:
            clean_order_status['symbol'] = order_status['data']['symbol']
            clean_order_status['side'] = order_status['data']['side']
            clean_order_status['size'] = order_status['data']['size']
            clean_order_status['price'] = order_status['data']['price']
            clean_order_status['isActive'] = order_status['data']['isActive']

            return clean_order_status

    def _start_ws(self):
        public_token = ''
        auth_endpoint = 'https://api.kucoin.com/api/v1/bullet-public'
        response = requests.post(auth_endpoint)

        if response.status_code == 200:
            token_data = response.json()
            public_token = token_data['data']['token']
        else:
            print("Error:", response.text)

        socket_url = self.wss_url + "endpoint" + "?token=" + public_token

        self._ws = websocket.WebSocketApp(socket_url, on_open=self.on_open, on_close=self.on_close, on_error=self.on_error, on_message=self.on_message)

        while True:
            try:
                self._ws.run_forever()
            except Exception as e:
                logger.error("Kucoin error in run_forever() method: %s", e)
            time.sleep(2)

    def on_open(self, ws):
        logger.info("Kucoin websocket connection opened")

        self.subscribe_channel(["/market/ticker:BTC-USDT", "/market/ticker:ETH-USDT"])

    def on_close(self, *args):
        logger.warning("Kucoin Websocket connection closed")

    def on_error(self, ws, msg: str):
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

            self.add_log(symbol + " " + str(sub_data['data']['bestBid']) + " / " + str(sub_data['data']['bestAsk']))

        # print('Socket returns:', self.prices)

    def subscribe_channel(self, contracts):
        data = dict()
        data['id'] = self._ws_id
        data['type'] = "subscribe"
        data['privateChannel'] = False
        data['response'] = True
        # data['topic'] = "/market/ticker:all"

        self._ws_id += 1

        for contract in contracts:
            data['topic'] = contract
            try:
                self._ws.send(json.dumps(data))
                print("Subscribed to", contract)
            except Exception as e:
                print("WebSocket error while subscribing to", contract, ":", e)


    def process_candles(self, candles):
        processed = []
        total_difference = 0

        for _ in range(num_batches):
            params = {
                'symbol': symbol,
                'granularity': interval,
                'limit': batch_size,
                'to': current_time
            }

            # Make the request to the API
            candles_res = self._make_request("GET", endpoint, params=params)
            candles = candles_res['data']

            if not candles:
                break

            for entry in candles:
                timestamp = entry[0]
                highest_price = entry[2]
                lowest_price = entry[3]
                difference = highest_price - lowest_price
                total_difference += difference

                # Convert timestamp to a readable format
                readable_time = datetime.utcfromtimestamp(timestamp / 1000).strftime('%Y-%m-%d %H:%M:%S')

                processed.append({
                    'time': readable_time,
                    'difference': difference
                })

        # Set the current time to the timestamp of the earliest candle minus one interval
        current_time = int(
            datetime.strptime(processed[-1]['time'], '%Y-%m-%d %H:%M:%S').timestamp() * 1000) - interval_ms

        average_difference = total_difference / len(candles) if candles else 0
        return processed, average_difference
