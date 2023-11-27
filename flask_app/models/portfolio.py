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



    @classmethod
    def user_portfolios(cls, data):
        query = """SELECT * FROM portfolios
                WHERE user_id = %(id)s;"""
        results = connectToMySQL(cls.db).query_db(query, data)
        portfolios = []
        for row in results:
            portfolios.append(cls(row))
        # print(portfolios)
        return portfolios
    

    @classmethod
    def save(cls, data):
        query = """INSERT INTO portfolios (name, user_id)
                VALUES (%(name)s, %(user_id)s);"""
        return connectToMySQL(cls.db).query_db(query, data)
    

    @classmethod
    def check_name(cls, data):
        query = """SELECT name FROM portfolios WHERE user_id = %(user_id)s;"""
        results = connectToMySQL(cls.db).query_db(query, data)
        names = []
        for name in results:
            names.append(name['name'])
        return names
        
    @staticmethod
    def validate_portfolio_data(data):
        is_valid = True
        if data['name'] in Portfolio.check_name(data):
            flash('Portfolio Name already exists')
            is_valid = False
        
        return is_valid
