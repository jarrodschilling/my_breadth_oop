from flask_app.models.portfolio import Portfolio
from flask_app.models.stock import Stock
from flask_app.static.data import helpers
from flask_app import app
import yfinance as yf
from flask_app.static.data.data import indices, sectors, industries, sub_sectors

ticker1 = 'JPM'
ticker2 = 'QQQ'
ticker3 = 'MSFT'
tickers = [ticker1, ticker2, ticker3]

for ticker in tickers:
    name = yf.Ticker(ticker).info['shortName']
    data = {
        'name': name,
        'ticker': ticker
    }
    save_stock = Stock.add_stock(data)
