from flask import Flask, render_template, redirect, url_for, request, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'  # Change this to a strong secret key
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'  # SQLite database
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.session_protection = 'strong'

# User model
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), nullable=False, unique=True)
    password = db.Column(db.String(150), nullable=False)

# User log model
class UserLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    action = db.Column(db.String(150), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    duration = db.Column(db.Float, nullable=True)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            # Log the login action
            new_log = UserLog(user_id=user.id, action='Logged In')
            db.session.add(new_log)
            db.session.commit()
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid credentials', 'danger')
    return render_template('login.html')

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html', username=current_user.username)

@app.route('/logout')
@login_required
def logout():
    # Calculate session duration and log it
    last_login = UserLog.query.filter_by(user_id=current_user.id, action='Logged In').order_by(UserLog.timestamp.desc()).first()
    if last_login:
        last_login.duration = (datetime.datetime.utcnow() - last_login.timestamp).total_seconds() / 60.0  # duration in minutes
        db.session.commit()

    user_id = current_user.id
    logout_user()
    # Log the logout action
    new_log = UserLog(user_id=user_id, action='Logged Out')
    db.session.add(new_log)
    db.session.commit()
    return redirect(url_for('home'))

@app.route('/create_user', methods=['GET', 'POST'])
def create_user():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # Check if the username already exists
        if User.query.filter_by(username=username).first():
            flash('Username already exists, please choose a different one', 'danger')
            return redirect(url_for('create_user'))

        # Hash the password before storing it using the default method
        hashed_password = generate_password_hash(password)
        
        # Create a new user with the hashed password
        new_user = User(username=username, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()

        flash('User created successfully!', 'success')
        return redirect(url_for('login'))

    return render_template('create_user.html')

@app.route('/user_logs')
@login_required
def user_logs():
    # Retrieve logs for the current user
    logs = UserLog.query.filter_by(user_id=current_user.id).order_by(UserLog.timestamp.desc()).all()
    return render_template('user_logs.html', logs=logs)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Create the database tables automatically
    app.run(debug=True)
