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
    # Check that the user has at least 1 portfolio or redirect back to portfolios home page
    if not portfolios:
        flash("Please create a portfolio to view detail")
        return redirect('/portfolios')

    port_list = []
    for port in portfolios:
        port_list.append(helpers.ma_compute_test(port.stocks, 'today'))

    return render_template('breadth-detail.html', portfolios=portfolios, port_list=port_list)


@app.route('/portfolios/summary')
def summary():
    data = {
        'user_id': session['user_id']
    }
    portfolios = Portfolio.user_portfolios(data)
    # Check that the user has at least 1 portfolio or redirect back to portfolios home page
    if not portfolios:
        flash("Please create a portfolio to view detail")
        return redirect('/portfolios')
    # Returns a list of three portfolio dictionaries that have Keys set to each moving average and a list of Stock objects as Values
    port_list = helpers.breadth_summary_portfolios(portfolios)

    # summary_total = helpers.breadth_summary_total(portfolios)

    #NEED TO THINK THROUGH HOW TO ADD A TOTAL ROW
    return render_template('breadth-summary.html', portfolios=portfolios, port_list=port_list)



# These will require user login but ANYONE logged in can see them all
@app.route('/core/sectors/summary')
def core_sector_summary():
    pass

@app.route('/core/sectors/detail')
def core_sector_detail():
    pass

@app.route('/core/indices/summary')
def core_index_summary():
    pass

@app.route('/core/indices/detail')
def core_index_detail():
    pass