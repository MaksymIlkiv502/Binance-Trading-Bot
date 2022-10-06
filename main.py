import pprint
import math
import time
import ord
import websocket
import json
import talib
import numpy
import pandas as pd
import telebot
import datetime
from binance.client import *
import logging

TICKER = 'btcusdt'
RSI_PERIOD = 14
MA_PERIOD = 9
ATR_PERIOD = 14
TREND_FLOAT = 1
RSI_DIFFERENCE_FLOAT = 0.3
TREND_SPECTATING_LENGTH = 20
TP_const = 0.4
SL_const = 0.3
START_MARGIN = 5

logging.basicConfig(filename='logs.log', level=logging.INFO, format='%(asctime)s:%(message)s')
pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
pd.options.mode.chained_assignment = None
bot = telebot.TeleBot('5256276497:AAGkHGl-R8_K3s8jCXvTq6V5XLaj2cKZKeU')
bot.config['api_key'] = '5256276497:AAGkHGl-R8_K3s8jCXvTq6V5XLaj2cKZKeU'

client = Client('Binance API',
                'Binance API KEY')

url = 'wss://fstream.binance.com:443/ws/' + TICKER + '@kline_1m'

closes = []
ETHTREND = False

data = client.futures_klines(symbol=TICKER.upper(), interval=Client.KLINE_INTERVAL_1MINUTE, limit=1500)
cut_data = []
for i in data:
    i[0] = datetime.datetime.fromtimestamp(int(i[0]) / 1000).strftime('%B %#d, %Y %H:%M:%S')
    cut_data.append(i[0:6])
