# events.py - Updated version
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from .models import Event, Comment, User, Booking
from .forms import EventForm, CommentForm
from . import db
import os
from werkzeug.utils import secure_filename

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


@destbp.route('/categorise')
def categorise():
    genre = request.args.get('genre', 'All') 
    if genre == "All":
        events = db.session.scalars(db.select(Event)).all()
    else:
        events = db.session.scalars(db.select(Event).where(Event.genre == genre)).all()
    
    for event in events:
        event.update_status()
    db.session.commit()
    
    return render_template('index.html', events=events, genre=genre)


@destbp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    print('Method type: ', request.method)
    form = EventForm()
    if form.validate_on_submit():
        db_file_path = check_upload_file(form)
        event = Event(
            name=form.name.data,
            description=form.description.data, 
            genre=form.genre.data, 
            image=db_file_path,
            currency=form.currency.data,
            user_id=current_user.id 
        )
        db.session.add(event)
        db.session.commit()
        flash('Successfully created new event', 'success')
        return redirect(url_for('event.show', id=event.id))
    return render_template('events/create.html', form=form)

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
