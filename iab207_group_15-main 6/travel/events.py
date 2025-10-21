from flask import Blueprint, render_template, request, redirect, url_for, flash
from .models import Event, Comment, Booking, User
from datetime import datetime
from .forms import EventForm, CommentForm
from . import db
import os
from werkzeug.utils import secure_filename
from flask_login import current_user, login_required

destbp = Blueprint('event', __name__, url_prefix='/events')

@destbp.route('/<id>')
def show(id):
    event = db.session.scalar(db.select(Event).where(Event.id == id))
    if not event:
        flash('Event not found', 'error')
        return redirect(url_for('main.index'))
    
    # Get comments for this event
    comments = db.session.scalars(
        db.select(Comment).where(Comment.event_id == id) 
        .join(User).order_by(Comment.created_at.desc())
    ).all()
    
    # Check if current user has booked this event
    user_has_booked = False
    if current_user.is_authenticated:
        existing_booking = db.session.scalar(
            db.select(Booking).where(
                Booking.user_id == current_user.id, 
                Booking.event_id == id
            )
        )
        user_has_booked = existing_booking is not None
    
    cform = CommentForm()
    return render_template('Events/show.html', 
                         event=event, 
                         form=cform, 
                         comments=comments,
                         user_has_booked=user_has_booked)  # Pass this to template


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
    return render_template('events/buyTickets.html', event=event)


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

    event = db.session.scalar(db.select(Event).where(Event.id==id))
    
    if not event:
        flash('Event not found', 'error')
        return redirect(url_for('main.index'))
        
    if form.validate_on_submit():  
        print('Form validated', form.text.data)
        comment = Comment(
            text=form.text.data, 
            event=event,
            user_id=current_user.id 
        ) 
        db.session.add(comment) 
        db.session.commit() 
        flash('Your comment has been added', 'success') 
    return redirect(url_for('event.show', id=id))

@destbp.route('/<id>/update', methods=['GET', 'POST'])
@login_required
def update(id):
    event = db.session.scalar(db.select(Event).where(Event.id == id))
    
    if not event or event.user_id != current_user.id:
        flash('You can only update your own events', 'error')
        return redirect(url_for('main.index'))
    
    form = EventForm(obj=event)
    if form.validate_on_submit():
        if form.image.data:
            db_file_path = check_upload_file(form)
            event.image = db_file_path
            
        event.name = form.name.data
        event.description = form.description.data
        event.genre = form.genre.data
        event.currency = form.currency.data
        
        db.session.commit()
        flash('Event updated successfully', 'success')
        return redirect(url_for('event.show', id=id))
    
    return render_template('events/update.html', form=form, event=event)

@destbp.route('/<id>/cancel')
@login_required
def cancel(id):
    event = db.session.scalar(db.select(Event).where(Event.id == id))
    
    if not event or event.user_id != current_user.id:
        flash('You can only cancel your own events', 'error')
        return redirect(url_for('main.index'))
    
    event.status = 'Cancelled'
    db.session.commit()
    flash('Event cancelled successfully', 'success')
    return redirect(url_for('event.show', id=id))

def check_upload_file(form):
    fp = form.image.data
    
    # Check if a file was actually uploaded
    if not fp or fp.filename == '':
        # No file was uploaded, return None or the existing path
        return None
    
    # Check if it's a string (existing path) instead of a file object
    if isinstance(fp, str):
        return fp  # Return the existing path
    
    # It's a new file upload, process it
    filename = secure_filename(fp.filename)
    BASE_PATH = os.path.dirname(__file__)
    
    # Create the image directory if it doesn't exist
    image_dir = os.path.join(BASE_PATH, 'static/image')
    if not os.path.exists(image_dir):
        os.makedirs(image_dir)
    
    upload_path = os.path.join(image_dir, filename)
    db_upload_path = '/static/image/' + filename
    
    # Save the file
    fp.save(upload_path)
    return db_upload_path

@destbp.route('/create', methods=['GET', 'POST'])
@destbp.route('/create/<int:id>', methods=['GET', 'POST'])
@login_required
def create(id=None):
  if id:
    event = db.session.get(Event, id)
    form = EventForm(obj = event)
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
      image2 = db_file_path,
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

@destbp.route('/<id>/book', methods=['POST'])
@login_required
def book(id):
    print(f"=== BOOK ROUTE CALLED ===")
    print(f"Event ID: {id}")
    print(f"Current User: {current_user.id} - {current_user.username}")
    
    event = db.session.scalar(db.select(Event).where(Event.id == id))
    
    if not event:
        print("❌ Event not found")
        flash('Event not found', 'error')
        return redirect(url_for('event.show', id=id))

    print(f"Event found: {event.name}, Status: {event.status}")
    
    if event.status != 'Open':
        print(f"❌ Event not open. Status: {event.status}")
        flash('Event is not available for booking', 'error')
        return redirect(url_for('event.show', id=id))

    # Check for existing booking
    existing_booking = db.session.scalar(
        db.select(Booking).where(Booking.user_id == current_user.id, Booking.event_id == id)
    )
    
    if existing_booking:
        print("❌ User already booked this event")
        flash('You have already booked this event', 'info')
        return redirect(url_for('event.show', id=id))
    
    print("✅ Creating new booking...")
    booking = Booking(user_id=current_user.id, event_id=id)
    db.session.add(booking)
    
    # Update event status if capacity reached
    if len(event.bookings) >= event.capacity:
        event.status = 'Sold Out'
        print("🎫 Event sold out!")
    
    db.session.commit()
    print("✅ Booking created successfully!")
    flash('Event booked successfully!', 'success')
    return redirect(url_for('event.my_tickets'))


@destbp.route('/my-tickets')
@login_required
def my_tickets():
    # Get all bookings for the current user
    bookings = db.session.scalars(
        db.select(Booking)
        .where(Booking.user_id == current_user.id)
        .join(Event)
        .order_by(Booking.booked_at.desc())
    ).all()
    
    return render_template('events/my_ticket.html', bookings=bookings)

