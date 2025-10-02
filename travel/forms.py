from flask_wtf import FlaskForm
from wtforms.fields import TextAreaField,SubmitField, StringField, PasswordField, SelectField
from wtforms.validators import InputRequired, Email, EqualTo
from flask_wtf.file import FileRequired, FileField, FileAllowed


ALLOWED_FILE = {'PNG','JPG','png','jpg'}


class EventForm(FlaskForm):
  name = StringField('Country', validators=[InputRequired()])
  # adding two validators, one to ensure input is entered and other to check if the 
  # description meets the length requirements
  description = TextAreaField('Description', validators = [InputRequired()])
  genre = SelectField('Genre', choices=[('pop', 'Pop'), ('rap', 'Rap'), ('country', 'Country')])
  # genre = SelectField('Genre', choices=[('Pop'), ('Rap'), ('Country')])


  image = FileField('Event Image', validators=[
    FileRequired(message='Image cannot be empty'),
    FileAllowed(ALLOWED_FILE, message='Only PNG or JPG files allowed')])

  currency = StringField('Currency', validators=[InputRequired()])
  submit = SubmitField("Create")



class LoginForm(FlaskForm):
  username = StringField('Username', validators=[InputRequired()])
  password = PasswordField('Password', validators=[InputRequired()])
  submit = SubmitField("Login")


class RegisterForm(FlaskForm):
  username = StringField('Username', validators=[InputRequired('Enter username...')])
  email = StringField('Email', validators=[InputRequired(),Email() ])
  password = PasswordField('Password', validators=[InputRequired('Enter password...')])
  confirm = PasswordField('Confirm Password', 
          validators=[EqualTo('password', message='Re-enter same as Password')])
  

  contactNumber = StringField('ContactNumber', validators=[InputRequired('Enter phone number...')])
  streetAddress = StringField('StreetAddress', validators=[InputRequired('Enter street address...')])
  submit = SubmitField("Register")

class CommentForm(FlaskForm):
  text = TextAreaField('Comment', validators=[InputRequired("Enter comment...")])
  submit = SubmitField("Create")




