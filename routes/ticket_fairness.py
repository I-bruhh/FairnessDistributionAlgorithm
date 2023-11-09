from flask import flash, request, render_template, redirect, url_for, session
from datetime import datetime
import routes.concert_db as concert_db
import routes.auth_db as auth_db
from app import ticketing_systems


def sale_has_started(concert_id):
    # Fetch the concert based on the concert_id
    selected_concert = concert_db.get_concert_by_id(concert_id)

    # Parse the start_ticket_sale datetime string to a datetime object
    start_ticket_sale_datetime = datetime.strptime(selected_concert.start_ticket_sale, "%Y-%m-%d %H:%M:%S")

    # Get the current datetime
    current_datetime = datetime.now()

    # Check if the current datetime is earlier than the start_ticket_sale datetime
    return current_datetime >= start_ticket_sale_datetime


def add_user(ticketing_system):
    user_id = int(request.form['user_id'])
    arrival_time = int(request.form['arrival_time'])
    ticketing_system.add_user_to_waiting_room(user_id, arrival_time)
    return "User added to waiting room."


def start_sale():
    ticketing_systems.start_sale()
    return "Ticket sale has started."


def waiting_room(concert_id):
    username = session.get('username')
    user = auth_db.get_user_by_username(username)
    # Fetch the concert based on the concert_id
    selected_concert = concert_db.get_concert_by_id(concert_id)

    # Check if the current datetime is earlier than the start_ticket_sale datetime
    if not sale_has_started(concert_id):
        # I want to add this user into the waiting room queue for this specific concert
        # Get the TicketingSystem instance for this concert
        selected_ticketing_system = ticketing_systems[concert_id]

        if selected_ticketing_system:
            # Add the user to the waiting room
            selected_ticketing_system.add_user_to_waiting_room(user.id, datetime.now())

            # Get the queue position assigned to the user
            queue_position = user.queue_position

            return render_template('waiting_room.html', concert=selected_concert, queue_position=queue_position)

    # If the current datetime is not earlier, users should not be in the waiting room
    return redirect(url_for("ticket_fairness.queue", concert_id=concert_id))


def queue(concert_id):
    username = session.get('username')
    user = auth_db.get_user_by_username(username)
    # Fetch the concert based on the concert_id
    selected_concert = concert_db.get_concert_by_id(concert_id)
    # Check if the sale has started
    if sale_has_started(concert_id):
        if request.method == 'POST':
            # Process the user's request to join the queue
            # Get the TicketingSystem instance for this concert
            selected_ticketing_system = ticketing_systems.get(concert_id)

            if selected_ticketing_system:
                # Add the user to the queue for this concert
                user_id = selected_ticketing_system.add_user_to_queue(user.id)

                flash(f'You have joined the queue with user ID {user_id}')
        return render_template('queue.html', concert=selected_concert)
    else:
        return render_template('booth.html', concert_id=concert_id)
