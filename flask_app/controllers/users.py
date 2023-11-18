from flask import Flask, redirect, render_template, session, request, flash
from flask_app.models.user import User
from flask_bcrypt import Bcrypt
from flask_app import app
bcrypt = Bcrypt(app)


@app.route('/')
def welcome():
    return render_template('index.html')


@app.route('/register')
def register():
    return render_template('register.html')


@app.route('/register/new', methods=['POST'])
def register_new():
    if not User.validate_reg(request.form):
        return redirect('/register')
    pw_hash = bcrypt.generate_password_hash(request.form.get('password'))
    data = {
        "first_name": request.form['first_name'],
        "last_name": request.form['last_name'],
        "username": request.form['username'],
        "password": pw_hash
    }
    user_id = User.save(data)
    print(user_id)
    session['user_id'] = user_id
    session['first_name'] = data['first_name']

    return redirect('/portfolios')


@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/login/user', methods=['POST'])
def login_user():
    data = {
        "username": request.form['username'],
    }
    user_in_db = User.get_one(data)
    if not user_in_db:
        flash('Invalid Email/Password')
        return redirect('/login')
    if not bcrypt.check_password_hash(user_in_db.password, request.form.get('password')):
        flash('Invalid Email/Password')
        return redirect('/login')
    
    session['user_id'] = user_in_db.id
    session['first_name'] = user_in_db.first_name

    return redirect('/portfolios')

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')