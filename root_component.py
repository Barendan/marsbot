import tkinter as tk
import time

from styling import *
from logging_component import Logging
from watchlist_component import Watchlist

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

        self.update_ui()

        # self._logging_frame.add_log("This is a test message.")
        # time.sleep(2)
        # self._logging_frame.add_log("This is another test message.")

    def update_ui(self):
        for log in self.kucoin.logs:
            if not log['displayed']:
                self._logging_frame.add_log(log['log'])
                log['displayed'] = True

        self.after(1500, self.update_ui)