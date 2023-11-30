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
    #Before calling API, make sure Portfolio name isn't empty and isn't a copy
    validate_portfolio_data = Portfolio.validate_portfolio_data(request.form)
    if validate_portfolio_data == False:
        return redirect('/portfolios/new')
    
    #Combine tickers and stock_names with one API CALL????
    tickers = Stock.clean_symbols(request.form.getlist('tickers[]'))
    if not tickers:
        flash('New Portfolio cannot be empty')
        return redirect('/portfolios/new')
    stock_names = helpers.symbol_name(tickers)
    stock_ids = Stock.get_stock_ids(tickers, stock_names)

    new_portfolio_id = Portfolio.save(request.form)
    
    # for i in range(len(stock_ids)):
    #     join_data = {
    #         'portfolio_id': new_portfolio_id,
    #         'stock_id': stock_ids[i]
    #     }
    #     new_join = PortfoliosStocks.save(join_data)

    new_join = PortfoliosStocks.save_test(new_portfolio_id, stock_ids)

    
    return redirect('/portfolios')


@app.route('/portfolios/detail')
def breadth_detail():
    if 'user_id' not in session:
        return redirect('/')
    
    data = {
        'user_id': session['user_id']
    }
    portfolios = Portfolio.user_portfolios(data)
    # print(portfolios[0].stocks[1]['name'])
    #for port in ports iterate with f string to change variable name and port index[]
    portfolio_one_200 = helpers.ma_compute_yf(portfolios[0].stocks, 'sma200', 'today')
    print(portfolio_one_200)

    return render_template('breadth-detail.html')