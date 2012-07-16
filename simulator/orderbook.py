import copy
import datetime
import numpy as np
from collections import defaultdict
from messages import Order, LimitOrder, MarketOrder
from messages import Ack, Reject, Filled, Canceled, TimeUpdate

## order book kept at the model side
## the purpose to keep records of orders the model send (assuming all new orders are acked, so no repond to ack)
## respond to reject, fills, and canceled (note that when only receives canceled notice, can we cancel an order)
class OrderBookDict(object):
    exchange = None
    product = None
    date = None
    buy_order_dict = defaultdict(dict)
    sell_order_dict = defaultdict(dict)

    def __init__(self, exchange, product, date):
        self.exchange = exchange
        self.product = product
        self.date = date

    def update(self, msg):
        if order.get('exchange') == self.exchange and order.get('product') == self.product:
            if isinstance(msg, Order):
                self.update_on_order(msg)
            elif isinstance(msg, Reject):
                self.update_on_reject(msg)
            elif isinstance(msg, Filled):
                self.update_on_filled(msg)
            elif isinstance(msg, Canceled):
                self.update_on_cancelled(msg)

    def update_on_order(self, order):
        side = order.get('side')
        orderid = order.order_id
        price = order.get('price')
        if side > 0:
            buy_order_dict[price][orderid] = order
        else :
            sell_order_dict[price][orderid] = order
    
    def find_price_for_orderid(self, orderid):
        for price in buy_order_dict.keys():
            if orderid in buy_order_dict[price].keys():
                return 1, price
        for price in sell_order_dict.keys():
            if orderid in sell_order_dict[price].keys():
                return -1, price
        return 0, 0

    def update_on_reject(self, reject):
        orderid = reject.get('orderid_rejected')
        side, price = self.find_price_for_orderid(orderid)
        if side > 0:
            del self.buy_order_dict[price][orderid]
        elif side < 0:
            del self.sell_order_dict[price][orderid]

    def update_on_canceled(self, canceled):
        orderid = canceled.get('orderid_canceled')
        side, price = self.find_price_for_orderid(orderid)
        if side > 0:
            del self.buy_order_dict[price][orderid]
        elif side < 0:
            del self.sell_order_dict[price][orderid]

    def update_on_filled(self, filled):
        orderid = filled.get('orderid')
        side, price = self.find_price_for_orderid(orderid)
        if side > 0:
            if filled.get('quantity') >= self.buy_order_dict[price][orderid].get('quantity'):
                del self.buy_order_dict[price][orderid]
            else :
                self.buy_order_dict[price][orderid].set('quantity', self.buy_order_dict[price][orderid].get('quantity') - filled.get('quantity'))
        elif side < 0:
            if filled.get('quantity') >= self.sell_order_dict[price][orderid].get('quantity'):
                del self.sell_order_dict[price][orderid]
            else :
                self.sell_order_dict[price][orderid].set('quantity', self.sell_order_dict[price][orderid].get('quantity') - filled.get('quantity'))
                                                         
