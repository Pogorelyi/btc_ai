from bitmex_websocket import BitMEXWebsocket
from time import sleep
import config.account as account
from order_creator import OrderCreator
from cache import Cache

sleep_seconds = 4
maxUnrealisedPnl = 10000
start_contracts = 100
averaging_price_diff = 10
close_price_diff = 5
max_long_position_increments = 5
position_multiplier = 2

cache = Cache()


def get_price(ws):
    ticker = ws.get_ticker()

    return ticker['last']
    # while (ws.ws.sock.connected):
    #     ticker = ws.get_ticker()
    #     print(ticker['last'])
    #     sleep(sleep_seconds)


def create_long_client():
    return OrderCreator(account.is_test_net(), account.get_api_key_long(), account.get_api_secret_long())


def get_orders(ws):
    orders = ws.funds()
    for key in orders:
        print(key + ":" + str(orders[key]))


def calculate_start_price(start_price, before_long_amount, last_price, long_current_amount):
    new_contracts_amount = long_current_amount - before_long_amount

    return ((start_price * before_long_amount) + (last_price * new_contracts_amount) ) / long_current_amount


if __name__ == "__main__":
    creator_long = create_long_client()

    ws = BitMEXWebsocket(endpoint=account.get_end_point(), symbol="XBTUSD", api_key=account.get_api_key_long(), api_secret=account.get_api_secret_long())
    ws.get_instrument()
    start_price = 0

    long_current_amount = start_contracts

    long_position_increments = 1
    long_is_order_closed = True
    price_diff = 0

    while 1:
        last_price = get_price(ws)

        # LONG logic
        if long_is_order_closed:
            start_price = creator_long.create_order(start_contracts, last_price - 0.5)
            if start_price == 0:
                print('start order failed. restart')
                long_is_order_closed = True
            else:
                long_current_amount = start_contracts
                long_is_order_closed = False

        if not long_is_order_closed:
            price_diff = last_price - start_price
            print('Start Price: ' + str(start_price))
            print('Last Price: ' + str(last_price))
            print('Price Diff: ' + str(price_diff))

        if not long_is_order_closed and price_diff < -averaging_price_diff and long_position_increments < max_long_position_increments:
            before_long_amount = long_current_amount
            print('averaging start')
            created_price = creator_long.create_order(long_current_amount*position_multiplier, last_price + 0.5)
            if created_price != 0:
                long_current_amount = long_current_amount + long_current_amount * position_multiplier
                long_position_increments = long_position_increments + 1
                start_price = calculate_start_price(start_price, before_long_amount, created_price, long_current_amount)
                print('\033[32m averaging success\033[0m')
            else :
                print('\033[31m averaging error\033[0m')
                sleep(2)

        # close current position
        if not long_is_order_closed and price_diff > close_price_diff:
            print('\033[35m Close order\033[0m')
            sell_price = creator_long.create_order(0 - long_current_amount, order_type='Sell', close_order=True)
            if sell_price != 0:
                long_is_order_closed = True
                long_current_amount = 0
                print('\033[35m Close Success \033[0m')
            else:
                print('\033[31m Close Error \033[0m')

        # SHORT logic

        sleep(sleep_seconds)

