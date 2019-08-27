from cache import Cache
from config.printer import Printer
from time import sleep
import time


class MainBot:

    SHORT_ORDER = 'short'
    LONG_ORDER = 'long'
    IS_CLOSED_SUFFIX = '_is_closed'
    ORDER_VALUE_SUFFIX = '_value'
    CURRENT_TREND = 'long'

    sleep_seconds = 4
    start_contracts = 100
    averaging_price_diff = -40
    apposite_order_max_diff = 50
    close_price_diff = 20
    max_position_increments = 5
    position_multiplier = 1.5
    _strategy = 'long'
    close_order_type = 'Sell'

    current_position_increments = 1
    is_order_closed = True
    price_diff = 0

    def __init__(self, api_client, web_socket):
        self.cache = Cache()
        self.api_client = api_client
        self.ws = web_socket
        self.printer = Printer()

    def run(self, strategy):
        current_amount = self.start_contracts
        start_price = 0
        price_diff = 0

        self.set_cache_is_closed(1)

        #is_main_strategy = self.CURRENT_TREND == strategy

        while 1:
            last_price = self.get_price()


            # start trade order
            if self.is_order_closed:
                self._strategy = strategy if strategy != 'rand' else self.get_strategy()
                self.close_order_type = 'Buy' if self._strategy == self.SHORT_ORDER else 'Sell'
                opposite_order_status = self.get_opposite_order_status()
                opposite_order_start = self.get_opposite_order_value()

                if opposite_order_status == 0 or abs(last_price - opposite_order_start) < self.apposite_order_max_diff:
                    if opposite_order_status == 1:
                        print(abs(last_price - opposite_order_start))
                    if self._strategy == self.SHORT_ORDER:
                        start_price = self.api_client.create_order(self.start_contracts, last_price + 0.5, order_type='Sell')
                    else :
                        start_price = self.api_client.create_order(self.start_contracts, last_price - 0.5)
                    if start_price == 0:
                        self.printer.indiana('start order failed. restart')
                        self.is_order_closed = True
                    else:
                        current_amount = self.start_contracts
                        self.is_order_closed = False
                        self.set_cache_is_closed(0)
                        self.set_cache_position_price(start_price)
                else:
                    #print(opposite_order_status)
                    #print(abs(last_price - opposite_order_start) < self.apposite_order_max_diff)
                    self.printer.red('wait for opposite')

            if not self.is_order_closed:
                price_diff = (start_price - last_price) if self._strategy == self.SHORT_ORDER else (last_price - start_price)
                self.printer.info(str(last_price) + ' - ' + str(start_price) + ' = ' + str(price_diff))

            # averaging
            if not self.is_order_closed \
                    and price_diff < self.averaging_price_diff \
                    and self.current_position_increments < self.max_position_increments:
                before_amount = current_amount
                self.printer.yellow('averaging start: ' + str(current_amount * self.position_multiplier))
                if self._strategy == self.SHORT_ORDER:
                    created_price = self.api_client.create_order(current_amount * self.position_multiplier, last_price, order_type='Sell')
                else:
                    created_price = self.api_client.create_order(current_amount * self.position_multiplier, last_price)

                if created_price != 0:
                    current_amount = current_amount + current_amount * self.position_multiplier
                    self.current_position_increments = self.current_position_increments + 1
                    start_price = self.calculate_start_price(start_price, before_amount, created_price, current_amount)
                    self.printer.green('averaging success: contracts = ' + str(current_amount))
                    self.set_cache_position_price(start_price)
                else:
                    self.printer.red('averaging error')
                    sleep(2)

            # close current position
            if not self.is_order_closed and price_diff > self.close_price_diff:
                self.printer.info('Close order')
                sell_price = self.api_client.create_order(current_amount, order_type=self.close_order_type, close_order=True)
                if sell_price != 0:
                    self.is_order_closed = True
                    current_amount = 0
                    self.printer.green('Close Success')
                    self.set_cache_is_closed(1)
                    self.set_cache_position_price(0)
                    self.printer.info('wait before open order')
                    sleep(30)
                else:
                    self.printer.red('Close Error')

            sleep(self.sleep_seconds)

    def get_price(self):
        ticker = self.ws.get_ticker()

        return ticker['last']

    def get_opposite_order_status(self):
        opposite_order = self.get_opposite_order()
        cache_key = opposite_order + self.IS_CLOSED_SUFFIX
        value = self.cache.get(cache_key, get_int=True)

        return value if value else 0

    def set_cache_position_price(self, price):
        cache_key = self._strategy + self.ORDER_VALUE_SUFFIX
        self.cache.set(cache_key, price)

    def get_opposite_order_value(self):
        opposite_order = self.get_opposite_order()
        cache_key = opposite_order + self.ORDER_VALUE_SUFFIX
        value = self.cache.get(cache_key)

        return value if value else 10000000

    def get_opposite_order(self):
        return self.LONG_ORDER if self._strategy == self.SHORT_ORDER else self.SHORT_ORDER

    def set_cache_is_closed(self, is_closed):
        is_current_position_closed_key = self._strategy + self.IS_CLOSED_SUFFIX
        self.cache.set(is_current_position_closed_key, is_closed)

    def clear_cache(self):
        self.cache.clear_all()

    @staticmethod
    def calculate_start_price(start_price, before_long_amount, last_price, long_current_amount):
        new_contracts_amount = long_current_amount - before_long_amount

        return round(((start_price * before_long_amount)+(last_price * new_contracts_amount))/long_current_amount, 1)

    @staticmethod
    def get_strategy():
        timestamp = int(time.time())
        rand_value = timestamp % 2
        return 'long' if rand_value == 1 else 'short'