## order book kept at the exchange simulator
## doing book record, no sending messages
## respond to new orders
## respond to reject, canceled, filled and timeupdates sent by the exchange simulator
## can provide exchange simulator orders to be filled
## keep record of current time
class OrderBookQueue(object):
    exchange = None
    product = None
    date = None
    cur_time = None
    buy_price_queue = []
    buy_order_queue = []
    sell_price_queue = []
    sell_order_queue = []
    
    def __init__(self, exchange, product, date):
        self.exchange = exchange
        self.product = product
        self.date = date
        self.cur_time = datetime.time(0, 0)

    def update(self, msg):
        if isinstance(msg, TimeUpdate):
            self.update_on_timeupdate(msg)
        if order.get('exchange') == self.exchange and order.get('product') == self.product:
            if isinstance(msg, Order):
                self.update_on_order(msg)
            elif isinstance(msg, Reject):
                self.update_on_reject(msg)
            elif isinstance(msg, Filled):
                self.update_on_filled(msg)
            elif isinstance(msg, Canceled):
                self.update_on_cancelled(msg)

    def update_on_order(self, order):
        order = copy.deepcopy(order)
        side = order.get('side')
        price = order.get('price')
        if side > 0:
            if price in self.buy_price_queue:
                idx = self.buy_price_queue.index(price)
                self.buy_order_queue[idx].append(order)
            else :
                idx = np.searchsorted(self.buy_price_queue, price)
                self.buy_price_queue.insert(idx, price)
                self.buy_order_queue.insert(idx, [order])
        else :
            if price in self.sell_price_queue:
                idx = self.sell_price_queue.index(price)
                self.sell_order_queue[idx].append(order)
            else :
                idx = np.searchsorted(self.sell_price_queue, price)
                self.sell_price_queue.insert(idx, price)
                self.sell_order_queue.insert(idx, [order])


    def delete_order(self, side, price_idx, order):
        if side > 0:
            if len(self.buy_price_queue[price_idx]) == 1:
                self.buy_price_queue = self.buy_price_queue[:price_idx] + self.buy_price_queue[(price_idx+1):]
                self.buy_order_queue = self.buy_order_queue[:price_idx] + self.buy_order_queue[(price_idx+1):]
            else :
                self.buy_order_queue[price_idx].remove(order)
        elif side < 0 :
            if len(self.sell_price_queue[price_idx]) == 1:
                self.sell_price_queue = self.sell_price_queue[:price_idx] + self.sell_price_queue[(price_idx+1):]
                self.sell_order_queue = self.sell_order_queue[:price_idx] + self.sell_order_queue[(price_idx+1):]
            else :
                self.sell_order_queue[price_idx].remove(order)
        

    def update_on_reject(self, reject):
        orderid = reject.get('orderid_rejected')
        side, price_idx, order = self.find_order_for_orderid(orderid)
        self.delete_order(side, price_idx, order)

    def update_on_canceled(self, canceled):
        orderid = canceled.get('orderid_canceled')
        side, price_idx, order = self.find_order_for_orderid(orderid)
        self.delete_order(side, price_idx, order)

    def update_on_filled(self, filled):
        orderid = filled.get('orderid')
        quantity = filled.get('quantity')
        side, price_idx, order = self.find_order_for_orderid(orderid)
        if order.get('quantity') <= quantity:
            self.delete_order(side, price_idx, order)
        else :
            order.set('quantity', order.get('quantity') -  quantity)

    def update_on_timeupdate(self, timeupdate):
        self.date = timeupdate.get('date')
        self.cur_time = timeupdate.get('time')
    
    def find_order_for_orderid(self, orderid):
        for price_idx in range(len(self.buy_price_queue)):
            orderid_list = [order.order_id for order in self.buy_order_queue[price_idx]]
            if orderid in orderid_list:
                return 1, price_idx, self.buy_order_queue[price_idx][orderid_list.index(orderid)]
        for price_idx in range(len(self.sell_price_queue)):
            orderid_list = [order.order_id for order in self.sell_order_queue[price_idx]]
            if orderid in orderid_list:
                return 1, price_idx, self.sell_order_queue[price_idx][orderid_list.index(orderid)]
        return 0, 0, None

    def find_top_orders_for_price_quantity(self, price, quantity, aggressor_side):
        top_order_list = []
        if aggressor_side > 0:
            cum_qty = 0
            for price_idx, sell_price in enumerate(self.sell_price_queue):
                if sell_price <= price and cum_qty < quantity:
                    for order in self.sell_order_queue[price_idx]:
                        top_order_list.append((sell_price, min(quantity - cum_qty, order.get('quantity')), order.order_id))
                        cum_qty += top_order_list[-1][1]
            return top_order_list
        if aggressor_side < 0:
            cum_qty = 0
            range_idx = range(len(self.buy_price_queue))
            range_idx.reverse()
            for price_idx in range_idx:
                buy_price = self.buy_price_queue[price_idx]
                if buy_price >= price and cum_qty < quantity:
                    for order in self.buy_order_queue[price_idx]:
                        top_order_list.append((buy_price, min(quantity - cum_qty, order.get('quantity')), order.order_id))
                        cum_qty += top_order_list[-1][1]
            return top_order_list
        return top_order_list


    
                                                             



