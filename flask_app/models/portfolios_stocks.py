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
    def save(cls, data):
        query = """INSERT INTO portfolios_stocks (portfolio_id, stock_id)
                VALUES (%(portfolio_id)s, %(stock_id)s);"""
        return connectToMySQL(cls.db).query_db(query, data)