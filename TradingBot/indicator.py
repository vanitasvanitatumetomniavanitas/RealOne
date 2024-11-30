# indicator.py
import ta


def calculate_macd(df):
    macd = ta.trend.MACD(  #type: ignore
        close=df['close'],
        window_slow=26,
        window_fast=12,
        window_sign=9)
    df['MACD'] = macd.macd().round(2)
    return df
