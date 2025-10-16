from . import db
from datetime import datetime
from flask_login import UserMixin


class User(db.Model, UserMixin):
    __tablename__ = 'users' # good practice to specify table name
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), index=True, unique=True, nullable=False)
    email = db.Column(db.String(100), index=True, nullable=False)
	# password should never stored in the DB, an encrypted password is stored
	# the storage should be at least 255 chars long, depending on your hashing algorithm
    password = db.Column(db.String(100), index=True, nullable=False) # later have to make hashed

    contactNumber = db.Column(db.String(100), index=True, nullable=False, unique=True)
    streetAddress = db.Column(db.String(100), index=True, nullable=False)
    
    # password_hash = db.Column(db.String(255), nullable=False)

    # relation to call user.comments and comment.created_by

    comments = db.relationship('Comment', backref='user')
    events = db.relationship('Event', backref='user')
    
    # string print method
    def __repr__(self):
        return f"Name: {self.name}"

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

class Booking(db.Model):
    __tablename__ = 'booking'
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(100), nullable = False)
    email = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20))
    num_tickets = db.Column(db.Integer, nullable=False)
    total_price = db.Column(db.Float, nullable=False)
    billing_address = db.Column(db.String(255))
    event_id = db.Column(db.Integer, db.ForeignKey('events.id'), nullable=False)
    date_booked = db.Column(db.DateTime, default=datetime.now(), nullable=False)

    event = db.relationship('Event', backref='bookings')

    def __repr__(self):
        return f'<Booking {self.full_name} x{self.num_tickets} (event={self.event_id})>'
	
    # string print method
    def ticket_count(self):
        if self.event and self.num_tickets <= self.event.tickets_available:
            self.event.tickets_available -= self.num_tickets
            db.session.commit()
            return True
        return False

    def __repr__(self):
        return f"Name: {self.name}"


    
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

class Comment(db.Model):
    __tablename__ = 'comments'
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(400))
    created_at = db.Column(db.DateTime, default=datetime.now())
    # add the foreign key
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    Event_id = db.Column(db.Integer, db.ForeignKey('events.id'))

    # string print method
    def __repr__(self):
        return f"Comment: {self.text}"
    



class Event(db.Model):
    __tablename__ = 'events'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80))
    description = db.Column(db.String(200))
    image = db.Column(db.String(400))
    # currency = db.Column(db.String(3))
    genre = db.Column(db.String(50))
    event_status = db.Column(db.String(50))
    # new fields for event creation
    location = db.Column(db.String(200))
    event_date = db.Column(db.Date)
    start_time = db.Column(db.Time)
    end_time = db.Column(db.Time)
    ticket_details = db.Column(db.String(1000))
    tickets_available = db.Column(db.Integer)
    ticket_price = db.Column(db.Float)
    image2 = db.Column(db.String(400), nullable=True)
    image3 = db.Column(db.String(400), nullable=True)

    # relationship to comments
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    comments = db.relationship('Comment', backref='event')
    # bookings = db.relationship('Booking', backref='event')


    def statusUpdate(self):
        current_date = datetime.now().date()
        
        if self.tickets_available <= 0:
            self.event_status = "Sold Out"
        elif self.event_date < current_date:
            self.event_status = "Inactive"
        else:
             self.event_status = "Open"


        db.session.commit()

    def __repr__(self):
        return f"Name: {self.name}"
