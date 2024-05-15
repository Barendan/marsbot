import tkinter as tk

from styling import *

class Watchlist(tk.Frame):
    def __init__(self, kucoin_contracts, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # self.kucoin_symbols = list(kucoin_contracts.keys())

        self._commands_frame = tk.Frame(self, bg=BG_COLOR)
        self._commands_frame.pack(side=tk.TOP)

        self._table_frame = tk.Frame(self, bg=BG_COLOR)
        self._table_frame.pack(side=tk.TOP)

        self.kucoin_label = tk.Label(self._commands_frame, text="Kucoin", bg=BG_COLOR, fg=FG_COLOR, font=BOLD_FONT)
        self.kucoin_label.grid(row=0, column=0)

        self.kucoin_entry = tk.Entry(self._commands_frame, fg=FG_COLOR, justify=tk.CENTER, insertbackground=FG_COLOR,
                                       bg=BG_COLOR_2)
        self.kucoin_entry.grid(row=1, column=0)
        self.kucoin_entry.bind("<Return>", self.add_symbol)


        self.body_widgets = dict()

        self._headers = ["symbol", "exchange", "bid", "ask", "remove"]

        for idx, h in enumerate(self._headers):
            header = tk.Label(self._table_frame, text=h.capitalize() if h != "remove" else "", bg=BG_COLOR,
                              fg=FG_COLOR, font=BOLD_FONT)
            header.grid(row=0, column=idx)

        for h in self._headers:
            self.body_widgets[h] = dict()
            if h in ["bid", "ask"]:
                self.body_widgets[h + "_var"] = dict()

        self._body_index = 1

    def add_symbol(self, event):
        symbol = event.widget.get()

        # run the request
        event.widget.delete(0, tk.END)
