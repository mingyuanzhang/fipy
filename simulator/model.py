from orderbook import OrderBookDict
from messages import Order, LimitOrder, MarketOrder
from messages import Ack, Reject, Filled, Canceled, TimeUpdate
from messages import BookUpdate

class Model(object):
    def __init__(self):
        pass

    def update_on_market(self, market_update):
        pass

    def update_on_timer(self, time_update):
        pass

    def update_on_ack(self, ack):
        pass

    def update_on_filled(self, filled):
        pass

    def update_on_canceled(self, canceled):
        pass

    def generate_message(self):
        pass

    def log_events(self):
        pass


