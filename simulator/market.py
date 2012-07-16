import datetime
import numpy as np
from orderbook import OrderBookQueue
from messages import Order, LimitOrder, MarketOrder
from messages import Ack, Reject, Filled, Canceled, TimeUpdate
from messages import BookUpdate


class Market(object):
    exchange = None
    product = None

    dates = []
    begin_time = None
    end_time = None

    market_data_keys = []
    market_data = None
    cur_row_id = 0
    cur_market_book = None

    client_order_book = None

    cur_event = None
    cur_inbound_message = None
    cur_outbound_message = None

    def __init__(self, exchange, product):
        self.exchange = exchange
        self.product = product

    def load_data(self):
        pass

    def initialize(self, date):
        pass

    def market_close(self, date):
        pass
    
    def run_one_event_loop(self, message):
        self.accept_message(message)
        self.act_on_message(message)
        generated_message = self.generate_message(message)
        self.log_events()
        return generated_message

    def accept_message(self, message):
        pass

    def act_on_message(self, message):
        pass

    def act_on_limit_order(self, limit_order):
        pass

    def act_on_market_order(self, market_order):
        pass

    def act_on_modify(self, modify):
        pass

    def act_on_cancel(self, cancel):
        pass

    def act_on_time_update(self, timeupdate):
        pass

    def match_on_market_order(self, market_order):
        pass

    def match_on_book_update(self):
        pass

    def generate_message(self):
        pass

    def generate_book_update(self):
        pass

    def log_events(self):
        pass

