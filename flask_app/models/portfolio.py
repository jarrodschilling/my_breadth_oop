from flask_app.config.mysqlconnection import connectToMySQL
from flask import Flask, session, flash
from flask_app.models import stock


class Portfolio:
    db = "my_breadth_schema"
    def __init__(self, data):
        self.id = data['id']
        self.name = data['name']
        self.user_id = data['user_id']
        self.created_at = data['created_at']
        self.updated_at = data['updated_at']
        self.stocks = []



    @classmethod
    def user_portfolios(cls, data):
        query = """SELECT * FROM portfolios
                LEFT JOIN portfolios_stocks 
                ON portfolios_stocks.portfolio_id = portfolios.id
                LEFT JOIN stocks 
                ON stocks.id = portfolios_stocks.stock_id 
                WHERE portfolios.user_id = %(user_id)s;"""
        results = connectToMySQL(cls.db).query_db(query, data)
        portfolios = {}
        for row in results:
            portfolio_id = row['portfolio_id']

            if portfolio_id not in portfolios:
                portfolios[portfolio_id] = cls(row)
            
            stock_data = {
                'id': row['stocks.id'],
                'name': row['stocks.name'],
                'ticker': row['ticker'],
                'created_at': row['stocks.created_at'],
                'updated_at': row['stocks.updated_at']
            }

            portfolios[portfolio_id].stocks.append(stock_data)

        portfolios_list = []
        # for value in portfolios.values():
        #     for i in range(len(value.stocks)):
        #         print(value.stocks[i]['ticker'])
        for value in portfolios.values():
            portfolios_list.append(value)
        print(portfolios_list)
        # for i in range(len(portfolios_list[1].stocks)):
        #     print(portfolios_list[1].stocks[i]['name'])

        return portfolios_list
    

    @classmethod
    def save(cls, data):
        portfolio_data = {
            'name': data['portfolio_name'],
            'user_id': session['user_id']
        }
        query = """INSERT INTO portfolios (name, user_id)
                VALUES (%(name)s, %(user_id)s);"""
        return connectToMySQL(cls.db).query_db(query, portfolio_data)
    

    @classmethod
    def check_name(cls, data):
        query = """SELECT name FROM portfolios WHERE user_id = %(user_id)s;"""
        results = connectToMySQL(cls.db).query_db(query, data)
        names = []
        for name in results:
            names.append(name['name'])
        return names
        
    @classmethod
    def too_many_portfolios(cls, data):
        query = """SELECT name FROM portfolios WHERE user_id = %(user_id)s GROUP BY name;"""
        results = connectToMySQL(cls.db).query_db(query, data)
        if len(results) >= 3:
            return True
    
    @staticmethod
    def validate_portfolio_data(data):
        name_data = {
            'name': data['portfolio_name'],
            'user_id': session['user_id']
        }
        is_valid = True
        if not name_data['name']:
            flash('Portfolio name cannot be blank')
            is_valid = False
        if name_data['name'] in Portfolio.check_name(name_data):
            flash('Portfolio name already exists')
            is_valid = False
        
        return is_valid
