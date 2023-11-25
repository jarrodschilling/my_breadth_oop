from flask_app.models.portfolio import Portfolio
from flask_app.models.stock import Stock
from flask_app import app

tickers = ['GS', 'MDB', 'TOL']
stock_names = ['Goldman Sachs', 'MongoDB', 'Toll Brothers']
for i in range(len(tickers)):
    #API CALL where stock_name = APICALL(tickers[i])
    stock_name = stock_names[i]

    stock_data = {
        'name': stock_name,
        'ticker': tickers[i]
    }
    stock_id = Stock.check_stock(stock_data)
    
    portfolio_data = {
        # pull from request.form, will stay the same
        'name': 'FINAL',
        # set to session user_id
        'user_id': 1,
        'stock_id': stock_id
    }
    
    # redirect back to Create Portfolio Page
    validate_portfolio_data = Portfolio.validate_portfolio_data(portfolio_data)
    if validate_portfolio_data == False:
        print("name already exists")

    portfolio = Portfolio.save(portfolio_data)


# Close, but created all new portfolios with unique ids. Need to pull portfolios page by
# session['user_id'] and portfolios.name. We also need to check when user creates
# a new portfolio that they don't use a same name that already exists.
# CHECK THAT STOCK DOESN'T ALREADY EXIST IN DATABASE