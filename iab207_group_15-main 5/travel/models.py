from . import db
from datetime import datetime
from flask_login import UserMixin

class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), index=True, unique=True, nullable=False)
    email = db.Column(db.String(100), index=True, nullable=False)
    password = db.Column(db.String(100), index=True, nullable=False)
    contactNumber = db.Column(db.String(100), index=True, nullable=False, unique=True)
    streetAddress = db.Column(db.String(100), index=True, nullable=False)
    
    # Relationships
    comments = db.relationship('Comment', backref='user')
    events = db.relationship('Event', backref='creator')  # Events created by this user
    orders = db.relationship('Order', backref='user')     # Tickets booked by this user
    
    def __repr__(self):
        return f"User: {self.username}"

class Event(db.Model):
    __tablename__ = 'Events'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80))
    description = db.Column(db.String(200))
    image = db.Column(db.String(400))
    currency = db.Column(db.String(3))
    genre = db.Column(db.String(50))
    status = db.Column(db.String(20), default='Open')  # Open, Inactive, Sold Out, Cancelled
    date = db.Column(db.DateTime, nullable=True)  # Add event date for status calculation
    capacity = db.Column(db.Integer, default=100)  # Maximum tickets available
    created_at = db.Column(db.DateTime, default=datetime.now())
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))  # Event creator
    
    # Relationships
    comments = db.relationship('Comment', backref='event', cascade='all, delete-orphan')
    orders = db.relationship('Order', backref='event', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f"Event: {self.name}"
    
    # Property to check if event is in past
    @property
    def is_past(self):
        if self.date:
            return self.date < datetime.now()
        return False
    
    # Auto-update status based on date and capacity
    def update_status(self):
        if self.status == 'Cancelled':
            return
            
        if self.is_past:
            self.status = 'Inactive'
        elif len(self.orders) >= self.capacity:
            self.status = 'Sold Out'
        else:
            self.status = 'Open'

class Comment(db.Model):
    __tablename__ = 'comments'
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(400))
    created_at = db.Column(db.DateTime, default=datetime.now())
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    event_id = db.Column(db.Integer, db.ForeignKey('Events.id'))

    def __repr__(self):
        return f"Comment: {self.text}"

class Order(db.Model):
    __tablename__ = 'orders'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    event_id = db.Column(db.Integer, db.ForeignKey('Events.id'))
    quantity = db.Column(db.Integer, default=1)
    total_price = db.Column(db.Float, nullable=True)
    booked_at = db.Column(db.DateTime, default=datetime.now())
    status = db.Column(db.String(20), default='Confirmed')  # Confirmed, Cancelled, Refunded
    
    def __repr__(self):
        return f"Order: {self.id} for Event: {self.event_id}"
    

# Add to models.py
class Booking(db.Model):
    __tablename__ = 'bookings'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    event_id = db.Column(db.Integer, db.ForeignKey('Events.id'))
    booked_at = db.Column(db.DateTime, default=datetime.now())
    quantity = db.Column(db.Integer, default=1)
    
    user = db.relationship('User', backref='bookings')
    event = db.relationship('Event', backref='bookings')