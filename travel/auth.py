from flask import Blueprint, render_template, redirect, url_for, flash
from .forms import LoginForm, RegisterForm
from .models import User

from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user
from . import auth

from . import db
# bp = Blueprint('auth',__name__)
authbp = Blueprint('auth', __name__ )

# @authbp.route('/register', methods = ['GET', 'POST'])
# def register():
#     # print('Method type: ', request.method)
#     form = RegisterForm()
#     if form.validate_on_submit():

#         # call the function that checks and returns image
#         user = User(username=form.username.data,
#                     email=form.email.data, 
#                     password=form.password.data,
#                     contactNumber=form.contactNumber.data, 
#                     streetAddress=form.streetAddress.data,
#                     )

#         # add the object to the db session
#         db.session.add(user)
#         # commit to the database
#         db.session.commit()
#         print('Successfully created user', 'success')
#         # Always end with redirect when form is valid
#         return redirect(url_for('auth.login'))
  
#     return render_template('user.html', form=form, heading="Register", description="Sign up as new user here")

@authbp.route('/register', methods = ['GET', 'POST'])  
def register():  
  #create the form
    form = RegisterForm()
    #this line is called when the form - POST
    if form.validate_on_submit():
      print('Register form submitted')
       
      #get username, password and email from the form
      username =form.username.data
      email=form.email.data

      #check if a user exists
      user = db.session.scalar(db.select(User).where(User.username==username))
      if user:#this returns true when user is not None
          flash('Username already exists, please try another')
          return redirect(url_for('auth.register'))
      
      user = db.session.scalar(db.select(User).where(User.email==email))
      if user:#this returns true when user is not None
          flash('Email already in use, please try another')
          return redirect(url_for('auth.register'))
      

      pwd = form.password.data
      contactNumber = form.contactNumber.data

      user = db.session.scalar(db.select(User).where(User.contactNumber==contactNumber))
      if user:#this returns true when user is not None
          flash('Contact number already in use, please try another')
          return redirect(url_for('auth.register'))

      streetAddress = form.streetAddress.data
      passwordHash = generate_password_hash(pwd)
      #create a new user model object
      new_user = User(username=username, password=passwordHash, email=email, contactNumber=contactNumber, streetAddress=streetAddress)
      db.session.add(new_user)
      db.session.commit()
      flash("Registered user successfully")
      return redirect(url_for('auth.login'))
       
    return render_template('user.html', form=form, heading='Register')


@authbp.route('/login', methods = ['GET', 'POST'])
def login():
  form = LoginForm()
  error=None
  if(form.validate_on_submit()):
    user_name = form.username.data
    password = form.password.data
    u1 = User.query.filter_by(username=user_name).first()
    
        #if there is no user with that name
    if u1 is None:
      error='Incorrect user name'
    #check the password - notice password hash function
    elif not check_password_hash(u1.password, password): # takes the hash and password
      error='Incorrect password'
    if error is None:
    #all good, set the login_user
      login_user(u1)
      return redirect(url_for('main.index'))
    else:
      print(error)
      flash(error)
    #it comes here when it is a get method
  return render_template('user.html', form=form, heading='Login')


@authbp.route('/logout')
def logout():
  logout_user()
  # return 'Successfully logged out user'
  return redirect(url_for('main.index'))
  



# # create a blueprint
# authbp = Blueprint('auth', __name__ )

# @authbp.route('/login', methods=['GET', 'POST'])
# def login():
#     loginForm = LoginForm()
#     if loginForm.validate_on_submit():
#         print('Successfully logged in')
#         flash('You logged in successfully')
#         return redirect(url_for('main.index'))
#     return render_template('user.html', form=loginForm,  heading='Login', description="Sign in here")

# @authbp.route('/register', methods = ['GET', 'POST'])
# def register():
#     form = RegisterForm()
#     if form.validate_on_submit():
#         print('Successfully registered')
#         return redirect(url_for('auth.login'))
#     return render_template('user.html', form=form, heading="Register", description="Sign up as new user here")
