
class Candle:
    def __init__(self, candle_info):
        self.timestamp = candle_info[0]
        self.open = float(candle_info[1])
        self.high = float(candle_info[2])
        self.low = float(candle_info[3])
        self.close = float(candle_info[4])
        self.volume = float(candle_info[5])


class Contract:
    def __init__(self, contract_info):
        self.symbol = contract_info['symbol']
        self.base_asset = contract_info['baseCurrency']
        self.quote_asset = contract_info['quoteCurrency']
        self.price_decimals = contract_info['tickSize']
        self.quantity_decimals = contract_info['lotSize']
        # self.lot_size = contract_info['lotSize']
        # self.tick_size = contract_info['tickSize']
        self.tick_size = 1 / pow(10, contract_info['tickSize'])
        self.lot_size = 1 / pow(10, contract_info['lotSize'])


class OrderStatus:
    def __init__(self, order_info):
        self.order_id = order_info['orderId']
        self.status = order_info['status']
        self.avg_price = float(order_info['avgPrice'])

