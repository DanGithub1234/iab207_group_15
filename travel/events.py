from flask import Blueprint, render_template, request, redirect, url_for
from datetime import datetime
from .models import Event, Comment, Booking
from .forms import EventForm, CommentForm
from . import db
import os
from werkzeug.utils import secure_filename
from flask_login import current_user

destbp = Blueprint('event', __name__, url_prefix='/events')

@destbp.route('/<id>')
def show(id):
    event = db.session.scalar(db.select(Event).where(Event.id==id))
    # create the comment form
    cform = CommentForm()    
    return render_template('events/show.html', event=event, form=cform, user=current_user)


@destbp.route('/<int:id>/buyTickets', methods=['GET', 'POST'])
def buyTickets(id):
    event = db.session.scalar(db.select(Event).where(Event.id == id))
    if request.method == 'POST':
        # read the posted fields (names match your HTML)
        full_name = request.form.get('full_name')
        email = request.form.get('email')
        phone = request.form.get('buyer_phone')
        quantity = int(request.form.get('quantity', 1))
        billing_address = request.form.get('billing_address', '')

        # compute total: (ticket price + $5 fee) * quantity
        total_price = (float(event.ticket_price) + 5.0) * quantity

        # save to DB
        booking = Booking(
            full_name=full_name,
            email=email,
            phone=phone,
            num_tickets=quantity,
            total_price=total_price,
            billing_address=billing_address,
            event_id=id,
            date_booked=datetime.utcnow()
        )
        db.session.add(booking)
        db.session.commit()
        print(f" Saved booking id={booking.id}")

        # re-render and open your modal
        return render_template(
            'events/buyTickets.html',
            event=event,
            show_modal=True,
            modal_name=full_name,
            modal_qty=quantity,
            modal_total=total_price
        )

    # GET
    return render_template('events/buyTickets.html', event=event)


@destbp.route('/categorise')
def categorise():
    genre = request.args.get('genre', 'All')
    if genre == "All":
      events = db.session.scalars(db.select(Event)).all()
    # create the comment form
    else:
       events = db.session.scalars(db.select(Event).where(Event.genre==genre)).all()
    return render_template('index.html', events=events, genre=genre)






# @destbp.route('/create', methods=['GET', 'POST'])
# def create():
#   print('Method type: ', request.method)
#   form = EventForm()
#   if form.validate_on_submit():
#     # call the function that checks and returns image
#     db_file_path = check_upload_file(form)
#     event = Event(name=form.name.data,description=form.description.data, genre=form.genre.data, 
#     image = db_file_path,currency=form.currency.data)
#     # add the object to the db session
#     db.session.add(event)
#     # commit to the database
#     db.session.commit()
#     print('Successfully created new travel event', 'success')
#     # Always end with redirect when form is valid
#     return redirect(url_for('event.create'))
#   return render_template('events/create.html', form=form)

def check_upload_file(form):
    # get file data from form  
    fp = form.image.data
    filename = fp.filename
    # get the current path of the module file… store image file relative to this path  
    BASE_PATH = os.path.dirname(__file__)
    # upload file location – directory of this file/static/image
    upload_path = os.path.join(BASE_PATH,'static/image',secure_filename(filename))
    # store relative path in DB as image location in HTML is relative
    db_upload_path = '/static/image/' + secure_filename(filename)
    # save the file and return the db upload path  
    fp.save(upload_path)
    return db_upload_path


@destbp.route('/<id>/comment', methods=['GET', 'POST'])  
def comment(id):  
    form = CommentForm()  
    # get the Event object associated to the page and the comment
    event = db.session.scalar(db.select(Event).where(Event.id==id))
    if form.validate_on_submit():  
      # read the comment from the form, associate the Comment's Event field
      # with the Event object from the above DB query
      comment = Comment(text=form.text.data, event=event, user_id=current_user.id) 
      # here the back-referencing works - comment.Event is set
      # and the link is created
      db.session.add(comment) 
      db.session.commit() 
      # flashing a message which needs to be handled by the html
      # flash('Your comment has been added', 'success')  
      print('Your comment has been added', 'success') 
    # using redirect sends a GET request to Event.show
    return redirect(url_for('event.show', id=id))



@destbp.route('/create', methods=['GET', 'POST'])
def create():
  print('Method type: ', request.method)
  form = EventForm()
  if form.validate_on_submit():
    # call the function that checks and returns image
    db_file_path = check_upload_file(form)
    event = Event(name=form.name.data,description=form.description.data, 
    image = db_file_path, 
    genre = form.genre.data,
    location = form.location.data,
    event_date = form.event_date.data,
    start_time = form.start_time.data,
    end_time = form.end_time.data,
    ticket_details=form.ticket_details.data, tickets_available=form.tickets_available.data,  ticket_price=form.ticket_price.data,
    image2 = db_file_path,
    image3 = db_file_path,
    user = current_user )

    # add the object to the db session
    db.session.add(event)
    # commit to the database
    db.session.commit()
    print(Event.query.all())

    # Always end with redirect when form is valid
    return redirect(url_for('event.create'))
  if request.method == 'POST':
        print("FORM ERRORS:", form.errors)
  return render_template('events/create.html', form=form, user=current_user)

# a rough booking history to see if bookings are saved
@destbp.route('/bookingHistory')
def booking_history():
    from .models import Booking
    rows = Booking.query.order_by(Booking.id.desc()).all()
    html_rows = [
        f"<tr><td>{b.id}</td><td>{b.full_name}</td><td>{b.email}</td>"
        f"<td>{b.num_tickets}</td><td>${b.total_price:.2f}</td>"
        f"<td>{b.event_id}</td><td>{b.date_booked}</td></tr>"
        for b in rows
    ]
    return (
        "<h2>Booking History</h2>"
        "<table border='1' cellpadding='6'>"
        "<tr><th>ID</th><th>Name</th><th>Email</th><th>Qty</th>"
        "<th>Total</th><th>Event</th><th>Date</th></tr>"
        + "".join(html_rows) + "</table>"
    )
