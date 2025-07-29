from flask import request,render_template,redirect,url_for, session, flash
from flask import current_app as app
from models.model import *
import matplotlib
matplotlib.use('Agg')
from matplotlib import pyplot as plt
from datetime import datetime
from collections import defaultdict

@app.route('/', methods=['GET', 'POST'])
def login():

    if request.method == 'POST':

        email = request.form['email']
        password = request.form['password']

        user = User.query.filter_by(email=email, password=password).first()

        if user:
            session['user_id'] = user.id
            session['role'] = user.role
            session['full_name'] = user.full_name

            if user.role == 'admin':
                flash('Login successful! Welcome, Admin.')
                return redirect(url_for('admin_dashboard'))
            else:
                flash('Login successful! Welcome, User.')
                return redirect(url_for('user_dashboard'))
            
        else:
            flash('Invalid email or password. Please try again.')
            return render_template('login.html')
        
    return render_template('login.html')

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
            flash('Email already registered. Please log in or use a different email.')
            return render_template('register.html')
        
        new_user = User(full_name=full_name, email=email, password=password, role=role, address=address, pin_code=pin_code)
        db.session.add(new_user)
        db.session.commit()

        flash('Registration successful! You can now log in.')
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/logout')
def logout():

    session.clear()

    flash('You have been logged out successfully.')
    return redirect(url_for('login'))

#========================================================================= Admin Dashboard ====================================================================

@app.route('/admin_dashboard', methods=['GET', 'POST'])
def admin_dashboard():
    if 'user_id' not in session or session.get('role') != 'admin':
        return redirect(url_for('login'))

    lots = ParkingLot.query.all()
    return render_template("admin_dashboard.html", lots=lots)

@app.route('/add_lot', methods=['GET', 'POST'])
def add_lot():
    if 'user_id' not in session or session.get('role') != 'admin':
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        lot_name = request.form['lot_name']
        address = request.form['address']
        pin_code = request.form['pin_code']
        price_per_unit = float(request.form['price_per_unit'])
        total_spots = int(request.form['total_spots'])
        
        new_lot = ParkingLot(
            lot_name=lot_name,
            address=address,
            pin_code=pin_code,
            price_per_unit=price_per_unit,
            total_spots=total_spots
        )
        db.session.add(new_lot)
        db.session.commit()
        for _ in range(total_spots):
            spot = ParkingSpot(lot_id=new_lot.id, status='A')
            db.session.add(spot)
        db.session.commit()

        flash('Parking lot added successfully!')
        return redirect(url_for('admin_dashboard'))

    return render_template("add_lot.html")

@app.route('/edit_lot/<int:lot_id>', methods=['GET', 'POST'])
def edit_lot(lot_id):
    if 'user_id' not in session or session.get('role') != 'admin':
        return redirect(url_for('login'))
    
    lot = ParkingLot.query.get_or_404(lot_id)

    if request.method == 'POST':
        lot.lot_name = request.form['lot_name']
        lot.address = request.form['address']
        lot.pin_code = request.form['pin_code']
        lot.price_per_unit = float(request.form['price_per_unit'])
        lot.total_spots = int(request.form['total_spots'])
        spots = ParkingSpot.query.filter_by(lot_id=lot.id).all()
        if len(spots) < lot.total_spots:
            for _ in range(lot.total_spots - len(spots)):
                new_spot = ParkingSpot(lot_id=lot.id, status='A')
                db.session.add(new_spot)
        elif len(spots) > lot.total_spots:
            for spot in spots[lot.total_spots:]:
                db.session.delete(spot)

        db.session.commit()
        flash('Parking lot updated successfully!')
        return redirect(url_for('admin_dashboard'))
    
    return render_template('edit_lot.html', lot=lot)

@app.route('/delete_lot/<int:lot_id>', methods=['GET'])
def delete_lot(lot_id):
    if 'user_id' not in session or session.get('role') != 'admin':
        return redirect(url_for('login'))
    
    lot = ParkingLot.query.get_or_404(lot_id)

    if lot.occupied_spot > 0:
        flash('Cannot delete lot with occupied lot.')
        return redirect(url_for('admin_dashboard'))
    db.session.delete(lot)
    db.session.commit()
    flash('Parking lot deleted successfully!')
    return redirect(url_for('admin_dashboard'))

