# Binance-Trading-Bot
Binance Trading bot where one of five trades should be successful. 


# Setup 

- pip install all the packages 
```
import websocket
import json
import talib
import numpy
import pandas as pd
import telebot
import datetime
from binance.client import *
import logging
```

- change the Telegram and Binance connection APIs
```
bot = telebot.TeleBot('5256285497:AAGkHGl-R8_K3s8jCXsdfdsfTq66VXLaj2cKZKeU')
bot.config['api_key'] = '5254286497:AAGkHGl-R8_K3s8jCXvTqsdfsdVXLaj2cKZKeU'

client = Client('sQ9R5olUHeU9lP5GYiRRRi8CMc8Twc1Cndfg1UkykmiI9X9bWkYe3AZh1ymMQWc1rlY',
                'rBgLjtkHlnTBw6i0LbivJyj09RBdfgol9QClIHnAnwRiXxyCNbE2ZkTajtUlb3UiAVu')
```

- Set kline interval

```
url = 'wss://fstream.binance.com:443/ws/' + TICKER + '@kline_1m'
data = client.futures_klines(symbol=TICKER.upper(), interval=Client.KLINE_INTERVAL_1MINUTE, limit=1500)
```
- Setting ticker / periods of RSI, MA, ART indicators / Take profit and Stoploss in percent % / Start margin 

```
TICKER = 'btcusdt'
RSI_PERIOD = 14
MA_PERIOD = 9
ATR_PERIOD = 14
TREND_FLOAT = 1
RSI_DIFFERENCE_FLOAT = 0.3
TREND_SPECTATING_LENGTH = 20
TP_const = 0.6
SL_const = 0.3
START_MARGIN = 3
```

# Starting the bot 

-main.py

![image](https://user-images.githubusercontent.com/109293615/194344761-b7d49914-6110-4bc5-98d4-153b4804072c.png)

If you are starting the bot first time, send Y if no press send N and enter the gain ballance: balance of the first trade + margin * Take profit

![image](https://user-images.githubusercontent.com/109293615/194345374-d1e48728-6d6a-4ff9-8c19-c1934c8e298d.png)

Each time the kendle closes the bot is checking for the BUY/SELL signal and output the result

![image](https://user-images.githubusercontent.com/109293615/194351148-098a3b4a-ce32-4d11-8e1a-98710ebedb03.png)


BUY/SELL signal received 
When the signal is received you are getting a notofication about it on your Telegram.

![image](https://user-images.githubusercontent.com/109293615/194352025-dccb1307-55d9-4cf5-933f-43ad16c2dfa1.png)

The bot also creates a buy/sell order on the close price of the last candle.
The bot is waiting for the order to be filled, and then automaticly creates a Take profit order and the stop loss. 
Every thing can be checked via logging

![Screenshot_6](https://user-images.githubusercontent.com/109293615/194351673-92d971c3-cf1e-4a71-8b4b-555d6c6b4851.jpg)


