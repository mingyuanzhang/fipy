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
        self.fields = {}
        self.msg_id = Message.msg_count
        Message.msg_count += 1
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
    def __init__(self, price, quantity, side, product, exchange):
        super(LimitOrder,self).__init__(price, quantity, side, product, exchange)
        self.order_id = Order.order_count
        Order.order_count += 1
        self.__class__.limitorder_count += 1


class MarketOrder(Order):
    msg_type = 'MarketOrder'
    marketorder_count = 0
    def __init__(self, price, quantity, side, product, exchange):
        super(MarketOrder,self).__init__(price, quantity, side, product, exchange)
        self.order_id = Order.order_count
        Order.order_count += 1
        self.__class__.marketorder_count += 1


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
        self.fields = {}
        self.msg_id = Message.msg_count
        Message.msg_count += 1
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
        self.fields = {}
        self.msg_id = Message.msg_count
        Message.msg_count += 1
        self.set('exchange', exchange)
        self.set('product', product)
        self.set('orderid_acked', orderid)

class Reject(Message):
    msg_type = 'Reject'
    keys = ['exchange', 'product', 'orderid_rejected']
    fields = {}
    def __init__(self, orderid, product, exchange):
        self.fields = {}
        self.msg_id = Message.msg_count
        Message.msg_count += 1
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
        self.fields = {}
        self.msg_id = Message.msg_count
        Message.msg_count += 1
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
        self.fields = {}
        self.msg_id = Message.msg_count
        Message.msg_count += 1
        self.set('exchange', exchange)
        self.set('product', product)
        self.set('orderid_canceled', orderid)


## market data messages simulator sent to model
class BookUpdate(Message):
    msg_type = 'BookUpdate'
    levels = 1
    required_keys = ['date', 'time', 'lastprice', 'volume', 'cumvolume', 'bid1', 'bidsize1', 'ask1', 'asksize1', 'lastdirection']
    optional_keys = []
    fields = {}
    def __init__(self, **kwargs):
        self.fields = {}
        self.msg_id = Message.msg_count
        Message.msg_count += 1
        self.keys = kwargs.keys()
        self.keys.sort()
        for key in kwargs:
            self.set(key, kwargs[key])

class TimeUpdate(Message):
    msg_type = 'TimeUpdate'
    keys = ['date', 'time']
    fields = {}
    def __init__(self, date, time):
        self.fields = {}
        self.msg_id = Message.msg_count
        Message.msg_count += 1
        self.set('date', date)
        self.set('time', time)



def test_all_messages():
    Message.msg_count = 0
    Order.order_count = 0
    assert Message.msg_count == 0
    assert Order.order_count == 0
    order = Order(0.1, 100, 1, 'aa', 'bb')
    order.stamptime('now')
    print order.to_string()
    assert order.to_string() == 'now::Order:0::Message:0@exchange:bb,product:aa,price:0.1,quantity:100,side:1'
    print Message.msg_count, Order.order_count
    assert Message.msg_count == 1
    assert Order.order_count == 1

    limit_order = LimitOrder(0.1, 100, 1, 'aa', 'bb')
    limit_order.stamptime('now1')
    print limit_order.to_string()
    assert limit_order.to_string() == 'now1::LimitOrder:1::Message:1@exchange:bb,product:aa,price:0.1,quantity:100,side:1'

    market_order = MarketOrder(0.1, 100, 1, 'aa', 'bb')
    market_order.stamptime('now2')
    print market_order.to_string()
    assert market_order.to_string() == 'now2::MarketOrder:2::Message:2@exchange:bb,product:aa,price:0.1,quantity:100,side:1'
    
    cancel = Cancel(1, 'aa', 'bb')
    cancel.stamptime('now3')
    print cancel.to_string()
    assert cancel.to_string() == 'now3::Cancel:3@exchange:bb,product:aa,orderid_to_cancel:1'

    ack = Ack(2, 'aa', 'bb')
    ack.stamptime('now4')
    print ack.to_string()
    assert ack.to_string() == 'now4::Acknowledge:4@exchange:bb,product:aa,orderid_acked:2'

    reject = Reject(2, 'aa', 'bb')
    reject.stamptime('now5')
    print reject.to_string()
    assert reject.to_string() == 'now5::Reject:5@exchange:bb,product:aa,orderid_rejected:2'

    filled = Filled(2, 0.1, 100, 1, 'aa', 'bb')
    filled.stamptime('now6')
    print filled.to_string()
    assert filled.to_string() == 'now6::Filled:6@exchange:bb,product:aa,orderid:2,price:0.1,quantity:100,side:1'

    canceled = Canceled(1, 'aa', 'bb')
    canceled.stamptime('now7')
    print canceled.to_string()
    assert canceled.to_string() == 'now7::Canceled:7@exchange:bb,product:aa,orderid_canceled:1'

    bookupdate = BookUpdate(date = '111', time = '000', bid1 = 10, ask1 = 20)
    bookupdate.stamptime('now8')
    print bookupdate.to_string()
    assert bookupdate.to_string() == 'now8::BookUpdate:8@ask1:20,bid1:10,date:111,time:000'

    timeupdate = TimeUpdate('111', '000')
    timeupdate.stamptime('now9')
    print timeupdate.to_string()
    assert timeupdate.to_string() == 'now9::TimeUpdate:9@date:111,time:000'
    
    
    

