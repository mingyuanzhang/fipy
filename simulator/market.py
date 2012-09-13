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

    raw_data = None
    
    market_data_keys = []
    market_data = None
    cur_date = None
    cur_row_id = 0
    cur_market_book = None

    client_order_book = None

    cur_event = None
    cur_inbound_message = None
    cur_outbound_message_queue = []

    def __init__(self, exchange, product):
        self.exchange = exchange
        self.product = product

    def load_data(self):
        pass

    def initialize(self, date):
        self.client_order_book = OrderBookQueue(self.exchange, self.product, date)
        self.market_data = raw_data[np.where(self.raw_data['date'] == date)]
        self.cur_date = date
        self.cur_row_id = 0
        self.cur_market_book = self.market_data[self.cur_row_id]

    def market_close(self, date):
        ## implement other market specific stuff at close
        self.client_order_book = None
    
    def run_one_event_loop(self, inbound_messages):
        outbound_messages = self.run_through_inbound_message_queue(inbound_messages)
        book_update = self.generate_book_update()
        return outbound_messages, book_update

    def run_through_inbound_message_queue(self, message_queue):
        for message in message_queue:
            self.accept_message(message)
            self.act_on_message(message)
            generated_messages = self.generate_outbound_messages()
            self.log_events()
        return generated_messages

    def accept_message(self, message):
        self.cur_event = message
        self.cur_inbound_message = message
        #self.client_order_book.update(message)

    def act_on_message(self, message):
        if isinstance(message, TimeUpdate):
            self.act_on_time_update(message)
        elif isinstance(message, LimitOrder):
            self.act_on_limit_order(message)
        elif isinstance(message, MarketOrder):
            self.act_on_market_order(message)
        elif isinstance(message, Modify):
            self.act_on_modify(message)
        elif isinstance(message, Cancel):
            self.act_on_cancel(message)

    def act_on_limit_order(self, limit_order):
        filled_message = self.match_on_market_order(limit_order)
        self.client_order_book.update(limit_order)
        if filled_message.get('quantity') > 0:
            self.cur_outbound_message_queue.append(filled_message)
            self.client_order_book.update(filled_message)
            
    def act_on_market_order(self, market_order):
        filled_message = self.match_on_market_order(market_order)
        if filled_message.get('quantity') > 0:
            self.cur_outbound_message_queue.append(filled_message)
        else :
            canceled = Canceled(market_order.order_id, self.product, self.exchange)
            self.cur_outbound_message_queue.append(canceled)

    def act_on_modify(self, modify):
        raise "Modify action not implemented"

    def act_on_cancel(self, cancel):
        self.client_order_book.update(cancel)

    def act_on_time_update(self, timeupdate):
        while self.market_data[self.cur_row_id]['time'] < timeupdate.get('time'):
            self.cur_row_id += 1
            self.cur_market_book = self.market_data[self.cur_row_id]
            filled_messages = self.match_on_book_update()
            self.cur_outbound_message_queue += filled_messages
            for fm in filled_messages:
                self.client_order_book.update(fm)

    def match_on_market_order(self, market_order):
        ## here only implemented simply just match on level 1 data with infinite quantity
        if market_order.get('side') > 0:
            if market_order.get('price') >= self.cur_market_book['ask1']:
                filled_message = Filled(market_order.order_id, self.cur_market_book['ask1'],
                                        market_order.get('quantity'), market_order.get('side'),
                                        market_order.get('product'), market_order.get('exchange'))
            else :
                filled_message = Filled(market_order.order_id, self.cur_market_book['ask1'],
                                        0, market_order.get('side'),
                                        market_order.get('product'), market_order.get('exchange'))
        else :
            if market_order.get('price') <= self.cur_market_book['bid1']:
                filled_message = Filled(market_order.order_id, self.cur_market_book['bid1'],
                                        market_order.get('quantity'), market_order.get('side'),
                                        market_order.get('product'), market_order.get('exchange'))
            else :
                filled_message = Filled(market_order.order_id, self.cur_market_book['bid1'],
                                        0, market_order.get('side'),
                                        market_order.get('product'), market_order.get('exchange'))
        return filled_message

    def match_on_book_update(self):
        ## here implement the conservative matching: when book disapear, fill on full size
        bidprice = self.cur_market_book['bid1'] + 0.0001
        buy_top_order_list = self.client_order_book.find_top_orders_for_price_quantity(bidprice, np.inf, -1)
        askprice = self.cur_market_book['ask1'] - 0.0001
        sell_top_order_list = self.client_order_book.find_top_orders_for_price_quantity(askprice, np.inf, 1)
        filled_messages = []
        for order in buy_top_order_list + sell_top_order_list:
            filled_messages.append(Filled(order.order_id, order.get('price'),
                                          order.get('quantity'), order.get('side'),
                                          order.get('product'), order.get('exchange')))
        return filled_messages

    def generate_outbound_messages(self):
        outbound_messages = self.cur_outbound_message_queue
        self.cur_outbound_message_queue = []
        return outbound_messages

    def generate_book_update(self):
        dictionary = dict(zip(self.market_data_keys, list(self.cur_market_book)))
        return BookUpdate(dictionary)

    def log_events(self):
        pass

