from flask import Flask, redirect, render_template, session, request
from flask_app.models.user import User
from flask_app.models.portfolio import Portfolio
from flask_app.models.stock import Stock
from flask_app.models.portfolios_stocks import PortfoliosStocks
from flask_app import app
from flask_app.static.data import helpers
from flask import flash


#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
# -----------------------------------------------------------------------------------------------
# ------------USER PORTFOLIOS CREATION + EDITING ROUTES
# -----------------------------------------------------------------------------------------------
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>


# ------------------- LIST OF ALL PORTFOLIOS CURRENTLY CREATED -------------------------
@app.route('/portfolios')
def home():
    if 'user_id' not in session:
        return redirect('/')
    data = {
        'user_id': session['user_id']
    }
    portfolios = Portfolio.user_portfolios(data)

    return render_template('portfolios.html', portfolios=portfolios)


# ------------------- CREATE NEW PORTFOLIO ----------------------------------------------
@app.route('/portfolios/new')
def new_portfolio_page():
    if 'user_id' not in session:
        return redirect('/')
    data = {
        'user_id': session['user_id']
    }
    if Portfolio.too_many_portfolios(data) == True:
        flash("You already have three portfolios, please delete one to add another")
        return redirect('/portfolios')
    return render_template('create-portfolio.html')


@app.route('/portfolios/new', methods=['POST'])
def new_portfolio():
    if 'user_id' not in session:
        return redirect('/')
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


# ------------------- ADD STOCKS TO EXISTING PORTFOLIO -------------------------------
@app.route('/add-stock/<int:id>')
def add_stock_page(id):
    if 'user_id' not in session:
        return redirect('/')
    portfolio = Portfolio.get_portfolio_by_id(id)
    print(portfolio)
    return render_template('add-stock.html', portfolio=portfolio)


@app.route('/add-stock', methods=['POST'])
def add_stock():
    if 'user_id' not in session:
        return redirect('/')
    #Combine tickers and stock_names with one API CALL????
    tickers = Stock.clean_symbols(request.form.getlist('tickers[]'))
    # if not tickers:
    #     flash('New Portfolio cannot be empty')
    #     return redirect('/portfolios/new')
    stock_names = helpers.symbol_name(tickers)
    stock_ids = Stock.get_stock_ids(tickers, stock_names)

    #Grab portfolio id from hidden form input
    portfolio_id = request.form['portfolio_id']

    #Add stocks to join table
    PortfoliosStocks.save_test(portfolio_id, stock_ids)

    return redirect('/portfolios')


# ------------------- DELETE STOCKS FROM EXISTING PORTFOLIO -------------------------------
@app.route('/delete-stock/<int:id>')
def delete_stock_page(id):
    if 'user_id' not in session:
        return redirect('/')
    portfolio = Portfolio.get_portfolio_by_id(id)
    stocks = PortfoliosStocks.get_stocks_in_portfolio(id)

    return render_template('delete-stock.html', portfolio=portfolio, stocks=stocks)


@app.route('/delete-stock', methods=['POST'])
def delete_stock():
    if 'user_id' not in session:
        return redirect('/')
    stock_ids = []
    tickers = request.form.getlist('tickers[]')
    for ticker in tickers:
        data = {
            'ticker': ticker
        }
        stock_id = Stock.grab_id(data)
        stock_ids.append(stock_id)
    
    #Grab portfolio id from hidden form input
    portfolio_id = request.form['portfolio_id']

    #Delete stocks from join table
    PortfoliosStocks.delete_stocks(portfolio_id, stock_ids)

    return redirect('/portfolios')


# ------------------- DELETE PORTFOLIO -------------------------------
@app.route('/portfolios/delete/<int:id>')
def delete_portfolio_page(id):
    if 'user_id' not in session:
        return redirect('/')
    portfolio = Portfolio.get_portfolio_by_id(id)
    return render_template('delete-portfolio.html', portfolio=portfolio)


@app.route('/portfolios/delete', methods=['POST'])
def delete_portfolio():
    if 'user_id' not in session:
        return redirect('/')
    Portfolio.delete_portfolio(request.form['portfolio_id'])
    return redirect('/portfolios')

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
# -----------------------------------------------------------------------------------------------
# ------------USER PORTFOLIO BREADTH PAGES
# -----------------------------------------------------------------------------------------------
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>


