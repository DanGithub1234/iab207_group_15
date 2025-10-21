from travel import db, create_app
from travel.models import db, Event, Booking
from sqlalchemy import inspect

app = create_app()
ctx = app.app_context()
ctx.push()
db.create_all()
quit()
