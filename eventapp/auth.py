from flask import Blueprint, render_template, redirect, url_for, flash
from .forms import LoginForm, RegisterForm
from .models import User

from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user
from . import auth

from . import db

# define the blueprint 
authbp = Blueprint('auth', __name__ )


# regiester route 
@authbp.route('/register', methods = ['GET', 'POST'])  
def register():  
    form = RegisterForm()
    #the validation of form is fine, HTTP request is POST
    if form.validate_on_submit():
      print('Register form submitted')
       
      #get full name, password and email from the form
      fullname =form.fullname.data
      email=form.email.data

      #check if a user exists
      user = db.session.scalar(db.select(User).where(User.fullname==fullname))
      if user:#this returns true when user is not None
          flash('Name already exists, please try another')
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
      new_user = User(fullname=fullname, password=passwordHash, email=email, contactNumber=contactNumber, streetAddress=streetAddress)
      db.session.add(new_user)
      db.session.commit()
      flash("Registered user successfully, login to get started.")
      return redirect(url_for('auth.login'))
    else:
      return render_template('user.html', form=form, heading='Register')


# login route
@authbp.route('/login', methods = ['GET', 'POST'])
def login():
  form = LoginForm()
  error=None
  if(form.validate_on_submit()):
    email_address = form.email.data
    password = form.password.data
    u1 = User.query.filter_by(email=email_address).first()
    
        #if there is no user with that name
    if u1 is None:
      error='Incorrect name'
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
  return redirect(url_for('main.index'))
  