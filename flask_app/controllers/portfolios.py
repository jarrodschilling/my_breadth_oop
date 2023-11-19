from flask import Flask, redirect, render_template, session, request
from flask_app.models.user import User
from flask_app.models.portfolio import Portfolio
from flask_app.models.stock import Stock
from flask_app import app
from flask_app.static.data.data import stocks as api_call


@app.route('/portfolios')
def home():
    if 'user_id' not in session:
        return redirect('/')
    data = {
        'id': session['user_id']
    }
    portfolios = Portfolio.user_portfolios(data)
    return render_template('portfolios.html', portfolios=portfolios)


@app.route('/portfolios/new', methods=['POST'])
def new_portfolio():
    # tickers = request.form.getlist('tickers')
    tickers = ['JPM', 'MDB', 'DASH']
    # Check if stock exists in stocks table
    # If not, add stock to stock table
    # Retrieve stocks.id for every stock being added to the portfolio
    # P
    stock_ids = [1, 2, 3, 4]
    for i in range(len(stock_ids)):

        portfolio_data = {
            'name': request.form['portfolio_name'],
            'user_id': session['user_id'],
            'stock_id': stock_ids[i]
        }