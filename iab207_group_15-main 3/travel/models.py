from . import db
from datetime import datetime
from uuid import uuid4
from flask_login import UserMixin


# --- User ---
class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), index=True, unique=True, nullable=False)
    email = db.Column(db.String(100), index=True, nullable=False)
    password = db.Column(db.String(100), index=True, nullable=False)

    contactNumber = db.Column(db.String(100), index=True, nullable=False, unique=True)
    streetAddress = db.Column(db.String(100), index=True, nullable=False)

    # relations (these are fine)
    comments = db.relationship('Comment', backref='user')
    events = db.relationship('Event', backref='user')
    bookings = db.relationship('Booking', backref='user', cascade='all, delete-orphan')  # <-- add

    def __repr__(self):
        return f"<User id={self.id} username={self.username}>"

# class Event(db.Model):
#     __tablename__ = 'Events'
#     id = db.Column(db.Integer, primary_key=True)
#     name = db.Column(db.String(80))
#     description = db.Column(db.String(200))
#     image = db.Column(db.String(400))
#     currency = db.Column(db.String(3))
#     genre = db.Column(db.String(50))
#     # ... Create the Comments db.relationship
# 	# relation to call event.comments and comment.event
#     comments = db.relationship('Comment', backref='event')
	
#     # string print method
#     def __repr__(self):
#         return f"Name: {self.name}"
    


# Uncomment later

# --- Booking ---
class Booking(db.Model):
    __tablename__ = 'booking'
    id = db.Column(db.Integer, primary_key=True)
    # optional human-friendly order code
    order_code = db.Column(db.String(16), unique=True, nullable=False, default=lambda: uuid4().hex[:8].upper())

    # who & what
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)  # <-- add
    event_id = db.Column(db.Integer, db.ForeignKey('events.id', ondelete='CASCADE'), nullable=False)

    # details
    full_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20))
    num_tickets = db.Column(db.Integer, nullable=False)
    total_price = db.Column(db.Float, nullable=False)
    billing_address = db.Column(db.String(255))
    date_booked = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)  # utcnow

    event = db.relationship('Event', backref='bookings')

    def ticket_count(self):
        if self.event and self.num_tickets <= self.event.tickets_available:
            self.event.tickets_available -= self.num_tickets
            db.session.commit()
            return True
        return False

    def __repr__(self):
        return f"<Booking id={self.id} order={self.order_code} user={self.user_id} event={self.event_id}>"



    
# class Event(db.Model):
#     __tablename__ = 'event'
#     id = db.Column(db.Integer, primary_key=True)
#     name = db.Column(db.String(80))
#     description = db.Column(db.String(200))
#     image = db.Column(db.String(400))
#     # ... Create the Comments db.relationship
# 	# relation to call Event.comments and comment.Event
#     comments = db.relationship('Comment', backref='event')
	
#     # string print method
#     def __repr__(self):
#         return f"Name: {self.name}"

# --- Comment ---
class Comment(db.Model):
    __tablename__ = "comments"
    id = db.Column(db.Integer, primary_key=True)

    body = db.Column(db.Text, nullable=False)   # <- keep as body
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    event_id = db.Column(db.Integer, db.ForeignKey("events.id", ondelete="CASCADE"), nullable=False)

    user = db.relationship("User", backref=db.backref("comments", cascade="all, delete-orphan"))
    event = db.relationship(
        "Event",
        backref=db.backref("comments", cascade="all, delete-orphan", order_by="Comment.created_at.desc()")
    )

    def __repr__(self):
        return f"<Comment id={self.id} user_id={self.user_id} event_id={self.event_id}>"



class Event(db.Model):
    __tablename__ = 'events'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80))
    description = db.Column(db.String(200))
    image = db.Column(db.String(400))
    genre = db.Column(db.String(50))
    event_status = db.Column(db.String(50))
    location = db.Column(db.String(200))
    event_date = db.Column(db.Date)
    start_time = db.Column(db.Time)
    end_time = db.Column(db.Time)
    ticket_details = db.Column(db.String(1000))
    tickets_available = db.Column(db.Integer)
    ticket_price = db.Column(db.Float)
    image2 = db.Column(db.String(400), nullable=True)
    image3 = db.Column(db.String(400), nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    def statusUpdate(self):
        current_date = datetime.now().date()
        available = self.tickets_available or 0  # safe default

        if available <= 0:
            self.event_status = "Sold Out"
        elif self.event_date and self.event_date < current_date:
            self.event_status = "Inactive"
        else:
            self.event_status = "Open"

    db.session.commit()

