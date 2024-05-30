import tkinter as tk
import logging

from styling import *
from logging_component import Logging
from watchlist_component import Watchlist
from trades_component import TradesWatch

logger = logging.getLogger()


class Root(tk.Tk):
    def __init__(self, kucoin):
        super().__init__()

        self.kucoin = kucoin

        self.title("KuCoin Trading Bot")
        self.configure(bg=BG_COLOR)

        self._left_frame = tk.Frame(self, bg=BG_COLOR)
        self._left_frame.pack(side=tk.LEFT)

        self._right_frame = tk.Frame(self, bg=BG_COLOR)
        self._right_frame.pack(side=tk.RIGHT)

        self._watchlist_frame = Watchlist(self.kucoin.contracts, self._left_frame, bg=BG_COLOR)
        self._watchlist_frame.pack(side=tk.TOP)

        self._logging_frame = Logging(self._left_frame, bg=BG_COLOR)
        self._logging_frame.pack(side=tk.TOP)

        self._trades_frame = TradesWatch(self._right_frame, bg=BG_COLOR)
        self._trades_frame.pack(side=tk.TOP)

        self.update_ui()

    def update_ui(self):
        for log in self.kucoin.logs:
            if not log['displayed']:
                self._logging_frame.add_log(log['log'])
                log['displayed'] = True

        try:
            for key, value in self._watchlist_frame.body_widgets['symbol'].items():
                symbol = self._watchlist_frame.body_widgets['symbol'][key].cget("text")

                # print('Symbol input:', symbol)
                # print('Contract access', self.kucoin.contracts[symbol])

                if symbol not in self.kucoin.contracts:
                    continue

                if symbol not in self.kucoin.prices:
                    self.kucoin.get_bid_ask(self.kucoin.contracts[symbol])
                    continue

                prices = self.kucoin.prices[symbol]
                precision = self.kucoin.contracts[symbol].price_decimals

                # Convert decimal float into a whole number to represent precision
                precision_str = f"{precision:.1e}"
                exponent = int(precision_str.split('e')[-1])
                decimal_places = abs(exponent)

                if prices['bid'] is not None:
                    price_str = "{0:.{prec}f}".format(prices['bid'], prec=decimal_places)
                    self._watchlist_frame.body_widgets['bid_var'][key].set(price_str)
                if prices['ask'] is not None:
                    price_str = "{0:.{prec}f}".format(prices['ask'], prec=decimal_places)
                    self._watchlist_frame.body_widgets['ask_var'][key].set(price_str)
        except RuntimeError as e:
            logger.error("Error while looping through watchlist dictionary: %s", e)

        self.after(1500, self.update_ui)