from flask import Flask, redirect, render_template, session, request
from flask_app.models.user import User
from flask_app.models.portfolio import Portfolio
from flask_app import app


@app.route('/portfolios')
def home():
    if 'user_id' not in session:
        return redirect('/')
    return render_template('portfolios.html')