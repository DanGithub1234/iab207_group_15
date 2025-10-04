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

# class Booking(db.Model):
#     __tablename__ = 'booking'
#     id = db.Column(db.Integer, primary_key=True)
#     name = db.Column(db.String(80))
#     bookingDateTime = db.Column(db.Integer)
#     numberOfTickets = db.Column(db.Integer)
#     totalPrice = db.Column(db.Integer)
#     # ... Create the Comments db.relationship
# 	# relation to call event.comments and comment.Event
#     # comments = db.relationship('Comment', backref='Event')
#     # add the foreign key
#     user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
#     Event_id = db.Column(db.Integer, db.ForeignKey('Events.id'))
	
#     # string print method
#     def __repr__(self):
#         return f"Name: {self.name}"
    
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
    currency = db.Column(db.String(3))

    # new fields for event creation
    location = db.Column(db.String(200))
    event_date = db.Column(db.Date)
    start_time = db.Column(db.Time)
    end_time = db.Column(db.Time)
    ticket_details = db.Column(db.String(1000))
    tickets_available = db.Column(db.Integer)
    ticket_price = db.Column(db.Float)
    image2 = db.Column(db.String(400))
    image3 = db.Column(db.String(400))

    # relationship to comments
    comments = db.relationship('Comment', backref='destination')

    def __repr__(self):
        return f"Name: {self.name}"