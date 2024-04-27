from config import API_KEY, API_SECRET, API_PASSPHRASE
from kucoin_connect import get_accounts, get_coin, get_coins
import pprint
import tkinter as tk


def get_price():
    symbol = 'BTC-USDT'
    price = get_coin(API_KEY, API_SECRET, API_PASSPHRASE, symbol)
    if price is not None:
        print(f"The current price of {symbol} is {price}")


def get_balance():
    balances = get_accounts(API_KEY, API_SECRET, API_PASSPHRASE)
    print("Here are your balances:")
    pprint.pprint(balances)


get_balance()


if __name__ == '__main__':
    root = tk.Tk()
    root.title("KuCoin Coins")
    root.configure(bg='gray12')

    crypto_font = ('Calibri', 11, 'bold')
    coins = get_coins()

    frame = tk.Frame(root, bg='gray')
    frame.pack(padx=10, pady=10)

    if coins:
        for i, coin in enumerate(coins):
            row_index = i // 5
            col_index = i % 5

            label_text = f"{i + 1}. {coin}"
            label = tk.Label(frame, text=label_text, font=crypto_font, fg='Steel Blue1', bg='gray12')
            label.grid(row=row_index, column=col_index, sticky='ew')

    # root.mainloop()



