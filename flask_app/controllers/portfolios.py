from flask import Flask, redirect, render_template, session, request
from flask_app.models.user import User
from flask_app.models.portfolio import Portfolio
from flask_app.models.stock import Stock
from flask_app.models.portfolios_stocks import PortfoliosStocks
from flask_app import app
from flask_app.static.data import helpers
from flask import flash


@app.route('/portfolios')
def home():
    if 'user_id' not in session:
        return redirect('/')
    data = {
        'user_id': session['user_id']
    }
    portfolios = Portfolio.user_portfolios(data)
    return render_template('portfolios.html', portfolios=portfolios)

@app.route('/portfolios/new')
def new_portfolio_page():
    data = {
        'user_id': session['user_id']
    }
    if Portfolio.too_many_portfolios(data) == True:
        flash("You already have three portfolios, please delete one to add another")
        return redirect('/portfolios')
    return render_template('create-portfolio.html')

@app.route('/portfolios/new', methods=['POST'])
def new_portfolio():
    tickers = Stock.clean_symbols(request.form.getlist('tickers[]'))
    stock_names = helpers.symbol_name(tickers)
    stock_ids = Stock.get_stock_ids(tickers, stock_names)

    validate_portfolio_data = Portfolio.validate_portfolio_data(request.form)
    if validate_portfolio_data == False:
        return redirect('/portfolios/new')
    
    new_portfolio_id = Portfolio.save(request.form)
    
    for i in range(len(stock_ids)):
        join_data = {
            'portfolio_id': new_portfolio_id,
            'stock_id': stock_ids[i]
        }
        new_join = PortfoliosStocks.save(join_data)



    # GET ONE portfolio id, hardcode it to the data and THEN loop through the stock_ids
    # to Query the portfolios_stocks table

    
    return redirect('/portfolios')