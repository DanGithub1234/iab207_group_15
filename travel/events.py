from flask import Blueprint, render_template, request, redirect, url_for, flash
from datetime import datetime
from werkzeug.utils import secure_filename
from flask_login import current_user, login_required
from .models import Event, Comment, Booking, db
from .forms import EventForm, CommentForm
import os

# Blueprint
destbp = Blueprint("event", __name__, url_prefix="/events")

# -------------------- SHOW EVENT --------------------
@destbp.route("/<int:id>")
def show(id: int):
    event = db.session.get(Event, id)
    if not event:
        flash("Event not found.", "warning")
        return redirect(url_for("main.index"))

    event.statusUpdate()
    cform = CommentForm()

    comments = (
        db.session.execute(
            db.select(Comment)
              .where(Comment.event_id == id)
              .order_by(Comment.created_at.desc())
        ).scalars().all()
    )

    return render_template(
        "events/show.html",
        event=event,
        form=cform,
        comments=comments,
        user=current_user
    )


# -------------------- BUY TICKETS --------------------
@destbp.route("/<int:id>/buyTickets", methods=["GET", "POST"])
@login_required
def buyTickets(id: int):
    event = db.session.get(Event, id)
    if not event:
        flash("Event not found.", "warning")
        return redirect(url_for("main.index"))

    if request.method == "POST":
        full_name = (request.form.get("full_name") or "").strip()
        email = (request.form.get("email") or "").strip()
        phone = (request.form.get("buyer_phone") or "").strip()
        billing_address = (request.form.get("billing_address") or "").strip()
        try:
            quantity = int(request.form.get("quantity") or 1)
        except ValueError:
            quantity = 1

        if quantity < 1:
            flash("Quantity must be at least 1.", "warning")
            return redirect(url_for("event.buyTickets", id=id))
        if event.tickets_available is None or event.tickets_available < quantity:
            flash("Not enough tickets available.", "warning")
            return redirect(url_for("event.buyTickets", id=id))

        total_price = (float(event.ticket_price or 0) + 5.0) * quantity

        booking = Booking(
            full_name=full_name,
            email=email,
            phone=phone,
            num_tickets=quantity,
            total_price=total_price,
            billing_address=billing_address,
            event_id=event.id,
            user_id=current_user.id,
            date_booked=datetime.utcnow(),
        )

        event.tickets_available = (event.tickets_available or 0) - quantity

        db.session.add(booking)
        db.session.commit()

        return render_template(
            "events/buyTickets.html",
            event=event,
            show_modal=True,
            modal_name=full_name,
            modal_qty=quantity,
            modal_total=total_price,
            modal_order_id=getattr(booking, "order_code", None) or booking.id,
        )

    return render_template("events/buyTickets.html", event=event)


# -------------------- FILTER BY GENRE --------------------
@destbp.route("/categorise")
def categorise():
    genre = request.args.get("genre", "All")
    if genre == "All":
        events = db.session.scalars(db.select(Event)).all()
    else:
        events = db.session.scalars(
            db.select(Event).where(Event.genre == genre)
        ).all()

    for event in events:
        event.statusUpdate()
    db.session.commit()

    return render_template("index.html", events=events, genre=genre)

# -------------------- FILE UPLOAD HELPER --------------------
def check_upload_file(form):
    fp = form.image.data
    filename = fp.filename

    BASE_PATH = os.path.dirname(__file__)
    upload_path = os.path.join(BASE_PATH, "static/image", secure_filename(filename))
    db_upload_path = "/static/image/" + secure_filename(filename)

    fp.save(upload_path)
    return db_upload_path


# -------------------- COMMENTS --------------------
@destbp.route("/<int:id>/comment", methods=["POST"])
@login_required
def comment(id: int):
    form = CommentForm()
    event = db.session.get(Event, id)
    if not event:
        flash("Event not found.", "warning")
        return redirect(url_for("main.index"))

    if form.validate_on_submit():
        new_comment = Comment(
            body=form.body.data.strip(),
            event=event,
            user_id=current_user.id,
        )
        db.session.add(new_comment)
        db.session.commit()
        flash("Your comment has been added.", "success")
    else:
        for field, errs in form.errors.items():
            for e in errs:
                flash(f"{field}: {e}", "warning")

    return redirect(url_for("event.show", id=id))


# -------------------- CREATE / EDIT EVENT --------------------
@destbp.route("/create", methods=["GET", "POST"])
@destbp.route("/create/<int:id>", methods=["GET", "POST"])
@login_required
def create(id: int | None = None):
    event = db.session.get(Event, id) if id else None
    form = EventForm(obj=event) if event else EventForm()

    if form.validate_on_submit():
        db_file_path = check_upload_file(form)

        if event:
            event.name = form.name.data
            event.description = form.description.data
            event.image = db_file_path
            event.genre = form.genre.data
            event.location = form.location.data
            event.event_date = form.event_date.data
            event.start_time = form.start_time.data
            event.ticket_details = form.ticket_details.data
        else:
            event = Event(
                name=form.name.data,
                description=form.description.data,
                image=db_file_path,
                genre=form.genre.data,
                location=form.location.data,
                event_date=form.event_date.data,
                start_time=form.start_time.data,
                end_time=form.end_time.data,
                ticket_details=form.ticket_details.data,
                tickets_available=form.tickets_available.data,
                ticket_price=form.ticket_price.data,
                image2=db_file_path,
                image3=db_file_path,
                user=current_user,
            )
            event.statusUpdate()
            db.session.add(event)

        db.session.commit()
        flash("Event saved.", "success")
        return redirect(url_for("event.create"))

    if request.method == "POST":
        print("FORM ERRORS:", form.errors)

    return render_template("events/create.html", form=form, user=current_user)


# -------------------- MY TICKETS --------------------
@destbp.route("/my-tickets")
@login_required
def my_tickets():
    bookings = (
        db.session.execute(
            db.select(Booking)
              .where(Booking.user_id == current_user.id)
              .order_by(Booking.date_booked.desc())
        ).scalars().all()
    )
    return render_template("events/my_ticket.html", bookings=bookings)


# -------------------- BOOKING HISTORY DEBUG --------------------
@destbp.route("/bookingHistory")
@login_required
def booking_history():
    rows = Booking.query.filter_by(user_id=current_user.id).order_by(Booking.id.desc()).all()
    html_rows = [
        f"<tr><td>{b.id}</td><td>{b.order_code or ''}</td><td>{b.full_name}</td><td>{b.email}</td>"
        f"<td>{b.num_tickets}</td><td>${b.total_price:.2f}</td>"
        f"<td>{b.event_id}</td><td>{b.date_booked}</td></tr>"
        for b in rows
    ]
    return (
        "<h2>My Booking History</h2>"
        "<table border='1' cellpadding='6'>"
        "<tr><th>ID</th><th>Order</th><th>Name</th><th>Email</th><th>Qty</th>"
        "<th>Total</th><th>Event</th><th>Date</th></tr>"
        + "".join(html_rows) + "</table>"
    )
