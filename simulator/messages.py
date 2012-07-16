class Message(object):
    msg_type = "Message"
    msg_id = 0
    msg_count = 0
    timestamps = []
    keys = []
    fields = {}
    def __init__(self):
        self.msg_id = self.__class__.msg_count
        self.__class__.msg_count += 1

    def get(self, fieldname):
        if fieldname not in self.keys:
            raise "Invalid call to get method: %s not in keys"%fieldname
        return self.fields[fieldname]

    def set(self, fieldname, fieldvalue):
        if fieldname not in self.keys:
            raise "Invalid call to set method: %s not in keys"%fieldname
        self.fields[fieldname] = fieldvalue

    def stamptime(self, timestamp):
        self.timestamps.append(timestamp)

    def to_string(self):
        string = str(self.timestamps[-1]) + '::' + self.msg_type + ':' + str(self.msg_id) + '@' + ','.join(["%s:%s"%(key, self.fields[key]) for key in self.keys])
        return string
    

## messages model sent to simulator
class Order(Message):
    msg_type = "Order"
    order_count = 0
    order_id = 0
    keys = ['exchange', 'product', 'price', 'quantity', 'side']
    fields = {}
    def __init__(self, price, quantity, side, product, exchange):
        super(Order,self).__init__()
        self.order_id = self.__class__.order_count
        self.__class__.order_count += 1
        self.set('exchange', exchange)
        self.set('product', product)
        self.set('price', price)
        self.set('quantity', quantity)
        self.set('side', side)

    def to_string(self):
        string = str(self.timestamps[-1]) + '::' + self.msg_type + ':' + str(self.order_id) + '::' + 'Message:' + str(self.msg_id) + '@' + ','.join(["%s:%s"%(key, self.fields[key]) for key in self.keys])
        return string


class LimitOrder(Order):
    msg_type = 'LimitOrder'
    limitorder_count = 0
    limitorder_id = 0
    def __init__(self, price, quantity, side, product, exchange):
        super(LimitOrder,self).__init__()
        self.order_id = self.__class__.limitorder_count
        self.__class__.limitorder_count += 1
        self.set('exchange', exchange)
        self.set('product', product)
        self.set('price', price)
        self.set('quantity', quantity)
        self.set('side', side)

class MarketOrder(Order):
    msg_type = 'MarketOrder'
    marketorder_count = 0
    marketorder_id = 0
    def __init__(self, price, quantity, side, product, exchange):
        super(MarketOrder,self).__init__()
        self.order_id = self.__class__.marketorder_count
        self.__class__.marketorder_count += 1
        self.set('exchange', exchange)
        self.set('product', product)
        self.set('price', price)
        self.set('quantity', quantity)
        self.set('side', side)

class Modify(Message):
    pass

class CancelReplace(Message):
    pass

class Cancel(Message):
    msg_type = 'Cancel'
    cancel_count = 0
    keys = ['exchange', 'product', 'orderid_to_cancel']
    fields = {}
    def __init__(self, limitorder_id, product, exchange):
        super(Cancel,self).__init__()
        self.__class__.cancel_count += 1
        self.set('exchange', exchange)
        self.set('product', product)
        self.set('orderid_to_cancel', limitorder_id)


## messages simulator sent to model with respect to orders
class Ack(Message):
    msg_type = 'Acknowledge'
    keys = ['exchange', 'product', 'orderid_acked']
    fields = {}
    def __init__(self, orderid, product, exchange):
        super(Ack,self).__init__()
        self.set('exchange', exchange)
        self.set('product', product)
        self.set('orderid_acked', orderid)

class Reject(Message):
    msg_type = 'Reject'
    keys = ['exchange', 'product', 'orderid_rejected']
    fields = {}
    def __init__(self, orderid, product, exchange):
        super(Ack,self).__init__()
        self.set('exchange', exchange)
        self.set('product', product)
        self.set('orderid_rejected', orderid)

class Filled(Message):
    msg_type = 'Filled'
    filled_count = 0
    filled_id = 0
    keys = ['exchange', 'product', 'orderid', 'price', 'quantity', 'side']
    fields = {}
    def __init__(self, orderid, price, quantity, side, product, exchange):
        super(Filled,self).__init__()
        self.set('exchange', exchange)
        self.set('product', product)
        self.set('orderid', orderid)
        self.set('price', price)
        self.set('quantity', quantity)
        self.set('side', side)

class Canceled(Message):
    msg_type = 'Canceled'
    keys = ['exchange', 'product', 'orderid_canceled']
    fields = {}
    def __init__(self, orderid, product, exchange):
        super(Canceled,self).__init__()
        self.set('exchange', exchange)
        self.set('product', product)
        self.set('orderid', orderid)


## market data messages simulator sent to model
class BookUpdate(Message):
    msg_type = 'BookUpdate'
    levels = 1
    required_keys = ['date', 'time', 'lastprice', 'volume', 'cumvolume', 'bid1', 'bidsize1', 'ask1', 'asksize1', 'lastdirection']
    optional_keys = []
    fields = {}
    def __init__(self, **kwargs):
        super(BookUpdate,self).__init__()
        self.keys = kwargs.keys()
        self.keys.sort()
        for key in kwargs:
            self.set(key, kwargs[key])

class TimeUpdate(Message):
    msg_type = 'TimeUpdate'
    keys = ['date', 'time']
    fields = {}
    def __init__(self, date, time):
        super(TimeUpdate,self).__init__()
        self.set('date', date)
        self.set('time', time)



