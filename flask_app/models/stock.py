from flask_app.config.mysqlconnection import connectToMySQL
from flask import flash
import yfinance as yf

class Stock:
    db = "my_breadth_schema"
    def __init__(self, data):
        self.id = data['id']
        self.name = data['name']
        self.ticker = data['ticker']
        self.created_at = data['created_at']
        self.updated_at = data['updated_at']


    @classmethod
    def add_stock(cls, data):
        query = """INSERT INTO stocks (name, ticker)
                VALUES (%(name)s, %(ticker)s);"""
        return connectToMySQL(cls.db).query_db(query, data)
    
    @classmethod
    def check_stock(cls, data):
        query = """SELECT ticker FROM stocks;"""
        results = connectToMySQL(cls.db).query_db(query, data)
        tickers = []
        for ticker in results:
            tickers.append(ticker['ticker'])
        if data['ticker'] in tickers:
            return Stock.grab_id(data)
        else:
            return Stock.add_stock(data)


    @classmethod
    def grab_id(cls, data):
        query = """SELECT * FROM stocks WHERE ticker = %(ticker)s;"""
        results = connectToMySQL(cls.db).query_db(query, data)
        if len(results) < 1:
            return False
        return cls(results[0]).id

    @staticmethod
    def symbol_check(data):
        ticker_data = yf.download(data)
        if ticker_data.empty:
            return False
        else:
            name = yf.Ticker(data)
            output = name.info['shortName']
            return output

    @staticmethod
    def validate_stock_data(data):
        is_valid = True
        pass