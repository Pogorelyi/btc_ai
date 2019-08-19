import bitmex


class OrderCreator:

    def __init__(self, is_test_net, api_key, api_secret):
        self._client = bitmex.bitmex(test=is_test_net, api_key=api_key, api_secret=api_secret)

    def create_order(self, amount):
        result = self._client.Order.Order_new(symbol='XBTUSD', orderQty=amount).result()
        print("'\033[92m'create: " + str(result[0]['orderQty']) + " = " + str(result[0]['price']) + '\033[0m')

        return result[0]['price']

