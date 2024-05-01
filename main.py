from config import API_KEY, API_SECRET, API_PASSPHRASE
from kucoin_connect import KucoinAPI
import pprint
import tkinter as tk


kucoin_api = KucoinAPI(API_KEY, API_SECRET, API_PASSPHRASE)

balances = kucoin_api.get_accounts()


# Print the balances to verify if the connection is successful
print("Account Balances in Environment:")
print(balances)

coins = kucoin_api.get_coins()
# print("Here are some coins:", coins)

# example order data
order_data = {
    'clientOid': '0x000001DD_BA6DC170',
    'symbol': 'BTC-USDT',
    'side': 'buy',
    'type': 'limit',
    'price': 43200,
    'size': '0.001',
}
# order_status = kucoin_api.place_order(order_data)
# print("Order Status:", order_status)


# example cancel order
# order_id_to_cancel = '6632b02625856c0007894662'
# cancel_result = kucoin_api.cancel_order(order_id_to_cancel)
# if cancel_result:
#     print("Order canceled successfully.")


# example order status
# order_id_to_check = '6632b02625856c0007894662'
# order_status = kucoin_api.get_order_status(order_id_to_check)
# print("Order Status:", order_status)


if __name__ == '__main__':
    root = tk.Tk()
    root.title("KuCoin Coins")
    root.configure(bg='gray12')

    crypto_font = ('Calibri', 11, 'bold')
    # coins = get_coins()

    frame = tk.Frame(root, bg='gray')
    frame.pack(padx=10, pady=10)

    if coins:
        for i, coin in enumerate(coins):
            row_index = i // 5
            col_index = i % 5

            label_text = f"{i + 1}. {coin}"
            label = tk.Label(frame, text=label_text, font=crypto_font, fg='Steel Blue1', bg='gray12')
            label.grid(row=row_index, column=col_index, sticky='ew')

    root.mainloop()