# ------------------- USER PORTFOLIOS BREADTH DETAIL -------------------------------

@app.route('/portfolios/detail/<date>')
def breadth_detail(date):
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
        port_list.append(helpers.ma_compute_test(port.stocks, date))

    return render_template('breadth-detail.html', portfolios=portfolios, port_list=port_list)


# ------------------- USER PORTFOLIOS BREADTH SUMMARY -------------------------------

@app.route('/portfolios/summary/<date>')
def summary(date):
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
    # Returns a list of three portfolio dictionaries that have Keys set to each moving average and a list of Stock objects as Values
    port_list = helpers.breadth_summary_portfolios(portfolios, date)

    summary_total = helpers.breadth_summary_total(portfolios, date)

    return render_template('breadth-summary.html', portfolios=portfolios, port_list=port_list, summary_total=summary_total)


#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
# -----------------------------------------------------------------------------------------------
# ------------CORE SECTOR BREADTH PAGES
# -----------------------------------------------------------------------------------------------
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>


# These will require user login but ANYONE logged in can see them all
# ------------------- CORE SECTORS BREADTH DETAIL -------------------------------

@app.route('/core/sectors/detail/<date>')
def core_sector_detail(date):
    if 'user_id' not in session:
        return redirect('/')
    
    #SECTOR admin user_id hardcoded
    data = {
        'user_id': 1
    }
    portfolios = Portfolio.user_portfolios(data)
    # Check that the user has at least 1 portfolio or redirect back to portfolios home page
    if not portfolios:
        flash("Please create a portfolio to view detail")
        return redirect('/portfolios')

    port_list = []
    for port in portfolios:
        port_list.append(helpers.ma_compute_test(port.stocks, date))

    return render_template('sector-detail.html', portfolios=portfolios, port_list=port_list)


# ------------------- CORE SECTOR BREADTH SUMMARY -------------------------------

@app.route('/core/sectors/summary/<date>')
def core_sector_summary(date):
    if 'user_id' not in session:
        return redirect('/')
    data = {
        'user_id': 1
    }
    portfolios = Portfolio.user_portfolios(data)
    # Check that the user has at least 1 portfolio or redirect back to portfolios home page
    if not portfolios:
        flash("Please create a portfolio to view detail")
        return redirect('/portfolios')
    # Returns a list of three portfolio dictionaries that have Keys set to each moving average and a list of Stock objects as Values
    port_list = helpers.breadth_summary_portfolios(portfolios, date)

    summary_total = helpers.breadth_summary_total(portfolios, date)

    return render_template('sector-summary.html', portfolios=portfolios, port_list=port_list, summary_total=summary_total)



#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
# -----------------------------------------------------------------------------------------------
# ------------CORE INDEX BREADTH PAGES
# -----------------------------------------------------------------------------------------------
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

# ------------------- CORE INDEX BREADTH DETAIL -------------------------------

@app.route('/core/indices/detail/<date>')
def core_index_detail(date):
    if 'user_id' not in session:
        return redirect('/')
    
    # INDEX admin user_id hardcoded
    data = {
        'user_id': 2
    }
    portfolios = Portfolio.user_portfolios(data)
    # Check that the user has at least 1 portfolio or redirect back to portfolios home page
    if not portfolios:
        flash("Please create a portfolio to view detail")
        return redirect('/portfolios')

    port_list = []
    for port in portfolios:
        port_list.append(helpers.ma_compute_test(port.stocks, date))

    return render_template('index-detail.html', portfolios=portfolios, port_list=port_list)


# ------------------- CORE INDEX BREADTH SUMMARY -------------------------------

@app.route('/core/indices/summary/<date>')
def core_index_summary(date):
    if 'user_id' not in session:
        return redirect('/')
    data = {
        'user_id': 2
    }
    portfolios = Portfolio.user_portfolios(data)
    # Check that the user has at least 1 portfolio or redirect back to portfolios home page
    if not portfolios:
        flash("Please create a portfolio to view detail")
        return redirect('/portfolios')
    # Returns a list of three portfolio dictionaries that have Keys set to each moving average and a list of Stock objects as Values
    port_list = helpers.breadth_summary_portfolios(portfolios, date)

    summary_total = helpers.breadth_summary_total(portfolios, date)

    return render_template('index-summary.html', portfolios=portfolios, port_list=port_list, summary_total=summary_total)

