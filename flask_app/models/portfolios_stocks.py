from flask_app.config.mysqlconnection import connectToMySQL
from flask_app.models import stock
from flask_app.models import portfolio
from flask import flash

class PortfoliosStocks:
    db = "my_breadth_schema"
    def __init__(self, data):
        self.portfolio_id = data['portfolio_id']
        self.stock_id = data['stock_id']


    
    @classmethod
    def save_test(cls, portfolio_id, stock_ids):
        for i in range(len(stock_ids)):
            data = {
                "portfolio_id": portfolio_id,
                "stock_id": stock_ids[i]
            }
            query = """INSERT INTO portfolios_stocks (portfolio_id, stock_id)
                    VALUES (%(portfolio_id)s, %(stock_id)s);"""
            results = connectToMySQL(cls.db).query_db(query, data)
        pass
        
    @classmethod
    def save(cls, data):
        query = """INSERT INTO portfolios_stocks (portfolio_id, stock_id)
                VALUES (%(portfolio_id)s, %(stock_id)s);"""
        return connectToMySQL(cls.db).query_db(query, data)
    

    @classmethod
    def get_stocks_in_portfolio(cls, data):
        portfolio_data = {
            'portfolio_id': data
        }
        query = """SELECT * FROM portfolios_stocks
                JOIN stocks ON stocks.id = portfolios_stocks.stock_id
                WHERE portfolios_stocks.portfolio_id = %(portfolio_id)s;"""
        results = connectToMySQL(cls.db).query_db(query, portfolio_data)
        stocks = []
        if results:
            for row in results:
                stock_data = {
                    'id': row['id'],
                    'name': row['name'],
                    'ticker': row['ticker'],
                    'created_at': row['created_at'],
                    'updated_at': row['updated_at']
                }
                stocks.append(stock.Stock(stock_data))
        
        return stocks
    

    @classmethod
    def delete_stocks(cls, portfolio_id, stock_ids):
        for i in range(len(stock_ids)):
            data = {
                "portfolio_id": portfolio_id,
                "stock_id": stock_ids[i]
            }

            query = """DELETE FROM portfolios_stocks 
                    WHERE portfolio_id = %(portfolio_id)s
                    AND stock_id = %(stock_id)s;"""
            results = connectToMySQL(cls.db).query_db(query, data)
        
        pass