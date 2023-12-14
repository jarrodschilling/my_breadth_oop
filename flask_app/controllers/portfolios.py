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


# ------------------- ADD STOCKS TO EXISTING PORTFOLIO -------------------------------
@app.route('/add-stock/<int:id>')
def add_stock_page(id):
    portfolio = Portfolio.get_portfolio_by_id(id)
    print(portfolio)
    return render_template('add-stock.html', portfolio=portfolio)


@app.route('/add-stock', methods=['POST'])
def add_stock():
    #Combine tickers and stock_names with one API CALL????
    tickers = Stock.clean_symbols(request.form.getlist('tickers[]'))
    if not tickers:
        flash('New Portfolio cannot be empty')
        return redirect('/portfolios/new')
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
    portfolio = Portfolio.get_portfolio_by_id(id)
    stocks = PortfoliosStocks.get_stocks_in_portfolio(id)

    return render_template('delete-stock.html', portfolio=portfolio, stocks=stocks)


@app.route('/delete-stock', methods=['POST'])
def delete_stock():
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


#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
# -----------------------------------------------------------------------------------------------
# ------------USER PORTFOLIO BREADTH PAGES
# -----------------------------------------------------------------------------------------------
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>


# ------------------- USER PORTFOLIOS BREADTH DETAIL -------------------------------

# GET ROUTE
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
    

# POST ROUTE to access current AND previous day closes
@app.route('/portfolios/detail', methods=['POST'])
def breadth_deatil_post():
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
    date = request.form['date']
    port_list = []
    for port in portfolios:
        port_list.append(helpers.ma_compute_test(port.stocks, date))

    return render_template('breadth-detail.html', portfolios=portfolios, port_list=port_list)


# ------------------- USER PORTFOLIOS BREADTH SUMMARY -------------------------------

# GET ROUTE
@app.route('/portfolios/summary/<date>')
def summary(date):
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


# POST ROUTE to access current AND previous day closes
@app.route('/portfolios/summary', methods=['POST'])
def summary_post():
    date = request.form['date']
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

# GET ROUTE
@app.route('/core/sectors/detail')
def core_sector_detail():
    pass


# POST ROUTE to access current AND previous day closes
@app.route('/core/sectors/detail', methods=['POST'])
def core_sector_detail_post():
    pass


# ------------------- CORE SECTOR BREADTH SUMMARY -------------------------------

# GET ROUTE
@app.route('/core/sectors/summary')
def core_sector_summary():
    pass


# POST ROUTE to access current AND previous day closes
@app.route('/core/sectors/summary', methods=['POST'])
def core_sector_summary_post():
    pass



#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
# -----------------------------------------------------------------------------------------------
# ------------CORE INDEX BREADTH PAGES
# -----------------------------------------------------------------------------------------------
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

# ------------------- CORE INDEX BREADTH DETAIL -------------------------------

# GET ROUTE
@app.route('/core/indices/detail')
def core_index_detail():
    if 'user_id' not in session:
        return redirect('/')
    
    #@@@@@@@@+++++++++ HARDCODE TO user_id of INDEX ADMIN +++++++++++++++++++++++@@@@@@@
    data = {
        'user_id': session['user_id']
    }
    portfolios = Portfolio.user_portfolios(data)

    port_list = []
    for port in portfolios:
        port_list.append(helpers.ma_compute_test(port.stocks, 'today'))

    # <<<<<<<<< NEEDS TO BE UPDATED >>>>>>>>>>>>>>>>
    return render_template('breadth-detail.html', portfolios=portfolios, port_list=port_list)


# ------------------- CORE INDEX BREADTH SUMMARY -------------------------------

# GET ROUTE
@app.route('/core/indices/summary')
def core_index_summary():
    pass


# POST ROUTE to access current AND previous day closes
@app.route('/core/indices/summary', methods=['POST'])
def core_index_summary_post():
    pass

