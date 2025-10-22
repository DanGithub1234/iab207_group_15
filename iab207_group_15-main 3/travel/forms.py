from flask_wtf import FlaskForm
from wtforms import (
    TextAreaField,
    SubmitField,
    StringField,
    PasswordField,
    SelectField,
    DateField,
    TimeField,
    IntegerField,
    DecimalField,
)
from wtforms.validators import InputRequired, Email, EqualTo, Length, NumberRange
from flask_wtf.file import FileRequired, FileField, FileAllowed


ALLOWED_FILE = {"PNG", "JPG", "png", "jpg"}


# -------------------- AUTH FORMS --------------------
class LoginForm(FlaskForm):
    username = StringField("Username", validators=[InputRequired()])
    password = PasswordField("Password", validators=[InputRequired()])
    submit = SubmitField("Login")


class RegisterForm(FlaskForm):
    username = StringField("Username", validators=[InputRequired("Enter username..."), Length(max=50)])
    email = StringField("Email", validators=[InputRequired(), Email(), Length(max=100)])
    password = PasswordField("Password", validators=[InputRequired("Enter password...")])
    confirm = PasswordField(
        "Confirm Password",
        validators=[EqualTo("password", message="Re-enter same as Password")],
    )

    contactNumber = StringField("Contact Number", validators=[InputRequired("Enter phone number...")])
    streetAddress = StringField("Street Address", validators=[InputRequired("Enter street address...")])
    submit = SubmitField("Register")


# -------------------- COMMENT FORM --------------------
# IMPORTANT: Our models use Comment.body, so keep the field name here as `text` and
# map it to Comment.body in the route (events.comment).
class CommentForm(FlaskForm):
    text = TextAreaField(
        "Add a comment",
        validators=[InputRequired(message="Comment cannot be empty."), Length(min=1, max=2000)],
    )
    submit = SubmitField("Post comment")


# -------------------- EVENT FORM --------------------
class EventForm(FlaskForm):
    # Event info
    name = StringField("Event Title", validators=[InputRequired(), Length(max=120)])
    description = TextAreaField("Description", validators=[InputRequired(), Length(max=2000)])

    # Genre
    genre = SelectField(
        "Genre",
        choices=[
            ("pop", "Pop"),
            ("rap", "Rap"),
            ("country", "Country"),
            ("other", "Other"),
        ],
        validators=[InputRequired()],
    )
    genre_other = StringField("Custom Genre (if Other)", validators=[Length(max=60)])

    # Location and timing
    location = StringField("Location", validators=[InputRequired(), Length(max=200)])
    event_date = DateField("Date", validators=[InputRequired()])
    start_time = TimeField("Start Time", validators=[InputRequired()])
    end_time = TimeField("End Time", validators=[InputRequired()])

    # Poster + optional images
    image = FileField(
        "Poster Image",
        validators=[
            FileRequired(message="Please upload a poster image"),
            FileAllowed(ALLOWED_FILE, "Only images are allowed!"),
        ],
    )
    image2 = FileField("Optional Image 2", validators=[FileAllowed(ALLOWED_FILE)])
    image3 = FileField("Optional Image 3", validators=[FileAllowed(ALLOWED_FILE)])

    # Ticket info
    ticket_details = TextAreaField("Ticket Details", validators=[InputRequired(), Length(max=1000)])
    tickets_available = IntegerField(
        "Ticket Availability", validators=[InputRequired(), NumberRange(min=1, max=1000000)]
    )
    ticket_price = DecimalField("Ticket Price", validators=[InputRequired(), NumberRange(min=0)])

    # Submit button
    submit = SubmitField("Create event")