@app.route('/view_spot/<int:spot_id>', methods=['GET', 'POST'])
def view_spot(spot_id):

    spot = ParkingSpot.query.get_or_404(spot_id)
    lot = ParkingLot.query.get(spot.lot_id)

    if request.method == 'POST':
        if spot.status == 'A':
            lot.total_spots -= 1
            db.session.delete(spot)
            db.session.commit()
            flash('Spot deleted successfully!')
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Cannot delete occupied spot.')

    return render_template('view_spot.html', spot=spot)

@app.route('/view_reservation/<int:spot_id>')
def view_reservation_details(spot_id):

    reservation = Reservation.query.filter_by(spot_id=spot_id).first_or_404()

    return render_template('reservation_details.html', reservation=reservation)

@app.route('/users')
def users_page():
    if 'user_id' not in session or session.get('role') != 'admin':
        return redirect(url_for('login'))

    all_users = User.query.filter_by(role='user').all()
    return render_template('users.html', users=all_users)

@app.route('/parking_history')
def parking_history():
    if 'user_id' not in session or session.get('role') != 'admin':
        return redirect(url_for('login'))

    reservations = Reservation.query.all()
    return render_template('parking_history.html', reservations=reservations)

@app.route('/summary')
def summary():
    if 'user_id' not in session or session.get('role') != 'admin':
        return redirect(url_for('login'))

    lots = ParkingLot.query.all()
    if not lots:
        return render_template("summary.html", pie_chart=None, bar_chart=None)

    lot_names = []
    revenues = []
    occupied_counts = []
    available_counts = []

    for lot in lots:
        lot_names.append(lot.lot_name)
        occupied = sum(1 for spot in lot.spots if spot.status == 'O')
        available = sum(1 for spot in lot.spots if spot.status == 'A')
        revenue = occupied * lot.price_per_unit
        revenues.append(revenue)
        occupied_counts.append(occupied)
        available_counts.append(available)

    total_revenue = sum(revenues)
    threshold_ratio = 0.05
    grouped_labels = []
    grouped_values = []
    others_value = 0

    for name, value in zip(lot_names, revenues):
        if total_revenue > 0 and value / total_revenue < threshold_ratio:
            others_value += value
        else:
            grouped_labels.append(name)
            grouped_values.append(value)

    if others_value > 0:
        grouped_labels.append("Others")
        grouped_values.append(others_value)

    if all(rev == 0 for rev in grouped_values):
        grouped_values = [1 for _ in grouped_values]

    plt.figure(figsize=(5, 5))
    plt.pie(grouped_values, labels=grouped_labels, autopct='%1.1f%%', startangle=140)
    plt.title("Revenue from each parking lot")
    pie_path = 'static/images/revenue_pie.png'
    plt.savefig(pie_path)
    plt.close()

    plt.figure(figsize=(5, 5))
    x = range(len(lot_names))
    plt.bar(x, occupied_counts, color='red', label='Occupied')
    plt.bar(x, available_counts, bottom=occupied_counts, color='green', label='Available')
    plt.xticks(x, lot_names, rotation=30)
    plt.ylabel("Number of Spots")
    plt.title("Available vs Occupied Spots per Lot")
    plt.legend()
    bar_path = 'static/images/occupancy_bar.png'
    plt.savefig(bar_path)
    plt.close()

    return render_template("summary.html", pie_chart=pie_path, bar_chart=bar_path)

@app.route('/edit_profile', methods=['GET', 'POST'])
def edit_profile():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user = User.query.get(session['user_id'])

    if request.method == 'GET':
        return render_template('edit_profile.html', user=user)
    
    if request.method == 'POST':
        user.full_name = request.form['full_name']
        user.email = request.form['email']
        user.address = request.form['address']
        user.pin_code = request.form['pin_code']
        user.password = request.form['password']

        db.session.commit()
        flash('Profile updated successfully!', 'success')
    


#========================================================================= User Dashboard ====================================================================

@app.route('/user_dashboard', methods=['GET', 'POST'])
def user_dashboard():
    if 'user_id' not in session and session.get('role') != 'user':
        return redirect(url_for('login'))
    
    user_id = session.get('user_id')

    lots = ParkingLot.query.all()
    reservations = Reservation.query.filter_by(user_id=user_id).all()

    return render_template("user_dashboard.html", reservations=reservations, lots=lots)
