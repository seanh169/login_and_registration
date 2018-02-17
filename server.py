from flask import Flask, request, redirect, render_template, session, flash
import re
import bcrypt
from mysqlconnection import MySQLConnector
app = Flask(__name__)
app.secret_key='thisisasecret'
mysql = MySQLConnector(app, 'mydb')
EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')
@app.route('/')
def index():
	# emails = mysql.query_db("SELECT * FROM userz")
	# print emails
	#lines above are to test if sql is connected properly
	return render_template('index.html')
@app.route('/registration', methods=['POST'])
def registration():
	register = True
	if len(request.form['first']) < 1:
		flash('First Name field is required')
		register = False
	elif len(request.form['first']) < 2:
		flash('First Name field must be two or more characters')
		register = False

	if len(request.form['last']) < 1:
		flash('Last Name is required')
		register = False
	elif len(request.form['last']) < 2:
		flash('First Name must be two or more characters')
		register = False

	if len(request.form['email']) < 1:
		flash('Email address field is required')
		register = False
	elif not EMAIL_REGEX.match(request.form['email']):
		flash('Email address field is not in valid format!')
		register = False
	else:
		emailmatch = mysql.query_db('SELECT * FROM userz WHERE email = :email', request.form)
		if len(emailmatch) > 0:
			flash('Email address already exists, please attempt to login above!')
			register = False

	if len(request.form['passwordnew']) < 1:
		flash("Password field is required")
		register = False
	elif len(request.form['passwordnew']) < 8:
		flash("Password field must be 8 characters or more")
		register = False

	if len(request.form['confirm']) < 1:
		flash("Confirm Password field is required")
		register = False
	elif request.form['confirm'] != request.form['passwordnew']:
		flash("Confirm Password field must match Password field, please try again")
		register = False
	if register:
	## if none of the above coniditons occur , then the email address is
	## going to be sent and stored in our database
		data = {
			"first": request.form["first"],
			"last": request.form["last"],
			"email": request.form["email"],
			"password": bcrypt.hashpw(request.form["passwordnew"].encode(), bcrypt.gensalt())
			}

		query = "INSERT INTO userz (first_name, last_name, email, password, created_at, updated_at) VALUES (:first, :last, :email, :password, NOW(), NOW());"
		user_id = mysql.query_db(query, data)
		session["username"] = "{} {}".format(request.form["first"], request.form["last"])
		session["user_id"] = user_id
		flash('USER HAS BEEN SUCESSFULLY ADDED!')
		return redirect("/")
	else:
		# flash the errors
		# redirect back to the register page
		##
		# if this line is not added - you will get a valueError of
		# View function did not return a response
		return redirect("/")
@app.route('/login', methods=["POST"])
def login():

	uservalid = True

	if len(request.form["username"]) < 1:
		flash("Email is required")
		uservalid = False
	elif not EMAIL_REGEX.match(request.form["username"]):
		flash("Invalid email")
		uservalid = False
	else:
		user_matched_email_list = mysql.query_db("SELECT * FROM userz WHERE email = :username", request.form)
		if len(user_matched_email_list) < 1:
			flash("Email doesn't exist")
			uservalid = False

	if len(request.form["password"]) < 1:
		flash("Password is required")
		uservalid = False
	elif len(request.form["password"]) < 8:
		flash("Password must be 8 characters or more")
		uservalid = False

	if not uservalid:
		return redirect("/")

	user = user_matched_email_list[0]

	print user 

	if bcrypt.checkpw(request.form["password"].encode(), user["password"].encode()):
		session['created_at']= user['created_at']
		session["user_id"] = user["id"]
		session["username"] = "{} {}".format(user["first_name"], user["last_name"])
		return render_template('success.html', username = session['username'], time=session['created_at'])

	else:
		# flash the errors
		# redirect back to the register page
		flash("Incorrect password")
		return redirect("/")

app.run(debug=True)

































