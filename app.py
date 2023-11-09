from config import Config
from flask import Flask, flash, request, render_template, redirect, url_for, session
import fairness_distribution_algorithm
import routes.concert_db as concert_db
import routes.auth_db as auth_db
from datetime import datetime


app = Flask(__name__)
app.config.from_object(Config)
app.secret_key = 'your_secret_key'

base_url = 'http://0.0.0.0:5001'


# Create a dictionary to store TicketingSystem instances
ticketing_systems = {}


# Fetch concerts and initialize TicketingSystem instances
def initialize_ticketing_systems():

    global ticketing_systems

    concerts = concert_db.get_all_concerts().get_json()

    for concert in concerts:
        # Define the acceptable range for the ticketing system
        acceptable_range = 100

        ticketing_system = fairness_distribution_algorithm.TicketingSystem(acceptable_range, concert['total_tickets_for_sale'])

        ticketing_systems[concert['concert_id']] = ticketing_system

    key = list(ticketing_systems.keys())

def sale_has_started(concert_id):
    # Fetch the concert based on the concert_id
    selected_concert = concert_db.get_concert_by_id(concert_id).get_json()

    # Parse the start_ticket_sale datetime string to a datetime object
    start_ticket_sale_datetime = datetime.strptime(selected_concert['start_ticket_sale'], "%Y-%m-%d %H:%M:%S")

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


@app.route("/concert/<int:concert_id>/waiting_room", methods=["GET"])
def waiting_room(concert_id):
    username = session.get('username')
    user = auth_db.get_user_by_username(username)
    print(user)
    # Fetch the concert based on the concert_id
    selected_concert = concert_db.get_concert_by_id(concert_id)

    # Check if the current datetime is earlier than the start_ticket_sale datetime
    if not sale_has_started(concert_id):

        # Get the TicketingSystem instance for this concert
        selected_ticketing_system = ticketing_systems[str(concert_id)]

        if selected_ticketing_system:
            # Add the user to the waiting room
            selected_ticketing_system.add_user_to_waiting_room(username, datetime.now())

            # Get the queue position assigned to the user
            queue_position = selected_ticketing_system

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


with app.app_context():
    initialize_ticketing_systems()


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)
