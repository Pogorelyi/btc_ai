from bitmex_websocket import BitMEXWebsocket
import config.account as account
from order_creator import OrderCreator
from bot import MainBot



def create_short_client():
    return OrderCreator(account.is_test_net(), account.get_api_key_short(), account.get_api_secret_short())


def create_long_client():
    return OrderCreator(account.is_test_net(), account.get_api_key_long(), account.get_api_secret_long())





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
        bot.run('rand')
    except KeyboardInterrupt:
        bot.clear_cache()
        exit(0)
        raise
    finally:
        bot.clear_cache()


