from flask import Blueprint
from .forms import EventForm, RegisterForm
from . import db
from .models import Event, User
from flask_login import login_required, current_user
from flask import Flask, render_template, request, redirect, url_for, flash



mainbp = Blueprint('main', __name__)


@mainbp.route('/')
def index():
    tag_line='You need a vacation'
    Events = Event.query.all() #get the hotels
    print('events',Events)
    return render_template('index.html', tag_line=tag_line,
                    Events=Events)


