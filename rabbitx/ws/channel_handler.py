from typing import Callable

class ChannelHandler:
    def __init__(self, name:str):
        self.name = name

    def on_subscribe(self, data: dict):
        pass

    def on_data(self, data: dict):
        pass