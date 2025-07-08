from flask import request,render_template,redirect,url_for, session, flash
from flask import current_app as app

from models.model import *
import matplotlib
matplotlib.use('Agg')
from matplotlib import pyplot as plt
from datetime import datetime



@app.route('/')
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        full_name = request.form['full_name']
        password = request.form['password']
        user = User.query.filter_by(email=full_name, password=password).first()
        if user:
            session['user_id'] = user.id
            session['role'] = user.role
            if user.role == 'admin':
                return redirect(url_for('admin_dashboard'))
            else:
                return redirect(url_for('user_dashboard'))
        else:
            return render_template('login.html', msg='Invalid user credentials....')
    return render_template('login.html', msg='')

# route for registering a new user
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        full_name = request.form['full_name']
        email = request.form['email']
        password = request.form['password']
        role = 'user'  
        address = request.form['address']
        pin_code = request.form['pin_code']
        user = User.query.filter_by(email=email).first()
        if user:
            return render_template('register.html', msg='Sorry, this email is already registered. Please use a different email.')
        new_user = User(full_name=full_name, email=email, password=password, role=role, address=address, pin_code=pin_code)
        db.session.add(new_user)
        db.session.commit()
        return render_template('login.html', success='Registration successful, please login.')
    return render_template('register.html',msg='')

@app.route('/admin_dashboard', methods=['GET', 'POST'])
def admin_dashboard():
    if 'user_id' not in session or session.get('role') != 'admin':
        return redirect(url_for('login'))

    lots = ParkingLot.query.all()
    return render_template("admin_dashboard.html", lots=lots)


@app.route('/user_dashboard')
def user_dashboard():
    return "<h2>User Dashboard Page - to be implemented</h2>"





