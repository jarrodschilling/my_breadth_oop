from flask_app.config.mysqlconnection import connectToMySQL
from flask import flash
import re

EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')
class User:
    db = "my_breadth_schema"
    def __init__(self, data):
        self.id = data['id']
        self.first_name = data['first_name']
        self.last_name = data['last_name']
        self.username = data['username']
        self.password = data['password']
        self.created_at = data['created_at']
        self.updated_at = data['updated_at']
        self.portfolios = []

    @classmethod
    def save(cls, data):
        query = """INSERT INTO users (first_name, last_name, username, password)
                VALUES (%(first_name)s, %(last_name)s, %(username)s, %(password)s);"""
        return connectToMySQL(cls.db).query_db(query, data)
    
    @classmethod
    def get_one(cls, data):
        query = """SELECT * FROM users WHERE username = %(username)s;"""
        results = connectToMySQL(cls.db).query_db(query, data)
        print(results)
        if len(results) < 1:
            return False
        return cls(results[0])
    
    @classmethod
    def get_all(cls):
        query = "SELECT * FROM users;"
        results = connectToMySQL(cls.db).query_db(query)
        users = []
        for row in results:
            users.append(cls(row))
        return(users)

    @staticmethod
    def validate_reg(user):
        is_valid = True
        if len(user['first_name']) < 1:
            flash("First name cannot be blank")
            is_valid = False
        if len(user['last_name']) < 1:
            flash("Last name cannot be blank")
            is_valid = False
        if len(user['username']) < 8:
            flash("Username must be at least 8 character long")
            is_valid = False
        if len(user['password']) < 8:
            flash("Password must be at least 8 character long")
            is_valid = False
        if user['password'] != user['confirmpassword']:
            flash("Passwords must match")
            is_valid = False
        if any(char.isdigit() for char in user['password']) == False:
            flash("Password must contain a number")
            is_valid = False
        if any(char.isalpha() for char in user['password']) == False:
            flash("Passwords must contain a letter")
            is_valid = False
        if any(char for char in user['password'] if not char.isalnum()) == False:
            flash("Passwords must contain a special character")
            is_valid = False
        # check to see if username already exists
        users = User.get_all()
        usernames = []
        for row in users:
            usernames.append(row.username)
        if user['username'] in usernames:
            flash("Username already exists")
            is_valid = False

        return is_valid