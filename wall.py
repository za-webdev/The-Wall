from flask import Flask,request,redirect,render_template,flash,session

from datetime import datetime
import re
import bcrypt

from mysqlconnection import MySQLConnector
app = Flask(__name__)

app.secret_key = "vsdkjnfskj/nsknjscdckj"

mysql = MySQLConnector(app, 'project')

EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9+-._]+@[a-zA-Z0-9+-._]+\.[a-zA-Z]+$')


@app.route('/')
def landing():
	return render_template('landing.html')

@app.route('/sign_in')
def sign_in():
	return render_template('sign_in.html')


@app.route('/sign_up')
def sign_up():
	return render_template('sign_up.html')


@app.route('/register', methods=['POST'])
def registration():
	print request.form
	valid = True
	#for all

	if request.form["first_name"]=='' or request.form["last_name"]=='' or request.form["email"]=='' or request.form["email"]=='' or request.form["confirm"]=='':
		flash("Please fill out all fields")
	#for first name
	
	if len(request.form["first_name"])< 2:
		flash("First name must be 2 characters or longer")
		valid = False
	elif  not request.form["first_name"].isalpha():
		flash("Name field cannot have numbers")
		valid=False

	#for last name
	
	if len(request.form["last_name"])< 2:
		flash("Last name must be 2 characters or longer")
		valid = False
	elif  not request.form["last_name"].isalpha():
		flash("Name field cannot have numbers")
		valid=False

	# f0r email
	
	if not EMAIL_REGEX.match(request.form["email"]):
		flash("Invalid Email")
		valid = False
	else:
		users = mysql.query_db("SELECT * FROM users WHERE email = :email", request.form)
		if len(users) > 0:
			flash("Email already exists")
			valid = False

	#for password

	if len(request.form["password"])<8:
		flash("password must be 8 characters or long")
		valid=False
	#for confirm password

	if request.form["password"] != request.form["confirm"]:
		flash("Password donot match")
		valid=False

	if not valid:
		return redirect('/sign_up')


	else:

		query="INSERT INTO users (first_name,last_name,email,password,created_at,updated_at)VALUES(:first_name,:last_name,:email,:password,NOW(),NOW())"
		print query
		data= dict(request.form)
		data["password"] = bcrypt.hashpw(request.form["password"].encode(), bcrypt.gensalt())
		session["user_id"] = mysql.query_db(query, data)


		return redirect('/wall')

@app.route('/login_page', methods=['POST'])
def login():
	print request.form
	valid = True
	#for email

	if request.form["email"]=='':
		flash("Please enter your email")
		valid=False
	
	if not EMAIL_REGEX.match(request.form["email"]):
		flash("Invalid Email")
		valid = False
	else:
		users = mysql.query_db("SELECT * FROM users WHERE email = :email", request.form)
		if len(users)<1:
			flash("Email does not exists")
			valid = False

	#for password

	if len(request.form["password"])<8:
		flash("password must be 8 characters or long")
		valid=False

	if valid:
		if bcrypt.checkpw(request.form["password"].encode(), users[0]["password"].encode()):
			session["user_id"] = users[0]["id"]
			
		else:
			flash("Incorrect password")

	if not valid:
		return redirect('/sign_in')

	else:

		return redirect('/wall')


@app.route('/wall')
def wall():
	return render_template("my_wall.html",messages=mysql.query_db("SELECT users.first_name,users.last_name,messages.message,messages.created_at,messages.id \
	 FROM messages JOIN users ON users.id=messages.user_id"),comments=mysql.query_db("SELECT users.first_name,users.last_name,comments.comment,comments.created_at,message_id\
	 FROM comments JOIN users ON users.id=comments.user_id"))

@app.route('/wall/post', methods=['post'])
def post():
	query="INSERT INTO messages (message, created_at,updated_at,user_id) VALUES (:message, NOW(),NOW(),:user_id)"

	data={'message':request.form['post'],'user_id':session["user_id"]}

	mysql.query_db(query,data)	

	return redirect('/wall')

@app.route("/wall/post/<_id>/delete", methods=["POST"])
def delete(_id):

		mysql.query_db("DELETE FROM comments WHERE message_id = :id", {"id": _id})
		mysql.query_db("DELETE FROM messages WHERE id = :id", {"id": _id})
		return redirect("/wall")
	



@app.route('/wall/post/<_id>/comment', methods=['post'])
def comment(_id):
	query="INSERT INTO comments (comment, created_at,updated_at,user_id,message_id) VALUES (:comment, NOW(),NOW(),:user_id,:message_id)"

	data={'comment':request.form['comment'],'user_id':session["user_id"],'message_id':_id}

	mysql.query_db(query,data)	

	return redirect('/wall')


@app.route('/logoff')

def logoff():

	session.clear()

	return redirect ('/')



app.run(debug=True)





