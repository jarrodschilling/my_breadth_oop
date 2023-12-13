from flask_app.config.mysqlconnection import connectToMySQL
from flask import flash
from flask_app.static.data import helpers


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
    def get_stock_by_ticker(cls, data):
        stock_data = {
            'ticker': data
        }
        query = """SELECT * FROM stocks WHERE ticker = %(ticker)s;"""
        results = connectToMySQL(cls.db).query_db(query, stock_data)
        if not results:
            return False
        return cls(results[0])

    @classmethod
    def grab_id(cls, data):
        query = """SELECT * FROM stocks WHERE ticker = %(ticker)s;"""
        results = connectToMySQL(cls.db).query_db(query, data)
        if len(results) < 1:
            return False
        return cls(results[0]).id

    @staticmethod
    def clean_symbols(data):
        ticker_list = data
        tickers = []
        for ticker in ticker_list:
            if len(ticker) > 0:
                if helpers.symbol_check(ticker) != False:
                    tickers.append(ticker.upper())
        
        return tickers
    
    @staticmethod
    def get_stock_ids(tickers, stock_names):
        stock_ids = []
        for i in range(len(tickers)):
            stock_data = {
                'name': stock_names[i],
                'ticker': tickers[i]
            }
            
            stock_id = Stock.check_stock(stock_data)
            stock_ids.append(stock_id)

        return stock_ids
    
    
