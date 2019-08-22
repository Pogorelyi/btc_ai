from bitmex_websocket import BitMEXWebsocket
from time import sleep
import config.account as account
from order_creator import OrderCreator
from cache import Cache
from config.printer import Printer
import random

sleep_seconds = 4
maxUnrealisedPnl = 14000
start_contracts = 100
averaging_price_diff = 20
close_price_diff = 10
max_long_position_increments = 4
position_multiplier = 2

#cache = Cache()

printer = Printer()

position = random.choice(['long', 'short'])


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

    return round(((start_price * before_long_amount) + (last_price * new_contracts_amount) ) / long_current_amount, 1)


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
            start_price = creator_long.create_order(start_contracts, last_price-0.5)
            if start_price == 0:
                printer.indiana('start order failed. restart')
                long_is_order_closed = True
            else:
                long_current_amount = start_contracts
                long_is_order_closed = False

        if not long_is_order_closed:
            price_diff = last_price - start_price
            printer.info(str(last_price) + ' - ' + str(start_price) + ' = ' + str(price_diff))

        if not long_is_order_closed and price_diff < -averaging_price_diff and long_position_increments < max_long_position_increments:
            before_long_amount = long_current_amount
            printer.yellow('averaging start')
            created_price = creator_long.create_order(long_current_amount*position_multiplier, last_price)
            if created_price != 0:
                long_current_amount = long_current_amount + long_current_amount * position_multiplier
                long_position_increments = long_position_increments + 1
                start_price = calculate_start_price(start_price, before_long_amount, created_price, long_current_amount)
                printer.green('averaging success: contracts = ' + str(long_current_amount))
            else:
                printer.red('averaging error')
                sleep(2)

        # close current position
        if not long_is_order_closed and price_diff > close_price_diff:
            printer.info('Close order')
            sell_price = creator_long.create_order(long_current_amount, order_type='Sell', close_order=True)
            if sell_price != 0:
                long_is_order_closed = True
                long_current_amount = 0
                print('\033[35m Close Success \033[0m')
                printer.green('Close Success')
            else:
                printer.red('Close Error')

        # SHORT logic

        sleep(sleep_seconds)

