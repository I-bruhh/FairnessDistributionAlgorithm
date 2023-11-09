from config import Config
from flask import Flask
import fairness_distribution_algorithm
import routes.concert_db as concert_db


app = Flask(__name__)
app.config.from_object(Config)
app.secret_key = 'your_secret_key'

base_url = 'http://0.0.0.0:5001'


# Create a dictionary to store TicketingSystem instances
ticketing_systems = {}


# Fetch concerts and initialize TicketingSystem instances
def initialize_ticketing_systems():

    global ticketing_systems

    concerts = concert_db.get_all_concerts()
    print(concerts)

    for concert in concerts:
        # Define the acceptable range for the ticketing system
        acceptable_range = 100

        ticketing_system = fairness_distribution_algorithm.TicketingSystem(acceptable_range, concert.total_tickets_for_sale)

        ticketing_systems[concert.id] = ticketing_system


with app.app_context():
    initialize_ticketing_systems()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)
