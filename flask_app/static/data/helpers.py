import yfinance as yf
from flask import flash
from datetime import datetime, timedelta
import datetime
from flask_app.models import stock as stk


# -------------------------- Preparing stocks for database ------------------------------
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

# -------------------------------- Getting data for moving averages --------------------
# Global dictionary for caching data
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
    data_cache[symbol] = data
    return data

# ------------------------------------- Moving Averages Calculations ------------------
def current_price(data, date):
    if date == "yesterday":
        closing_price = data['Close'].iloc[-2]
    elif date == "today":
        closing_price = data['Close'].iloc[-1]

    return closing_price


# Get EMA using API CALL data and user inputed period
def ema(data, ema_period, date):
    # Calculate EMA data
    ema_data = data['Close'].ewm(span=ema_period, adjust=False).mean()

    # Grab row based on date
    if date == "yesterday":
        moving_avg = ema_data.iloc[-2]
    elif date == "today":
        moving_avg = ema_data.iloc[-1]

    return moving_avg


# Get simple moving average using API CALL data and user inputed period
def sma(data, sma_period, date):
    # Calculate SMA data
    sma_data = data['Close'].rolling(window=sma_period).mean()

    # Grab row based on date
    if date == "yesterday":
        moving_average = sma_data.iloc[-2]
    elif date == "today":
        moving_average = sma_data.iloc[-1]

    return moving_average


# --------------------------------- Get data for frontend display---------------------

def ma_compute_test(stocks, date):
    stocks_lists = {}
    list_20 = []
    list_50 = []
    list_200 = []
    list_under = []

    symbols_to_fetch = set(stock['ticker'] for stock in stocks)

    data = batch_api_call(symbols_to_fetch)

    for stock in stocks:
        # stock_name = stock['name']
        stock_ticker = stock['ticker']
        current = current_price(data[stock_ticker], date)
        ema20 = ema(data[stock_ticker], 20, date)
        sma50 = sma(data[stock_ticker], 50, date)
        sma200 = sma(data[stock_ticker], 200, date)

        if current > ema20 and ema20 > sma50 and sma50 > sma200:
            list_20.append(stk.Stock.get_stock_by_ticker(stock_ticker))

        if current > sma50 and sma50 > sma200:
            list_50.append(stk.Stock.get_stock_by_ticker(stock_ticker))

        if current > sma200:
            list_200.append(stk.Stock.get_stock_by_ticker(stock_ticker))

        if current < sma200:
            list_under.append(stk.Stock.get_stock_by_ticker(stock_ticker))
    
    stocks_lists['ema20'] = list_20
    stocks_lists['sma50'] = list_50
    stocks_lists['sma200'] = list_200
    stocks_lists['under'] = list_under

    return stocks_lists


# Create list of dictionaries for the Breadth Summary Page
def breadth_summary_portfolios(portfolios, date):
    port_list = []
    for port in portfolios:
        stocks_above = (ma_compute_test(port.stocks, date))
        summary_percent = {}
        summary_percent['ema20'] = "{:.2f}%".format(100 * (len(stocks_above['ema20']) / len(port.stocks)))
        summary_percent['sma50'] = "{:.2f}%".format(100 * (len(stocks_above['sma50']) / len(port.stocks)))
        summary_percent['sma200'] = "{:.2f}%".format(100 * (len(stocks_above['sma200']) / len(port.stocks)))
        summary_percent['under'] = "{:.2f}%".format(100 * (len(stocks_above['under']) / len(port.stocks)))
        port_list.append(summary_percent)

    return port_list

def breadth_summary_total(portfolios, date):
    # Create dictionary containing the stocks in each portfolio for each category
    summary_percent = {}
    for i in range(0, len(portfolios)):
        stocks_above = ma_compute_test(portfolios[i].stocks, date)
        summary_percent[f'port{i}_ema20'] = stocks_above['ema20']
        summary_percent[f'port{i}_sma50'] = stocks_above['sma50']
        summary_percent[f'port{i}_sma200'] = stocks_above['sma200']
        summary_percent[f'port{i}_under'] = stocks_above['under']
    
    # Get combined number of stocks from all portfolios
    total_stock_port1 = 0
    total_stock_port2 = 0
    total_stock_port3 = 0
    if len(portfolios) > 0:
        total_stock_port1 = len(portfolios[0].stocks)
    if len(portfolios) > 1:
        total_stock_port2 = len(portfolios[1].stocks)
    if len(portfolios) > 2:
        total_stock_port3 = len(portfolios[2].stocks)
    total_stock_count = total_stock_port1 + total_stock_port2 + total_stock_port3
    
    # Create a dictionary that has the total(all 3 portfolios) number of stocks for each categroy
    summary_total = {}
    summary_total['ema20'] = 0
    summary_total['sma50'] = 0
    summary_total['sma200'] = 0
    summary_total['under'] = 0
    for i in range(0, len(portfolios)):
        summary_total['ema20'] += len(summary_percent[f'port{i}_ema20'])
        summary_total['sma50'] += len(summary_percent[f'port{i}_sma50'])
        summary_total['sma200'] += len(summary_percent[f'port{i}_sma200'])
        summary_total['under'] += len(summary_percent[f'port{i}_under'])

    # Divide each category by total amount of stocks in all the portfolios and format for frontend
    summary_total['ema20'] = "{:.2f}%".format(100 * (summary_total['ema20'] / total_stock_count))
    summary_total['sma50'] = "{:.2f}%".format(100 * (summary_total['sma50'] / total_stock_count))
    summary_total['sma200'] = "{:.2f}%".format(100 * (summary_total['sma200'] / total_stock_count))
    summary_total['under'] = "{:.2f}%".format(100 * (summary_total['under'] / total_stock_count))

    return summary_total

# def ma_compute_yf(stocks, ma_avg, date):
#     stocks_list = []

#     symbols_to_fetch = set(stock['ticker'] for stock in stocks)

#     data = batch_api_call(symbols_to_fetch)

#     for stock in stocks:
#         stock_name = stock['name']
#         stock_ticker = stock['ticker']
#         current = current_price(data[stock_ticker], date)
#         ema20 = ema(data[stock_ticker], 20, date)
#         sma50 = sma(data[stock_ticker], 50, date)
#         sma200 = sma(data[stock_ticker], 200, date)

#         if (ma_avg == "ema20") and current > ema20 and ema20 > sma50 and sma50 > sma200:
#             stocks_list.append(stk.Stock.get_stock_by_ticker(stock_ticker))

#         elif (ma_avg == "sma50") and current > sma50 and sma50 > sma200:
#             stocks_list.append(stk.Stock.get_stock_by_ticker(stock_ticker))

#         elif (ma_avg == "sma200") and current > sma200:
#             stocks_list.append(stk.Stock.get_stock_by_ticker(stock_ticker))

#         elif (ma_avg == "below") and current < sma200:
#             stocks_list.append(stk.Stock.get_stock_by_ticker(stock_ticker))
    

#     return stocks_list