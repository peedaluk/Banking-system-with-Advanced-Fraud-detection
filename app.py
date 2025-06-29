from flask import Flask, request, jsonify ,render_template
from flask_mysqldb import MySQL
from flask_bcrypt import Bcrypt
from flask_mail import Mail
import random

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# MySQL configuration
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = '1234567'
app.config['MYSQL_DB'] = 'bank_db'

# Flask-Mail configuration
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USE_SSL'] = True
app.config['MAIL_USERNAME'] = 'your_email@gmail.com'
app.config['MAIL_PASSWORD'] = 'your_email_password'
app.config['MAIL_DEFAULT_SENDER'] = 'your_email@gmail.com'


mysql = MySQL(app)
mail = Mail(app)
bcrypt = Bcrypt(app)

app.config['MYSQL'] = mysql
app.config['BCRYPT'] = bcrypt

@app.route('/')
def home():
    return render_template('login.html')

from routes.user import user_bp
from routes.admin import admin_bp
from routes.atm import atm_bp

app.register_blueprint(user_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(atm_bp)

if __name__ == '__main__':
    app.run(debug=True)
