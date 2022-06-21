# What do we need:
# 1 Binance API or a client connected to a websocket instead of a HTTP connection
# 2 Apply the RSI indicator

import websocket, json, pprint, talib, numpy
import config
from binance.client import Client
from binance.enums import *


# after the ws/ we need to provide a symbol that we want to trade with, then candlestick lines, and finally the time frame
SOCKET = "wss://stream.binance.com:9443/ws/ethusdt/@kline_1m"

# RSI configuration
RSI_PERIOD = 14
RSI_OVERBOUGHT = 70
RSI_OVERSOLD = 30
# pair you want to trade with
TRADE_SYMBOL = "ETHUSD"

# quantity of the pair you want to buy in this case 0.05 eth
TRADE_QUANTITY = 0.05

closes = []
in_position = False

# tld stands for the country prefix, so set your own, in my case is Germany
client = Client(config.APY_KEY, config.API_SECRET, tld="de")


def order(symbol, quantity, side, order_type=ORDER_TYPE_MARKET):
    try:
        print("sending order")
        order = client.create_order(
            symbol=symbol, side=side, type=ORDER_TYPE_MARKET, quantity=quantity
        )
        print(order)
    except Exception as e:
        return False

    return True


def on_open(ws):
    print("opened connection")


def on_close(ws):
    print("closed connection")


def on_message(ws, message):
    global closes
    print("recieved message")
    json_message = json.loads(message)
    pprint.pprint(json_message)

    candle = message["k"]

    is_candle_closed = candle["x"]
    close = candle["c"]

    if is_candle_closed:
        print("candle closed at {}", format(close))
        closes.append(float(close))
        print("closes")
        print(closes)

        if len(closes > RSI_PERIOD):
            np_closes = numpy.array(closes)
            rsi = talib.RSI(np_closes, RSI_PERIOD)
            print("All rsi calculates so far:")
            print(rsi)
            last_rsi = rsi[-1]
            print("the current rsi is ()".format(last_rsi))

            if last_rsi > RSI_OVERBOUGHT:
                if in_position:
                    print("sellllllllll!!!")
                    # all the binance sell logic
                    order_succeded = order(TRADE_SYMBOL, TRADE_QUANTITY, SIDE_SELL)
                    if order_succeded:
                        in_position = False
                        print("Order succeded")
                else:
                    print(
                        "Even if it is overbought, we dont own any. Nothing to do here!"
                    )

            if last_rsi < RSI_OVERSOLD:
                if in_position:
                    print("It is oversold but you alredy own it, nothing to do")
                else:
                    print("Oversold! buybuybuybuy!")
                    # binance buy order logic
                    order_succeded = order(TRADE_SYMBOL, TRADE_QUANTITY, SIDE_BUY)
                    if order_succeded:
                        in_position = True


ws = websocket.WebSocketApp(
    SOCKET, on_open=on_open, on_close=on_close, on_message=on_message
)
ws.run_forever()
