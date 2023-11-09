from flask import flash, Blueprint, request, render_template, redirect, url_for, session
from datetime import datetime
import fairness_distribution_algorithm, requests

# Create a Blueprint for profile-related routes
ticket_fairness_bp = Blueprint("ticket_fairness", __name__)

base_url = 'http://127.0.0.1:5001'


def sale_has_started(concert_id):
    # Fetch the concert based on the concert_id
    concert = requests.get(f'{base_url}/concert/{concert_id}').json()

    # Parse the start_ticket_sale datetime string to a datetime object
    start_ticket_sale_datetime = datetime.strptime(concert.start_ticket_sale, "%Y-%m-%d %H:%M:%S")

    # Get the current datetime
    current_datetime = datetime.now()

    # Check if the current datetime is earlier than the start_ticket_sale datetime
    return current_datetime >= start_ticket_sale_datetime


@ticket_fairness_bp.route('/initial')
def initial():
    # Create a dictionary to store TicketingSystem instances
    ticketing_systems = {}

    # Define the acceptable range for the ticketing system
    acceptable_range = 100

    # Fetch the list of concerts
    concerts = requests.get(f'{base_url}/concerts').json()

    for concert in concerts:
        ticketing_system = fairness_distribution_algorithm.TicketingSystem(acceptable_range, concert.total_tickets_for_sale)
        ticketing_systems[concert.id] = ticketing_system


@ticket_fairness_bp.route('/add_user', methods=['POST'])
def add_user():
    user_id = int(request.form['user_id'])
    arrival_time = int(request.form['arrival_time'])
    ticketing_system.add_user_to_waiting_room(user_id, arrival_time)
    return "User added to waiting room."

@ticket_fairness_bp.route('/start_sale')
def start_sale():
    ticketing_system.start_sale()
    return "Ticket sale has started."


@ticket_fairness_bp.route("/concert/<int:concert_id>/waiting_room")
def waiting_room(concert_id):
    username = session.get('user_id')
    user = requests.get(f'{base_url}/users/{username}').json()
    # Fetch the concert based on the concert_id
    concert = requests.get(f'{base_url}/concert/{concert_id}').json()

    # Check if the current datetime is earlier than the start_ticket_sale datetime
    if not sale_has_started(concert_id):
        # I want to add this user into the waiting room queue for this specific concert
        # Get the TicketingSystem instance for this concert
        ticketing_system = ticketing_system.get(concert_id)

        if ticketing_system:
            # Add the user to the waiting room
            ticketing_system.add_user_to_waiting_room(user.id, datetime.now())

            # Get the queue position assigned to the user
            queue_position = user.queue_position

            return render_template('waiting_room.html', concert=concert, queue_position=queue_position)

    # If the current datetime is not earlier, users should not be in the waiting room
    return redirect(url_for("ticket_fairness.queue", concert_id=concert.id))


@ticket_fairness_bp.route('/concert/<int:concert_id>/queue/', methods=['GET', 'POST'])
def queue(concert_id):
    user = User.query.get(session.get('user_id'))
    # Fetch the concert based on the concert_id
    concert = Concert.query.get(concert_id)
    # Check if the sale has started
    if sale_has_started(concert_id):
        if request.method == 'POST':
            # Process the user's request to join the queue
            # Get the TicketingSystem instance for this concert
            ticketing_system = ticketing_systems.get(concert_id)

            if ticketing_system:
                # Add the user to the queue for this concert
                user_id = ticketing_system.add_user_to_queue(user.id)

                flash(f'You have joined the queue with user ID {user_id}')
        return render_template('queue.html', concert=concert)
    else:
        return render_template('booth.html', concert_id=concert_id)
