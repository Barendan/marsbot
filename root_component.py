import tkinter as tk

from styling import *
from logging_component import Logging

class Root(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("KuCoin Coins")
        self.configure(bg=BG_COLOR)

        self.left_frame = tk.Frame(self, bg=BG_COLOR)
        self.left_frame.pack(side=tk.LEFT)

        self.right_frame = tk.Frame(self, bg=BG_COLOR)
        self.right_frame.pack(side=tk.RIGHT)

        self.logging_frame = Logging(self.left_frame, bg=BG_COLOR)
        self.logging_frame.pack(side=tk.TOP)

