from config import API_KEY, API_SECRET, API_PASSPHRASE
from kucoin_connect import get_accounts, get_coin, get_coins

from pprint import pprint
import tkinter as tk
from tkinter import scrolledtext


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

#
# def get_all():
#     coins = get_coins()
#     print("all the coins:", coins)
    # print("all the coins:", len(coins))
    # pprint(coins)

# get_all()


root = tk.Tk()
root.title("KuCoin Coins")

output_text = scrolledtext.ScrolledText(root, width=40, height=10, wrap=tk.WORD)
output_text.pack(padx=10, pady=10)

coins = get_coins()
if coins:
    output_text.insert(tk.END, "All Coins:\n")
    for coin in coins:
        output_text.insert(tk.END, coin + '\n')


root.mainloop()




