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

@app.route('/portfolios/new')
def new_portfolio_page():
    return render_template('create-portfolio.html')

@app.route('/portfolios/new', methods=['POST'])
def new_portfolio():
    ticker_list = request.form.getlist('tickers[]')
    tickers = []
    for ticker in ticker_list:
        if len(ticker) > 0:
            tickers.append(ticker.upper())
    print(tickers)
    stock_names = ['JPMorgan', 'Coca Cola', 'MongoDB']
    stock_ids = []
    for i in range(len(tickers)):
        #API CALL where stock_name = APICALL(tickers[i])
        # stock_name = stock_names[i]

        stock_data = {
            'name': stock_names[i],
            'ticker': tickers[i]
        }
        stock_id = Stock.check_stock(stock_data)
        stock_ids.append(stock_id)

    name_data = {
        'name': request.form['portfolio_name'],
        'user_id': session['user_id']
    }
    validate_portfolio_data = Portfolio.validate_portfolio_data(name_data)
    if validate_portfolio_data == False:
        return redirect('/portfolios/new')
    
    for i in range(len(stock_ids)):
        portfolio_data = {
            'name': request.form['portfolio_name'],
            'user_id': session['user_id'],
            'stock_id': stock_ids[i]
        }

        portfolio = Portfolio.save(portfolio_data)
    
    return redirect('/portfolios')