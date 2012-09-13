from collections import defaultdict
import datetime

class Simulator(object):
    
    timer_ms = None
    
    begin_time = None
    end_time = None
    
    date_list = []
    
    market_list = defaultdict(dict)
    model_list = []
    

    def __init__(self, timer_ms = 1000):
        self.timer_ms = timer_ms
        
        pass
    
    def load_market(self, market):
        
        pass
    
    def load_model(self, model):
        pass
    
    def run_on_date(self, adate):
        pass
    
    def run_all(self):
        pass
    
    def run_on_timer_loop(self):
        pass
    
    def run_on_all_events(self):
        pass
    
