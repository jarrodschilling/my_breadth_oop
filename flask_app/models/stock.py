from flask_app.config.mysqlconnection import connectToMySQL

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
    def add_portfolio_stocks(cls, tickers):
        for i in range(len(tickers)):
            stock_name = api_call(tickers[i])
            data = {
                'name': stock_name,
                'ticker': tickers[i]
            }
            query = """INSERT INTO stocks (name, ticker)
                    VALUES (%(name)s, %(ticker)s);"""
            results = connectToMySQL(cls.db).query_db(query, data)