from bitmex_websocket import BitMEXWebsocket
import config.account as account
from order_creator import OrderCreator
from bot import MainBot
import time


def create_short_client():
    return OrderCreator(account.is_test_net(), account.get_api_key_short(), account.get_api_secret_short())


def get_strategy():
    timestamp = int(time.time())
    rand_value = timestamp % 2
    return 'long' if rand_value == 1 else 'short'


if __name__ == "__main__":
    ws = BitMEXWebsocket(
        endpoint=account.get_end_point(),
        symbol="XBTUSD",
        api_key=account.get_api_key_short(),
        api_secret=account.get_api_secret_short()
    )
    ws.get_instrument()

    bot = MainBot(api_client=create_short_client(), web_socket=ws)

    try:
        bot.run(get_strategy())
    except KeyboardInterrupt:
        bot.clear_cache()
        exit(0)
        raise
    finally:
        bot.clear_cache()


