from flask import Flask, redirect, url_for
from config import Config
from routes.auth_db import auth_db_bp
from routes.concert_db import concert_db_bp
from routes.purchase_db import purchase_db_bp
from routes.ticket_fairness import ticket_fairness_bp

app = Flask(__name__)
app.config.from_object(Config)
app.secret_key = 'your_secret_key'

base_url = 'http://0.0.0.0:5001'

app.register_blueprint(auth_db_bp)
app.register_blueprint(concert_db_bp)
app.register_blueprint(purchase_db_bp)
app.register_blueprint(ticket_fairness_bp, url_prefix='/ticket_fairness')


@app.route('/')
def index():
    return redirect(url_for('ticket_fairness.initial'))


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)
