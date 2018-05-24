from flask import Flask, render_template, redirect, request, session, flash
from mysqlconnection import MySQLConnector
import re
import md5
from datetime import datetime 

app = Flask(__name__)
mysql = MySQLConnector(app, 'login_registration')

EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')

app.secret_key = '876dsf87ysuid'

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/success', methods=['POST'])
def success():
    first_name = request.form['first_name']
    last_name = request.form['last_name']
    email = request.form['email']
    password = md5.new(request.form['password']).hexdigest()
    confirm_password = md5.new(request.form['confirm_password']).hexdigest()


    errors = False
    if not first_name.isalpha() or len(first_name)<1:
        flash('first name must contain no numbers and be at least 2 characters')
        errors = True
    if not last_name.isalpha() or len(last_name)<1:
        flash('last name must contain no numbers and be at least 2 characters')
        errors = True
    if not EMAIL_REGEX.match(email):
        flash('invalid email format')
        errors = True
    if len(request.form['password']) < 8 or len(request.form['confirm_password']) < 8:
        flash('password must be at least 8 characters')
        errors = True 
    if password != confirm_password:
        flash("passwords don't match")
        errors = True

    if errors:
        return redirect('/')
    else:
        query = "INSERT INTO users (first_name, last_name, email, password, created_at, updated_at) VALUES (:fName, :lName, :email, :password, now(), now())"
        data = {
            'fName' : first_name,
            'lName' : last_name,
            'email' : email,
            'password': password,
        }
        mysql.query_db(query, data)
        flash('successful registration, please login')
        return redirect ('/')

@app.route('/user', methods=['POST'])
def login():
    email = request.form['email']
    password = md5.new(request.form['password']).hexdigest()
    query = "SELECT id, first_name, last_name, DATE_FORMAT(created_at, '%W %M %e %Y') as created_at FROM users WHERE users.email = :email AND users.password = :password"
    data = {
        'email' : email,
        'password' : password
    }
    loggedIn_user = mysql.query_db(query, data)
    if len(loggedIn_user)>0:
        session['uid'] = loggedIn_user[0]['id']
        return render_template('user_page.html',user=loggedIn_user[0])
    else:
        flash("login failed: email and/or password invalid please try again")
        return redirect('/')

app.run(debug=True)
