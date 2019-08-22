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
max_short_position_increments = 4
position_multiplier = 2

#cache = Cache()

printer = Printer()

position = random.choice(['short', 'short'])


def get_price(ws):
    ticker = ws.get_ticker()

    return ticker['last']
    # while (ws.ws.sock.connected):
    #     ticker = ws.get_ticker()
    #     print(ticker['last'])
    #     sleep(sleep_seconds)


def create_short_client():
    return OrderCreator(account.is_test_net(), account.get_api_key_short(), account.get_api_secret_short())


def get_orders(ws):
    orders = ws.funds()
    for key in orders:
        print(key + ":" + str(orders[key]))


def calculate_start_price(start_price, before_short_amount, last_price, short_current_amount):
    new_contracts_amount = short_current_amount - before_short_amount

    return round(((start_price * before_short_amount) + (last_price * new_contracts_amount) ) / short_current_amount, 1)


if __name__ == "__main__":
    creator_short = create_short_client()

    ws = BitMEXWebsocket(endpoint=account.get_end_point(), symbol="XBTUSD", api_key=account.get_api_key_short(), api_secret=account.get_api_secret_short())
    ws.get_instrument()
    start_price = 0

    short_current_amount = start_contracts

    short_position_increments = 1
    short_is_order_closed = True
    price_diff = 0

    while 1:
        last_price = get_price(ws)

        # short logic
        if short_is_order_closed:
            start_price = creator_short.create_order(start_contracts, last_price+0.5, order_type='Sell')
            if start_price == 0:
                printer.indiana('start order failed. restart')
                short_is_order_closed = True
            else:
                short_current_amount = start_contracts
                short_is_order_closed = False

        if not short_is_order_closed:
            price_diff = start_price - last_price
            printer.info(str(last_price) + ' - ' + str(start_price) + ' = ' + str(price_diff))

        if not short_is_order_closed and price_diff < -averaging_price_diff and short_position_increments < max_short_position_increments:
            before_short_amount = short_current_amount
            printer.yellow('averaging start')
            created_price = creator_short.create_order(short_current_amount*position_multiplier, last_price, order_type='Sell')
            if created_price != 0:
                short_current_amount = short_current_amount + short_current_amount * position_multiplier
                short_position_increments = short_position_increments + 1
                start_price = calculate_start_price(start_price, before_short_amount, created_price, short_current_amount)
                printer.green('averaging success: contracts = ' + str(short_current_amount))
            else:
                printer.red('averaging error')
                sleep(2)

        # close current position
        if not short_is_order_closed and price_diff > close_price_diff:
            printer.info('Close order')
            sell_price = creator_short.create_order(short_current_amount, order_type='Buy', close_order=True)
            if sell_price != 0:
                short_is_order_closed = True
                short_current_amount = 0
                print('\033[35m Close Success \033[0m')
                printer.green('Close Success')
            else:
                printer.red('Close Error')

        # SHORT logic

        sleep(sleep_seconds)

