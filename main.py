from config import API_KEY, API_SECRET, API_PASSPHRASE
from kucoin_connect import KucoinAPI
from root_component import Root

kucoin_api = KucoinAPI(API_KEY, API_SECRET, API_PASSPHRASE)

# GET BALANCES TEST
balances = kucoin_api.get_accounts()
print("Account Balances in Environment:")
print(balances)

# GET ALL COINS TEST
# coins = kucoin_api.get_coins()
# print('Fetched coins:',coins)

# GET 1 COIN TEST
# coin = kucoin_api.get_coin('BTC-USDT')
# print('Fetched coin:',coin)


# GET CANDLES TEST
klines_btc = {
    'symbol': 'BTC-USDT',
    'type': '1hour',
}
# Call the method with the parameters object
# historical_candles = kucoin_api.get_historical_candles(klines_btc)
# if historical_candles:
#     print("Historical Candles:")
#     print(historical_candles)



# SAMPLE ORDER DATA
order_data = {
    'clientOid': '0x000001DD_BA6DC170',
    'symbol': 'BTC-USDT',
    'side': 'buy',
    'type': 'limit',
    'price': 43200,
    'size': '0.001',
}
# order_made = kucoin_api.place_order(order_data)
# print("Order made:", order_made)

# example order status
# order_id_to_check = '6644fbc38de67e0007bdd142'
# order_status = kucoin_api.get_order_status(order_id_to_check)
# print("Order Status:", order_status)

# example cancel order
# order_id_to_cancel = '6644fbc38de67e0007bdd142'
# cancel_result = kucoin_api.cancel_order(order_id_to_cancel)
# if 'data' in cancel_result and 'cancelledOrderIds' in cancel_result['data']:
#     cancelled_order_ids = cancel_result['data']['cancelledOrderIds']
#     print('Cancelled order IDs:', cancelled_order_ids)
# else:
#     print('Error in order cancel:', cancel_result['msg'])



if __name__ == '__main__':
    # if coins:
    #     for i, coin in enumerate(coins):
    #         row_index = i // 5
    #         col_index = i % 5
    #
    #         label_text = f"{i + 1}. {coin}"
    #         label = tk.Label(frame, text=label_text, font=crypto_font, fg='Steel Blue1', bg='gray12')
    #         label.grid(row=row_index, column=col_index, sticky='ew')

    root = Root()
    root.mainloop()