df = pd.DataFrame(cut_data[:-1], columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
print(df.tail())


def on_open(ws):
    print('Opened connection')
    try:
        q = 1
        # message = bot.send_message('459862465', 'The bot has opened the connection Pycharm')
    except Exception as err:
        print(err)


def on_close(ws):
    print('Connection closed')
    bot.send_message('459862465', 'The bot has closed the connection')




def mytrim(float_number, length=3):
    if isinstance(float_number, float):
        num = str(float_number)
        digits = num.split(".")
        return_str = digits[0] + "." + str(digits[1])[:length]

        return return_str
    else:
        return float_number


def get_balance(array, asset):
    for i in array:
        if i['asset'] == asset:
            return i['balance']


def get_position(array, ticker):
    for i in array['positions']:
        if i['symbol'] == ticker:
            return [i['entryPrice'], i['positionAmt'], i['unrealizedProfit']]


START = True
IN_POSITION = False
start_balance = get_balance(client.futures_account_balance(), 'USDT')
gain_balance = 0
is_continuing = input("Is the bot staring from first trade? y/n")
if is_continuing == 'y':
    gain_balance = float(start_balance) * START_MARGIN / 100 + float(start_balance)
elif is_continuing == 'n':
    gain_balance = float(input('Please enter the gain balance'))
    START = False

logging.info('Gain balance is set to:' + str(gain_balance))

def create_trade(entry, side):
    global START_MARGIN
    global TP_const
    global SL_const
    global START
    global gain_balance
    global start_balance
    USDT_balance = get_balance(client.futures_account_balance(), 'USDT')
    quantity = 0
    print(START)
    try:
        if START == True:
            quantity = mytrim(float(start_balance) * START_MARGIN / float(entry))
            logging.info("The START is TRUE. The QTY is set to : " + str(quantity))
            print(quantity)
        elif START == False:
            print((float(gain_balance) - float(USDT_balance)) * 100 / TP_const / float(entry))
            logging.info('Gain bal : ' + str(gain_balance) + 'USDT Bal : ' + str(USDT_balance) + 'TP_const : ' + str(TP_const) + 'Entry : ' + str(entry))
            quantity = mytrim((float(gain_balance) - float(USDT_balance)) * 100 / TP_const / float(entry))
            logging.info("The START is FALSE. The QTY is set to : " + str(quantity))
            print(quantity)
    except Exception as err:
        print(err)
    logging.info('The order QTY is set to: ' + str(quantity))
    order = client.futures_create_order(symbol='BTCUSDT', side=side, quantity=str(quantity), type='LIMIT', price=entry, timeInForce='GTC')
    logging.info('The order has been created. Order id:  ' + str(order['orderId']))
    time.sleep(5)

    while True:
        order = client.futures_get_order(symbol='BTCUSDT', orderId=order['orderId'])
        logging.info("Cheking the order status")
        if order['status'] == 'FILLED' and order['side'] == 'BUY':
            logging.info('The order has been filled. Order id:  ' + str(order['orderId']))
            tp_price = mytrim(float(entry) + float(entry) * TP_const / 100, 1)
            sl_price = mytrim(float(entry) - float(entry) * SL_const / 100, 1)
            logging.info("Take profit price is " + tp_price + '||| Stop loss price is ' + sl_price)
            takeprofit = client.futures_create_order(symbol='BTCUSDT', side='SELL', quantity=order['origQty'], type='LIMIT', price=str(tp_price), timeInForce='GTC')
            logging.info('The TP order has been created. Order id:  ' + str(takeprofit['orderId']))
            stoploss = client.futures_create_order(symbol='BTCUSDT', side='SELL', quantity=order['origQty'], type='STOP_MARKET', stopPrice=str(sl_price), timeInForce='GTC')
            logging.info('The SL order has been created. Order id:  ' + str(stoploss['orderId']))
            break
        elif order['status'] == 'FILLED' and order['side'] == 'SELL':
            logging.info('The order has been filled. Order id:  ' + str(order['orderId']))
            tp_price = mytrim(float(entry) - float(entry) * TP_const / 100, 1)
            sl_price = mytrim(float(entry) + float(entry) * SL_const / 100, 1)
            logging.info("Take profit price is " + tp_price + '||| Stop loss price is ' + sl_price)
            takeprofit = client.futures_create_order(symbol='BTCUSDT', side='BUY', quantity=order['origQty'], type='LIMIT', price=str(tp_price), timeInForce='GTC')
            logging.info('The TP order has been created. Order id:  ' + str(takeprofit['orderId']))
            stoploss = client.futures_create_order(symbol='BTCUSDT', side='BUY', quantity=order['origQty'], type='STOP_MARKET', stopPrice=str(sl_price), timeInForce='GTC')
            logging.info('The SL order has been created. Order id:  ' + str(stoploss['orderId']))
            break
        elif order['status'] == 'CANCELED':
            logging.info('The order has been cancelled. Order id:  ' + str(order['orderId']))
            break
        else:
            logging.info('The order is not filled. Sleep. ')
            time.sleep(20)


def on_message(ws, message):
    global closes
    global START
    global start_balance
    global gain_balance
    global IN_POSITION

    json_message = json.loads(message)
    # pprint.pprint(json_message)
    candle = json_message['k']
    is_candle_closed = candle['x']
    close = candle['c']



    if is_candle_closed:
        try:
            print('Candle closed at {}'.format(close))
            time_of_candle = datetime.datetime.fromtimestamp(int(candle['T']) / 1000).strftime('%B %#d, %Y %H:%M:%S')
            df.loc[df.shape[0]] = [time_of_candle, candle['o'], candle['h'], candle['l'], candle['c'], candle['v']]

            logging.info('Getting the USDT balance')
            USDT_balance = get_balance(client.futures_account_balance(), 'USDT')
            logging.info('USDT balance is: ' + str(USDT_balance))
            info = client.futures_account()
            opened_positions = get_position(info, 'BTCUSDT')
            logging.info('Opened positions: ' + str(opened_positions))
            orders = client.futures_get_open_orders(symbol='BTCUSDT')
            logging.info('Opened orders: ' + str(orders))

            if float(opened_positions[0]) == 0 and len(orders) == 0:
                print("We can do a trade")
                if USDT_balance > start_balance:
                    start_balance = USDT_balance
                    gain_balance = float(USDT_balance) * START_MARGIN / 100 + float(USDT_balance)
                elif USDT_balance < start_balance:
                    START = False
            elif float(opened_positions[0]) != 0:
                bot.send_message('459862465', 'We have an opened position')
            elif len(orders) != 0:
                bot.send_message('459862465', 'We have an opened order')

            if df.count()['timestamp'] > RSI_PERIOD:
                np_close = numpy.array([float(i) for i in (df['close'].to_list())])
                np_high = numpy.array([float(i) for i in (df['high'].to_list())])
                np_low = numpy.array([float(i) for i in (df['low'].to_list())])

                rsi = talib.RSI(np_close, RSI_PERIOD)
                ma = talib.MA(np_close, MA_PERIOD)
                atr = talib.ATR(np_high, np_low, np_close, ATR_PERIOD)
                macd = talib.MACD(np_close, fastperiod=12, slowperiod=26, signalperiod=9)
                main_dataframe = df.assign(Rsi=rsi.tolist(), MA=ma.tolist(), ATR=atr.tolist(), MACD=macd[0].tolist(),
                                           MACD1=macd[1].tolist(), Signal=macd[2].tolist())
                df_sorted = main_dataframe.tail(TREND_SPECTATING_LENGTH)

                print(main_dataframe.tail(TREND_SPECTATING_LENGTH))
                try:
                    if float(df_sorted['Signal'].tolist()[-1]) >= 0 and float(df_sorted['Signal'].tolist()[-2]) < 0 and float(df_sorted['MACD'].tolist()[-1]) < 0 and float(df_sorted['MACD1'].tolist()[-1]) < 0:
                        logging.info('The trend changed to the uptrend.')
                        if float(opened_positions[0]) == 0 and len(orders) == 0:
                            create_trade(df_sorted['close'].tolist()[-1], 'BUY')
                            logging.info('We have received the buy signal. Creating an order with price: ' + str(df_sorted['close'].tolist()[-1]))
                            message = bot.send_message('459862465', 'We have received the buy signal. Creating an order with price: ' + str(df_sorted['close'].tolist()[-1]))
                    elif float(df_sorted['Signal'].tolist()[-1]) <= 0 and float(df_sorted['Signal'].tolist()[-2]) > 0 and float(df_sorted['MACD'].tolist()[-1]) > 0 and float(df_sorted['MACD1'].tolist()[-1]) > 0:
                        logging.info('The trend changed to the uptrend.')
                        if float(opened_positions[0]) == 0 and len(orders) == 0:
                            logging.info('We have received the sell signal. Creating an order with price: ' + str(df_sorted['close'].tolist()[-1]))
                            message = bot.send_message('459862465', 'We have received the sell signal. Creating an order with price: ' + str(df_sorted['close'].tolist()[-1]))
                            create_trade(df_sorted['close'].tolist()[-1], 'SELL')

                    else:
                        print('No trade signal')
                except Exception as err:
                    print(err)





        except Exception as err:
            print(err)


ws = websocket.WebSocketApp(url, on_open=on_open, on_close=on_close, on_message=on_message)
ws.run_forever()

