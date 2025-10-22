# create_sample_data.py
import sys
import os
from datetime import datetime, timedelta

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from travel import create_app, db
from travel.models import User, Event, Comment, Order

def create_sample_data():
    app = create_app()
    
    with app.app_context():
        # Drop all tables and recreate
        print("Dropping existing tables...")
        db.drop_all()
        print("Creating new tables...")
        db.create_all()
        
        # Create sample users
        print("Creating sample users...")
        user1 = User(
            username='john_doe',
            email='john@example.com',
            password='password123',  # In real app, this should be hashed
            contactNumber='0412345678',
            streetAddress='123 Main St, Brisbane'
        )
        
        user2 = User(
            username='jane_smith',
            email='jane@example.com',
            password='password123',
            contactNumber='0498765432',
            streetAddress='456 Queen St, Sydney'
        )
        
        db.session.add(user1)
        db.session.add(user2)
        db.session.commit()
        
        print(f"Created users: {user1.username}, {user2.username}")
        
        # Create sample events
        print("Creating sample events...")
        events = [
            Event(
                name='Coldplay: Music of the Spheres World Tour',
                description='Experience the magical performance of Coldplay live in concert with their greatest hits and spectacular visual effects.',
                image='/static/image/coldplay_concert.jpg',
                currency='AUD',
                genre='pop',
                status='Open',
                date=datetime.now() + timedelta(days=30),
                capacity=500,
                user_id=user1.id,
                created_at=datetime.now()
            ),
            Event(
                name='Zedd: Moment of Clarity Tour',
                description='An electrifying EDM experience with stunning light shows and incredible beats that will keep you dancing all night.',
                image='/static/image/zedd_concert.jpg',
                currency='AUD',
                genre='edm',
                status='Open',
                date=datetime.now() + timedelta(days=45),
                capacity=300,
                user_id=user1.id,
                created_at=datetime.now()
            ),
            Event(
                name='Taylor Swift: The Eras Tour',
                description='Journey through all of Taylor Swift musical eras in this spectacular stadium tour featuring hits from her entire career.',
                image='/static/image/taylor_swift_concert.jpg',
                currency='AUD',
                genre='pop',
                status='Sold Out',
                date=datetime.now() + timedelta(days=15),
                capacity=1000,
                user_id=user2.id,
                created_at=datetime.now()
            ),
            Event(
                name='Kendrick Lamar: The Big Steppers Tour',
                description='Witness the Pulitzer Prize-winning artist perform tracks from his latest album along with classic favorites.',
                image='/static/image/kendrick_concert.jpg',
                currency='AUD',
                genre='rap',
                status='Open',
                date=datetime.now() + timedelta(days=60),
                capacity=400,
                user_id=user2.id,
                created_at=datetime.now()
            ),
            Event(
                name='Luke Combs: Growin Up and Gettin Old Tour',
                description='Country music sensation Luke Combs brings his heartfelt songs and powerful voice to the stage.',
                image='/static/image/luke_combs_concert.jpg',
                currency='AUD',
                genre='country',
                status='Open',
                date=datetime.now() + timedelta(days=75),
                capacity=600,
                user_id=user1.id,
                created_at=datetime.now()
            ),
            Event(
                name='Arctic Monkeys: The Car Tour',
                description='The iconic indie rock band returns with their latest album and all your favorite classics.',
                image='/static/image/arctic_monkeys_concert.jpg',
                currency='AUD',
                genre='rock',
                status='Inactive',
                date=datetime.now() - timedelta(days=10),  # Past event
                capacity=800,
                user_id=user2.id,
                created_at=datetime.now()
            ),
            Event(
                name='BTS: Yet to Come in Busan',
                description='The global phenomenon BTS performs in a spectacular free concert celebrating Korean culture.',
                image='/static/image/bts_concert.jpg',
                currency='AUD',
                genre='pop',
                status='Cancelled',
                date=datetime.now() + timedelta(days=20),
                capacity=2000,
                user_id=user1.id,
                created_at=datetime.now()
            )
        ]
        
        for event in events:
            db.session.add(event)
        db.session.commit()
        
        print(f"Created {len(events)} sample events")
        
        # Create sample comments
        print("Creating sample comments...")
        comments = [
            Comment(
                text="Can't wait for this! Coldplay always puts on an amazing show!",
                user_id=user2.id,
                event_id=events[0].id,
                created_at=datetime.now() - timedelta(days=2)
            ),
            Comment(
                text="I've been waiting for them to come to Australia!",
                user_id=user1.id,
                event_id=events[0].id,
                created_at=datetime.now() - timedelta(days=1)
            ),
            Comment(
                text="Zedd's light shows are incredible. Highly recommend!",
                user_id=user2.id,
                event_id=events[1].id,
                created_at=datetime.now() - timedelta(days=3)
            ),
            Comment(
                text="So sad this got cancelled! Was really looking forward to it.",
                user_id=user1.id,
                event_id=events[6].id,
                created_at=datetime.now() - timedelta(days=1)
            )
        ]
        
        for comment in comments:
            db.session.add(comment)
        db.session.commit()
        
        print(f"Created {len(comments)} sample comments")
        
        # Create sample orders
        print("Creating sample orders...")
        orders = [
            Order(
                user_id=user1.id,
                event_id=events[1].id,  # Zedd concert
                quantity=2,
                total_price=180.00,
                booked_at=datetime.now() - timedelta(days=5)
            ),
            Order(
                user_id=user2.id,
                event_id=events[3].id,  # Kendrick Lamar
                quantity=1,
                total_price=120.00,
                booked_at=datetime.now() - timedelta(days=2)
            ),
            Order(
                user_id=user1.id,
                event_id=events[4].id,  # Luke Combs
                quantity=4,
                total_price=320.00,
                booked_at=datetime.now() - timedelta(days=1)
            )
        ]
        
        for order in orders:
            db.session.add(order)
        db.session.commit()
        
        print(f"Created {len(orders)} sample orders")
        
        print("\n✅ Sample data created successfully!")
        print(f"📊 Users: {User.query.count()}")
        print(f"🎵 Events: {Event.query.count()}")
        print(f"💬 Comments: {Comment.query.count()}")
        print(f"🎫 Orders: {Order.query.count()}")
        
        # Print login credentials for testing
        print("\n🔐 Test Login Credentials:")
        print(f"User 1: {user1.username} / {user1.email} / password123")
        print(f"User 2: {user2.username} / {user2.email} / password123")

if __name__ == '__main__':
    create_sample_data()