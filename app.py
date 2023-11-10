from config import Config
from flask import Flask, request, redirect, session
import fairness_distribution_algorithm
import routes.concert_db as concert_db
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

        ticketing_system = fairness_distribution_algorithm.TicketingSystem(acceptable_range,
                                                                           concert['start_ticket_sale'],
                                                                           concert['total_tickets_for_sale'])

        ticketing_systems[concert['concert_id']] = ticketing_system


def add_user(ticketing_system):
    user_id = int(request.form['user_id'])
    arrival_time = int(request.form['arrival_time'])
    ticketing_system.add_user_to_waiting_room(user_id, arrival_time)
    return "User added to waiting room."


@app.route("/concert/<int:concert_id>/arrive_waiting_room", methods=["GET"])
def arrive_waiting_room(concert_id):
    username = session.get('username')

    # Get the TicketingSystem instance for this concert
    selected_ticketing_system = ticketing_systems[str(concert_id)]

    if selected_ticketing_system:
        # Add the user to the waiting room
        selected_ticketing_system.add_user_to_waiting_room(username, datetime.now())

        # Get the queue position assigned to the user
        queue_position = selected_ticketing_system.user_queue_position(username)

        return redirect("http://127.0.0.1:5000/fairness/concert/{}/waiting_room/{}".format(concert_id, queue_position))


with app.app_context():
    initialize_ticketing_systems()


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)
