import bitmex
import json
from time import sleep
from timeit import default_timer as timer
from config.printer import Printer


class OrderCreator:

    def __init__(self, is_test_net, api_key, api_secret):
        self._client = bitmex.bitmex(test=is_test_net, api_key=api_key, api_secret=api_secret)
        self._max_order_check_time = 60
        self._printer = Printer()

    def create_order(self, amount, price=None, order_type='Buy', close_order=False):
        self._printer.yellow_bold(order_type)
        self._printer.yellow_bold(str(price))
        if close_order:
            result = self._client.Order.Order_new(symbol='XBTUSD', side=order_type, orderQty=100000, execInst='ReduceOnly').result()[0]
        else:
            result = self._client.Order.Order_new(symbol='XBTUSD', orderQty=amount, side=order_type, price=price, execInst='ParticipateDoNotInitiate').result()[0]

        price = result['price']
        if result['ordStatus'] == 'Filled':
            self._printer.green("create success: " + str(result['orderQty']) + " = " + str(price))
            sleep(3)
            return price
        elif result['ordStatus'] == 'Canceled':
            sleep(4)
            return 0

        order_id = result['orderID']

        start = timer()
        while 1:
            end = timer()
            if end - start > self._max_order_check_time:
                self.cancel_order(order_id)
                return 0
            if self._is_order_filled(order_id):
                self._printer.green("create success: " + str(result['orderQty']) + " = " + str(price))
                break
            sleep(3)

        return price

    def cancel_order(self, order_id):
        self._client.Order.Order_cancel(orderID=order_id).result()
        self._printer.red('Order canceled: ' + order_id)

    def _is_order_filled(self, order_id):
        order_id = {"orderID": order_id}
        res = self._client.Order.Order_getOrders(filter=json.dumps(order_id)).result()
        return res and res[0] and res[0][0] and res[0][0]['ordStatus'] == 'Filled'


