from flask import Flask, render_template, request, redirect, url_for, session
import hashlib
import smtplib
from email.mime.text import MIMEText
import mysql.connector
from mysql.connector import Error
from blockchain import Blockchain
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from io import BytesIO
import base64
from blockchain import Blockchain

# Initialize Blockchain
blockchain = Blockchain()

app = Flask(__name__)
app.secret_key = 'secret_key'

# Initialize Blockchain
blockchain = Blockchain()

# SMTP Credentials
sender = "cloudplatform432@gmail.com"
password = "gqqeyltwrjdgtjtx"

# MySQL Database Configuration
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',  # Replace with your MySQL username
    'password': '',  # Replace with your MySQL password
    'database': 'voting_system'  # Replace with your database name
}

def get_db_connection():
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        return connection
    except Error as e:
        print(f"Error connecting to MySQL: {e}")
        return None

def send_email(to_email, subject, body):
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = sender
    msg['To'] = to_email

    try:
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login(sender, password)
            server.send_message(msg)
        print("Email sent successfully.")
    except Exception as e:
        print(f"Error sending email: {e}")

def init_db():
    connection = get_db_connection()
    if connection:
        cursor = connection.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                first_name VARCHAR(255),
                last_name VARCHAR(255),
                father_name VARCHAR(255),
                age INT,
                gender VARCHAR(50),
                email VARCHAR(255),
                mobile_number VARCHAR(20),
                password VARCHAR(255),
                government_id_hash VARCHAR(255),
                status VARCHAR(50)
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS parties (
                id INT AUTO_INCREMENT PRIMARY KEY,
                party_name VARCHAR(255),
                candidate_name VARCHAR(255)
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS votes (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT,
                party_id INT
            )
        ''')
        connection.commit()
        cursor.close()
        connection.close()

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        connection = get_db_connection()
        if connection:
            cursor = connection.cursor()
            cursor.execute('SELECT * FROM users WHERE email=%s AND password=%s AND status="approved"', (email, password))
            user = cursor.fetchone()
            cursor.close()
            connection.close()
            
            if user:
                session['user'] = {
                    'id': user[0],
                    'fname': user[1],
                    'lname': user[2]
                }
                return redirect(url_for('dashboard'))
            else:
                return "Invalid credentials or account not approved."
    
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect(url_for('login'))
    
    connection = get_db_connection()
    if connection:
        cursor = connection.cursor()
        cursor.execute('SELECT * FROM parties')
        parties = cursor.fetchall()
        cursor.close()
        connection.close()
    
    return render_template('dashboard.html', parties=parties)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        father_name = request.form['father_name']
        age = int(request.form['age'])
        gender = request.form['gender']
        email = request.form['email']
        mobile_number = request.form['mobile_number']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        
        if password != confirm_password:
            return "Passwords do not match"
        
        if age < 18:
            return "You are underage to vote."
        
        government_id_file = request.files['government_id']
        government_id_hash = hashlib.sha256(government_id_file.read()).hexdigest()
        
        connection = get_db_connection()
        if connection:
            cursor = connection.cursor()
            cursor.execute('''
                INSERT INTO users (first_name, last_name, father_name, age, gender, email, mobile_number, password, government_id_hash, status)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ''', (first_name, last_name, father_name, age, gender, email, mobile_number, password, government_id_hash, 'pending'))
            connection.commit()
            cursor.close()
            connection.close()
        
        send_email(email, 'Registration Successful', 'Your registration is pending approval by the admin.')
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/admin_login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        if username == 'admin' and password == 'admin':
            session['admin'] = True
            return redirect(url_for('admin_dashboard'))
        else:
            return "Invalid credentials"
    
    return render_template('admin_login.html')

@app.route('/admin_dashboard')
def admin_dashboard():
    if 'admin' not in session:
        return redirect(url_for('admin_login'))
    
    connection = get_db_connection()
    if connection:
        cursor = connection.cursor()
        cursor.execute('SELECT * FROM users WHERE status="pending"')
        users = cursor.fetchall()
        cursor.execute('SELECT * FROM parties')
        parties = cursor.fetchall()
        cursor.close()
        connection.close()
    
    return render_template('admin_dashboard.html', users=users, parties=parties)

@app.route('/approve_user/<user_id>')
def approve_user(user_id):
    if 'admin' not in session:
        return redirect(url_for('admin_login'))
    
    connection = get_db_connection()
    if connection:
        cursor = connection.cursor()
        cursor.execute('UPDATE users SET status="approved" WHERE id=%s', (user_id,))
        connection.commit()
        cursor.close()
        connection.close()
    
    send_email('user_email', 'Approval Notification', 'Your registration has been approved by the admin.')
    return redirect(url_for('admin_dashboard'))

@app.route('/add_party', methods=['GET', 'POST'])
def add_party():
    if 'admin' not in session:
        return redirect(url_for('admin_login'))
    
    if request.method == 'POST':
        party_name = request.form['party_name']
        candidate_name = request.form['candidate_name']
        
        connection = get_db_connection()
        if connection:
            cursor = connection.cursor()
            cursor.execute('INSERT INTO parties (party_name, candidate_name) VALUES (%s, %s)', (party_name, candidate_name))
            connection.commit()
            cursor.close()
            connection.close()
        
        return redirect(url_for('admin_dashboard'))
    
    return render_template('add_party.html')

@app.route('/vote/<party_id>', methods=['POST'])
def vote(party_id):
    if 'user' not in session:
        return redirect(url_for('login'))
    
    connection = get_db_connection()
    if connection:
        cursor = connection.cursor()
        # Check if the user has already voted
        cursor.execute('SELECT * FROM votes WHERE user_id=%s', (session['user']['id'],))
        existing_vote = cursor.fetchone()
        
        if existing_vote:
            # User has already voted
            return render_template('vote.html', party=None, already_voted=True)
        
        # Fetch the party details
        cursor.execute('SELECT * FROM parties WHERE id=%s', (party_id,))
        party = cursor.fetchone()
        
        if party:
            # Record the vote in the database
            cursor.execute('INSERT INTO votes (user_id, party_id) VALUES (%s, %s)', (session['user']['id'], party_id))
            connection.commit()
            
            # Add the vote as a transaction to the blockchain
            transaction = {
                'voter_id': session['user']['id'],
                'party_name': party[1],
                'candidate_name': party[2]
            }
            blockchain.add_transaction(transaction)  # Add transaction to the blockchain
            blockchain.mine_block()  # Mine a new block
            
            cursor.close()
            connection.close()
            
            # Redirect to the dashboard after successful voting
            return redirect(url_for('dashboard'))
    
    return "Vote failed"
@app.route('/vote_results')
def vote_results():
    if 'admin' not in session:
        return redirect(url_for('admin_login'))
    
    connection = get_db_connection()
    if connection:
        cursor = connection.cursor()
        # Fetch party names and vote counts
        cursor.execute('SELECT party_name, COUNT(votes.id) FROM parties LEFT JOIN votes ON parties.id = votes.party_id GROUP BY parties.id')
        results = cursor.fetchall()
        cursor.close()
        connection.close()
    
    # Prepare data for the chart
    labels = [row[0] for row in results]  # Party names
    data = [row[1] for row in results]   # Vote counts

    return render_template('view_results.html', labels=labels, data=data)

@app.route('/blockchain_hash_values')
def blockchain_hash_values():
    # Pass the blockchain object to the template
    return render_template('blockchain_hash_values.html', blockchain=blockchain)
   

@app.route('/logout')
def logout():
    session.clear()  # Clear the session to log the user out
    return redirect(url_for('login'))  # Redirect to the login page

if __name__ == '__main__':
    init_db()
    app.run(debug=True)