from config import Config
from flask import Flask, request, redirect, session, jsonify
from flask_cors import CORS
import fairness_distribution_algorithm
import routes.concert_db as concert_db
from datetime import datetime


app = Flask(__name__)
CORS(app)
app.config.from_object(Config)
app.secret_key = 'your_secret_key'

ticketmaster_base_url = 'http://127.0.0.1:5000'


# Create a dictionary to store TicketingSystem instances
ticketing_systems = {}


# Fetch concerts and initialize TicketingSystem instances
def initialize_ticketing_systems():

    global ticketing_systems

    concerts = concert_db.get_all_concerts().get_json()

    for concert in concerts:
        # Define the acceptable range for the ticketing system
        acceptable_range = 10

        ticketing_system = fairness_distribution_algorithm.TicketingSystem(acceptable_range,
                                                                           concert['start_ticket_sale'],
                                                                           concert['total_tickets_for_sale'])

        ticketing_systems[concert['concert_id']] = ticketing_system


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


@app.route("/concert/<int:concert_id>/arrive_waiting_room", methods=["GET"])
def arrive_waiting_room(concert_id):
    username = session.get('username')

    # Get the TicketingSystem instance for this concert
    selected_ticketing_system = ticketing_systems[str(concert_id)]

    if selected_ticketing_system:
        # Add the user to the waiting room
        selected_ticketing_system.add_user_to_waiting_room(username, datetime.now())

        # Get the queue position assigned to the user
        cluster_number = selected_ticketing_system.user_cluster_number(username)

        return redirect("{}/fairness/concert/{}/waiting_room/{}".format(ticketmaster_base_url,
                                                                        concert_id, cluster_number))


@app.route('/concert/<int:concert_id>/user_status', methods=['GET'])
def user_status(concert_id):
    # Replace the following lines with your actual logic
    username = "ibrahim"

    # Fetch the TicketingSystem instance for the concert
    selected_ticketing_system = ticketing_systems[str(concert_id)]

    if not selected_ticketing_system:
        return jsonify({"error": "Ticketing system not found."}), 500

    # Check if the sale has started
    sale_started = sale_has_started(concert_id)

    # Get the user's queue position
    cluster_number = selected_ticketing_system.user_cluster_number(username)

    # Check if it's the user's turn and the booth has available slots
    is_user_turn = selected_ticketing_system.is_user_turn(username)

    # Check if there are users in the waiting room
    users_in_waiting_room = selected_ticketing_system.users_in_waiting_room()

    print("Users in waiting room:", selected_ticketing_system.waiting_room_service.get_waiting_room())

    user_status_data = {
        "clusterNumber": cluster_number,
        "isUserTurn": is_user_turn,
        "saleStarted": sale_started,
        "usersInWaitingRoom": users_in_waiting_room
    }
    print(user_status_data)

    return jsonify(user_status_data)


@app.route('/concert/<int:concert_id>/enter_booth', methods=['GET'])
def enter_booth(concert_id):
    # Replace the following lines with your actual logic
    username = session.get('username')  # Replace with the actual user_id

    # Fetch the TicketingSystem instance for the concert
    selected_ticketing_system = ticketing_systems[str(concert_id)]

    if not selected_ticketing_system:
        return jsonify({"error": "Ticketing system not found."}), 500

    selected_ticketing_system.process_queue(username)

    return redirect("{}/fairness/concert/{}/booth".format(ticketmaster_base_url, concert_id))


with app.app_context():
    initialize_ticketing_systems()


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)
