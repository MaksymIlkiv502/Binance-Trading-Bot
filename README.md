# Binance-Trading-Bot open source 
Binance Trading bot where one of nine trades should be successful. 

Briefly speaking: to get 1 % profit using the strategy one of nine trades should be successful with a TP/SL ratio: 2:1
WARNING: use this bot with the real money on your OWN risk.

The bot is builded using python, pandas, TA lib, websockets, Telegrambot, and some others packeges. 

The instructions to the bot and the setup info you can find below. 





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

# Process of working

Each time the kendle closes the bot is checking for the BUY/SELL signal and output the result

![image](https://user-images.githubusercontent.com/109293615/194351148-098a3b4a-ce32-4d11-8e1a-98710ebedb03.png)


BUY/SELL signal received 
When the signal is received you are getting a notofication about it on your Telegram.

![image](https://user-images.githubusercontent.com/109293615/194352025-dccb1307-55d9-4cf5-933f-43ad16c2dfa1.png)

The bot also creates a buy/sell order on the close price of the last candle.
The bot is waiting for the order to be filled, and then automaticly creates a Take profit order and the stop loss. 
Every thing can be checked via logging

![Screenshot_6](https://user-images.githubusercontent.com/109293615/194351673-92d971c3-cf1e-4a71-8b4b-555d6c6b4851.jpg)



# Strategy 

The strategy is build on the MACD indicator, it gets:
BUY signal when the MACD crosses to uptrend and both MACD  < 0.
SELL signal when the MACD crosses to downtrend and both MACD > 0. 

in the particular image we can see the latest 6 trades on the 1 h timeframe that bot have done.
1 of the trades(3rd one) was unsuccessfull and 5 of them gave us 5 % of the profit. 

We options were: 

- TP - 1 %
- SL - 1 % 
- Laverage - 1

where the maximum limit of Stop loss in a ROW is 4.

![image](https://user-images.githubusercontent.com/109293615/194361339-108e5890-622d-4d94-8ca2-a0f8d45a75fc.png)



# Calculations of the position size 

The position size is calcuclated that way that every time u loose, you increase your position size in order to cover all your last stoplosses and the profit. 
In this example we will have 5 % of profit and the maximum Stop losses 5, with the TP/SL ratio of 2:1

Starting balance 100 $ 

- TP - 1 %
- SL - 0.5 % 
- Laverage - 5

For exmple if we get 4 stoplosses: our balance will be 78.7 $ and the next trade the bot will create using the margin of 33.5 and the position size will be 2632.5 $ .
That means if we get the take profit of the trade we will earn 26.3 $. And that means 78.7 + 26.3 = **105 $ **


![image](https://user-images.githubusercontent.com/109293615/194365503-cda75ebb-477d-4b1a-8eeb-5d7db2a3d85e.png)


# The maximum stop loss number 



The maximum number of stoploses can be calculated using the Strategy.xlsx file. 
If the margin gets more than 125(Binance highest margin) there will be no possible to earn all the profit that is needed to cover the previous stoplosses +profit

![image](https://user-images.githubusercontent.com/109293615/194356429-747c491d-5824-45c9-916d-dabbbe8a56ed.png)

for example: 
- TP - 1 %
- SL - 0.3 % 
- Laverage - 1

In this case you get 1 % profit.
You loose all money if bot gets 15 stoploss in a ROW. 

![image](https://user-images.githubusercontent.com/109293615/194357623-1e7b8af8-67db-44fd-94f7-8ec2c26a0c9d.png)

for example: 
- TP - 1 %
- SL - 1 % 
- Laverage - 5

In this case you get 5 % profit and the winrate >50 % because the TP/SL is 1:1.
You loose all money if bot gets 4 stoploss in a ROW.


![image](https://user-images.githubusercontent.com/109293615/194357945-b9730107-4dd3-41ee-b582-b2ef34e033b7.png)


# Changing the strategy 

The strategy can be changed by changing the IF statements. Also in the dataframe there are some other indicators that can be used: ATR, RSI, MA, MACD.

```
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
```


