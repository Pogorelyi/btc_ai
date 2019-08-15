from bitmex_websocket import BitMEXWebsocket
from time import sleep

end_point = "https://testnet.bitmex.com/api/v1"
api_key = 'rMnq_8rhjmuuw2O4WBIiA8Bj'
api_secret = '7s4RiqCKV9e1fggCJEmO87JRZiVvOr8RjDFNMH7BINb0UQVm'
sleep_seconds = 4


def get_price(ws):
    ws.get_instrument()
    ticker = ws.get_ticker()

    return ticker['last']
    # while (ws.ws.sock.connected):
    #     ticker = ws.get_ticker()
    #     print(ticker['last'])
    #     sleep(sleep_seconds)


def get_orders(ws):
    orders = ws.funds()
    print(orders)


if __name__ == "__main__":
    ws = BitMEXWebsocket(endpoint=end_point, symbol="XBTUSD", api_key=api_key, api_secret=api_secret)
    while 1:
        method = int(input("1. price | 2. orders\n"))
        if method == 1:
            print(get_price(ws))
        else:
            get_orders(ws)

