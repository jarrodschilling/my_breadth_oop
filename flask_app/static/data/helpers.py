import yfinance as yf
from flask import flash


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