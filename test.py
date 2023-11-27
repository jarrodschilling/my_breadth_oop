from flask_app.models.portfolio import Portfolio
from flask_app.models.stock import Stock
from flask_app import app
import yfinance as yf

tickers = ['GS', 'MDB', 'TOL']

for ticker in tickers:
    print(yf.Ticker(ticker).info['shortName'])
