# exchange_client.py
import ccxt
import sys
import logging
import pandas as pd
from datetime import timedelta


class ExchangeClient:

    def __init__(self, api_key, secret_key, passphrase, symbol, leverage):
        self.api_key = api_key
        self.secret_key = secret_key
        self.passphrase = passphrase
        self.symbol = symbol
        self.leverage = leverage
        self.exchange = ccxt.okx({
            'apiKey': self.api_key,
            'secret': self.secret_key,
            'password': self.passphrase,
            'enableRateLimit': True,
            'options': {
                'defaultType': 'swap',
            },
        })
        self.set_leverage()

    def set_leverage(self):
        try:
            self.exchange.set_leverage(self.leverage, self.symbol)
            logging.info(f"레버리지 설정 완료: {self.leverage}x")
        except Exception as e:
            logging.error(f"레버리지 설정 중 오류 발생: {e}")
            sys.exit(1)

    def get_candle_data(self, bar_interval):
        ohlcv = self.exchange.fetch_ohlcv(self.symbol,
                                          timeframe=bar_interval,
                                          limit=10000)
        df = pd.DataFrame(
            ohlcv,
            columns=['timestamp', 'open', 'high', 'low', 'close',
                     'volume'])  #type:ignore
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        df['timestamp'] = df['timestamp'] + timedelta(hours=9)
        df = df.sort_values('timestamp')
        df.reset_index(drop=True, inplace=True)
        df['close'] = df['close'].astype(float)
        return df

    def get_current_price(self):
        ticker = self.exchange.fetch_ticker(self.symbol)
        if 'last' in ticker and ticker['last'] is not None:
            return round(float(ticker['last']), 2)
        else:
            raise ValueError("현재 가격을 가져올 수 없습니다.")

    def get_available_balance(self):
        balance = self.exchange.fetch_balance()
        if 'free' in balance and 'USDT' in balance['free']:
            return balance['USDT']['free']
        else:
            raise ValueError("USDT 잔고를 가져올 수 없습니다.")
