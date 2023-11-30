import yfinance as yf
from flask import flash
from datetime import datetime, timedelta
import datetime


# -------------------------- Preparing stocks for database------------------------------
def symbol_check(tickers):
    data = yf.download(tickers)
    if data.empty:
        return False
    else:
        name = yf.Ticker(tickers)
        output = name.info['shortName']
        return output


def symbol_name(tickers):
    names = []
    for ticker in tickers:
        names.append((yf.Ticker(ticker).info['shortName']))
    
    return names

# --------------------------------Getting data for moving averages--------------------
# Global variables for caching data
data_cache = {}

# Make batched API CALLS
def batch_api_call(symbols):
    data = {}
    for symbol in symbols:
        data[symbol] = api_data_call(symbol)
    
    return data


# Get historical price data
def api_data_call(symbol):
    if symbol in data_cache:
        return data_cache[symbol]
    
    today = datetime.date.today()
    tomorrow = today + datetime.timedelta(days=1)
    start_date = '2022-06-01'
    end_date = tomorrow.strftime('%Y-%m-%d')

    data = yf.download(symbol, start_date, end_date)

    return data

# ------------------------------------- Moving Averages Calculations ------------------
def current_price(data, date):
    if date == "yesterday":
        closing_price = data['Close'].iloc[-2]
    elif date == "today":
        closing_price = data['Close'].iloc[-1]

    return closing_price

def ema(data, ema_period, date):
    data[f'EMA_{ema_period}'] = data['Close'].ewm(span=ema_period, adjust=False).mean()

    if date == "yesterday":
        moving_avg = data[f'EMA_{ema_period}'].iloc[-2]
    elif date == "today":
        moving_avg = data[f'EMA_{ema_period}'].iloc[-1]

    return moving_avg


# Get simple moving average using API CALL data and user inputed period
def sma(data, sma_period, date):
    data[f'SMA_{sma_period}'] = data['Close'].rolling(window=sma_period).mean()

    if date == "yesterday":
        moving_average = data[f'SMA_{sma_period}'].iloc[-2]
    elif date == "today":
        moving_average = data[f'SMA_{sma_period}'].iloc[-1]

    return moving_average


# --------------------------------- Get data for frontend display---------------------
def ma_compute_yf(portfolios, ma_avg, date):
    pass