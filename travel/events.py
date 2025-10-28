from flask import Blueprint, render_template, request, redirect, url_for
from .models import Event, Comment, Booking
from datetime import datetime
from .forms import EventForm, CommentForm
from . import db
import os
from werkzeug.utils import secure_filename
from flask_login import current_user, login_required

destbp = Blueprint('event', __name__, url_prefix='/events')

MAX_PER_ORDER = 10


# @destbp.route('/bookinghistory')
# def bookinghistory(id):
#     event = db.session.scalar(db.select(Event).where(Event.id==id))
#     event.statusUpdate()
#     # create the comment form
#     cform = CommentForm()    
#     return render_template('events/show.html', event=event, form=cform, user=current_user)

@destbp.route('/<id>')
def show(id):
    event = db.session.scalar(db.select(Event).where(Event.id==id))
    event.statusUpdate()
    # create the comment form
    cform = CommentForm()    
    return render_template('events/show.html', event=event, form=cform, user=current_user)

@destbp.route('/<int:id>/buyTickets', methods=['GET', 'POST'])
@login_required
def buyTickets(id):
    event = db.session.scalar(db.select(Event).where(Event.id == id))
    if not event:
        return render_template('events/unavailable_modal.html',
                               title="Not found",
                               message="This event no longer exists.",
                               redirect_url=url_for('event.categorise'))

    status_is_open = (getattr(event, "event_status", "Open") == "Open")
    has_tickets    = (event.tickets_available or 0) > 0
    is_bookable    = status_is_open and has_tickets

    # If user tries to book tickets for unavailable event this modal appears
    if request.method == 'GET' and not is_bookable:
        return render_template('events/unavailable_modal.html',
                               title="Not available",
                               message=f"Sorry, “{event.name}” is not available for booking.",
                               redirect_url=url_for('event.categorise'))

    if request.method == 'POST':
        if not is_bookable:
            return render_template('events/unavailable_modal.html',
                                   title="Not available",
                                   message=f"Sorry, “{event.name}” is not available for booking.",
                                   redirect_url=url_for('event.categorise'))
            
    if request.method == 'POST':
        # read the posted fields (names match your HTML)
        full_name = request.form.get('full_name')
        email = request.form.get('email')
        phone = request.form.get('buyer_phone')
        quantity = int(request.form.get('quantity', 1))
        billing_address = request.form.get('billing_address', '')

        # adds an order limit to prevent overbooking
        remaining = event.tickets_available or 0
        qty_error = None
        if quantity < 1:
            qty_error = "Please enter at least 1 ticket."
        elif quantity > MAX_PER_ORDER:
            qty_error = f"You can buy a maximum of {MAX_PER_ORDER} tickets per order."
        elif quantity > remaining:
            qty_error = f"Only {remaining} ticket(s) remaining."

        if qty_error:
            qty_max = min(MAX_PER_ORDER, remaining) if remaining else MAX_PER_ORDER
            return render_template(
                'events/buyTickets.html',
                event=event,
                qty_error=qty_error,
                qty_value=quantity,
                qty_max=qty_max
            )
            
        # Total = (ticket price × quantity) + $5 one-time booking fee
        total_price = (float(event.ticket_price) * quantity) + 5.0

        # save to DB
        booking = Booking(
            full_name=full_name,
            email=email,
            phone=phone,
            num_tickets=quantity,
            total_price=total_price,
            billing_address=billing_address,
            event_id=id,
            user_id = current_user.id,
            date_booked=datetime.now()
        )


        event.tickets_available -= quantity
        db.session.add(booking)
        db.session.commit()
        # if booking.ticket_count():
        #     db.session.add(booking)
        #     db.session.commit()
        #     print(f"Saved booking id={booking.id}")
        # else:
        #     print(f"Not enough tickets")


        
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
    remaining = event.tickets_available or 0
    qty_max = min(MAX_PER_ORDER, remaining) if remaining else MAX_PER_ORDER
    return render_template('events/buyTickets.html', event=event, qty_max=qty_max)

@destbp.route('/categorise')
def categorise():

    events = db.session.scalars(db.select(Event)).all()
    
    genre = request.args.get('genre', 'All')
    if genre == "All":
      events = db.session.scalars(db.select(Event)).all()
    # create the comment form
    else:
       events = db.session.scalars(db.select(Event).where(Event.genre==genre)).all()

    for event in events:
      event.statusUpdate()
    db.session.commit() 

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
@login_required
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



@destbp.route('/cancel/<int:id>', methods=['POST'])
@login_required
def cancel(id):
    event = db.session.get(Event, id)
    # form = EventForm(obj=event)
    event.cancelEvent()
    db.session.commit()
    # flash("Event has been cancelled.")
    return redirect(url_for('event.show', id=id))



@destbp.route('/create', methods=['GET', 'POST'])
@destbp.route('/create/<int:id>', methods=['GET', 'POST'])
@login_required
def create(id=None):
  event = None
  if id:
    event = db.session.get(Event, id)
    form = EventForm(obj=event)
    # form.name.data = event.name 
    # form.description.data = event.description
    # db_file_path = event.image 
    # form.genre.data = event.genre 
    # form.location.data = event.location 
    # form.event_date.data = event.event_date 
    # form.start_time.data = event.start_time 
    # form.ticket_details.data = event.ticket_details 
    
  else:
    print('Method type: ', request.method)
    form = EventForm()
  if form.validate_on_submit():

    if event:
      db_file_path = check_upload_file(form)
      event.name = form.name.data
      event.description = form.description.data 
      event.image = db_file_path
      event.genre = form.genre.data 
      event.location = form.location.data 
      event.event_date = form.event_date.data 
      event.start_time = form.start_time.data 
      event.ticket_details = form.ticket_details.data 
  
       # add the others
      # event = Event(name=form.name.data,description=form.description.data, 
      # image = db_file_path, 
      # genre = form.genre.data,
      # location = form.location.data,
      # event_date = form.event_date.data,
      # start_time = form.start_time.data,
      # end_time = form.end_time.data,
      # ticket_details=form.ticket_details.data, tickets_available=form.tickets_available.data,  ticket_price=form.ticket_price.data,
      # image2 = db_file_path,
      # image3 = db_file_path,
      # user = current_user )
      # event.statusUpdate()

      # add a cancel events button here?


    else:
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
      image2 = db_file_path, # still need to get rid of these... but when i do they bugg
      image3 = db_file_path,
      user = current_user )

      event.statusUpdate()
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
# @destbp.route('/bookingHistory')
# def booking_history():
#     # from .models import Booking
#     # event = db.session.scalar(db.select(Event).where(Event.id==id))
#     rows = Booking.query.order_by(Booking.id.desc()).all()

#     return render_template('events/bookingHistory.html', bookings=bookings, user=current_user)
    
    # return (
    #     "<h2>Booking History</h2>"
    #     "<table border='1' cellpadding='6'>"
    #     "<tr><th>ID</th><th>Name</th><th>Email</th><th>Qty</th>"
    #     "<th>Total</th><th>Event</th><th>Date</th></tr>"
    #     + "".join(html_rows) + "</table>"
    # )
  #return render_template('events/create.html', form=form, user=current_user)
