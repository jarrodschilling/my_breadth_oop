from flask_app.config.mysqlconnection import connectToMySQL
from flask import flash


class Portfolio:
    db = "my_breadth_schema"
    def __init__(self, data):
        self.id = data['id']
        self.name = data['name']
        self.user_id = data['user_id']
        self.created_at = data['created_at']
        self.updated_at = data['updated_at']
        self.user = None
        self.stocks = []



    @classmethod
    def user_portfolios(cls, data):
        query = """SELECT * FROM portfolios
                LEFT JOIN users ON users.id = portfolios.user_id
                LEFT JOIN stocks ON stocks.id = portoflios.stock_id
                WHERE users.id = %(id)s;"""
        results = connectToMySQL(cls.db).query_db(query, data)
        portfolios = []
        for row in results:
            portfolios.append(cls(row))
        print(portfolios)
        return portfolios