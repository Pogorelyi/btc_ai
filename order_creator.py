import bitmex
import json
from time import sleep
from timeit import default_timer as timer


class OrderCreator:

    def __init__(self, is_test_net, api_key, api_secret):
        self._client = bitmex.bitmex(test=is_test_net, api_key=api_key, api_secret=api_secret)
        self._max_order_check_time = 40

    def create_order(self, amount, price=None, order_type='Buy', close_order=False):
        print('\033[33m' + order_type + '\033[0m')
        print("\033[33mOrder Price: " + str(price) + '\033[0m')
        if close_order:
            result = self._client.Order.Order_new(symbol='XBTUSD', side=order_type, orderQty=100000, execInst='ReduceOnly').result()[0]
        else:
            result = self._client.Order.Order_new(symbol='XBTUSD', orderQty=amount, side=order_type, price=price, execInst='ParticipateDoNotInitiate').result()[0]

        price = result['price']
        if result['ordStatus'] == 'Filled':
            print("'\033[92m'create success: " + str(result['orderQty']) + " = " + str(result['price']) + '\033[0m')
            sleep(3)
            return price
        elif result['ordStatus'] == 'Canceled':
            return 0

        order_id = result['orderID']

        start = timer()
        while 1:
            end = timer()
            if end - start > self._max_order_check_time:
                self.cancel_order(order_id)
                return 0
            if self._is_order_filled(order_id):
                print("'\033[92m'create: " + str(result['orderQty']) + " = " + str(result['price']) + '\033[0m')
                break
            sleep(3)

        return price

    def cancel_order(self, order_id):
        self._client.Order.Order_cancel(orderID=order_id).result()
        print('\033[31mOrder canceled: ' + order_id + '\033[0m')

    def _is_order_filled(self, order_id):
        order_id = {"orderID": order_id}
        res = self._client.Order.Order_getOrders(filter=json.dumps(order_id)).result()

        return res and res[0] and res[0][0] and res[0][0]['ordStatus'] == 'Filled'


