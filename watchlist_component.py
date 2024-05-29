import tkinter as tk
from styling import *


class Watchlist(tk.Frame):
    def __init__(self, kucoin_contracts, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.kucoin_symbols = list(kucoin_contracts.keys())

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

    def remove_symbol(self, b_index: int):
        for h in self._headers:
            self.body_widgets[h][b_index].grid_forget()
            del self.body_widgets[h][b_index]

    def add_symbol(self, event):
        symbol = event.widget.get()

        if symbol in self.kucoin_symbols:
            b_index = self._body_index

            self.body_widgets['symbol'][b_index] = tk.Label(self._table_frame, text=symbol, bg=BG_COLOR, fg=FG_COLOR_2,
                                                            font=GLOBAL_FONT)
            self.body_widgets['symbol'][b_index].grid(row=b_index, column=0)

            self.body_widgets['exchange'][b_index] = tk.Label(self._table_frame, text="Kucoin", bg=BG_COLOR, fg=FG_COLOR_2,
                                                              font=GLOBAL_FONT)
            self.body_widgets['exchange'][b_index].grid(row=b_index, column=1)

            self.body_widgets['bid_var'][b_index] = tk.StringVar()
            self.body_widgets['bid'][b_index] = tk.Label(self._table_frame,
                                                         textvariable=self.body_widgets['bid_var'][b_index],
                                                         bg=BG_COLOR, fg=FG_COLOR_2, font=GLOBAL_FONT)
            self.body_widgets['bid'][b_index].grid(row=b_index, column=2)

            self.body_widgets['ask_var'][b_index] = tk.StringVar()
            self.body_widgets['ask'][b_index] = tk.Label(self._table_frame,
                                                         textvariable=self.body_widgets['ask_var'][b_index],
                                                         bg=BG_COLOR, fg=FG_COLOR_2, font=GLOBAL_FONT)
            self.body_widgets['ask'][b_index].grid(row=b_index, column=3)

            self.body_widgets['remove'][b_index] = tk.Button(self._table_frame, text="X",
                                                             bg="darkred", fg=FG_COLOR, font=GLOBAL_FONT,
                                                             command=lambda: self.remove_symbol(b_index))
            self.body_widgets['remove'][b_index].grid(row=b_index, column=4)

            self._body_index += 1

        event.widget.delete(0, tk.END)
